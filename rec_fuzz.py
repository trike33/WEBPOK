#!/usr/bin/python3

import time
from pwn import *
from multiprocessing import Manager
import traceback
import asyncio
import aiohttp
from urllib.parse import urlparse
import random

# Function to handle the signal
def signal_handler(sig, frame):
	global stop_event #now we can change the stop_event value
	#global futures
	global thread_num
	print("stop_event caught!")
	print(f"attempting to cancel {thread_num} captain workers")
	stop_event.set()
	return

"""
def queque_worker(q):
	Function used to check if the queque length has changed
	q: queque
	size_lock: lock used to check the size without blocking
	mod_lock: lock used to modify the queue safely
	global stop_event # ensure that it can exit on signal
	print("Queque thread started sucessfully!")
	time.sleep(3)
	previous_length = len(q)

	while not stop_event:
		time.sleep(1)
		current_length = len(q)
		#print(3)	
		if current_length != previous_length:
			print(f"Queue size changed: {previous_length} -> {current_length}")
			previous_length = len(q)
			q.append(True)
		else:
			continue
	return
"""
async def fetch_url(url, session, semaphore, mydict, visited_urls, valid_urls, q):
	"""
	Asynchronous function to fetch data from a URL
	url: url to fetch
	session: session object used to reuse connections
	semaphore: used to limit the concurrent requests
	mydict: dictionary that we need to update if 200 is found
	visited_urls: set used to avoid visiting the same url twice
	valid_urls: update with full urls
	q: list to update with relative paths if 200 is found
	"""
	if url not in visited_urls:
		visited_urls.add(url)
		async with semaphore:  # Limit concurrent requests
				try:
					async with session.get(url, ssl=False) as response:
						#print(f"Fetching {url} - Status: {response.status}")
						if response.status == 200:
							print(f"Valid url: {url}")
							parsed_url = urlparse(url)
							#check to ensure we only store directories into the queue
							if '/' not in parsed_url.path[-1]: 
								if '.' not in parsed_url.path[-4] or '.' not in parsed_url.path[-5]:
									url_path = f"{parsed_url.path}/"
									valid_urls.add(url)
								else:
									valid_urls.add(url)
							if url_path not in q:
								q.append(url_path)
								mydict[url_path] = 0
						return
				finally:
					return
	else:
		return


async def run_async_requests(urls, max_req_num, semaphore, mydict, session, q):
	"""
	Function to run the async tasks
	urls: urls to try asyncrhonously
	max_req_num: used to limit asynchoronous requests
	semaphore: used to limit the concurrent requests
	mydict: dictionary that we need to update if 200 is found
	progress_bar: used to keep track of the progess
	session: session object created by each captain
	q: list to update if 200 is found
	"""
	global visited_urls
	global valid_urls

	tasks = [fetch_url(url, session, semaphore, mydict, visited_urls, valid_urls, q) for url in urls]
	results = await asyncio.gather(*tasks)
	return results


async def captain_worker(base_url, lines, extensions, max_req_num, semaphore, mydict, q, progress_bar, captain_num):
	"""
	Asynchronous function responsible for organizing the run_async_requests function workload, each captain
	is responsible for its progress bar
	base_url: base_url to construct urls from
	lines: directories to attempt
	extensions: extensions to attempt
	max_req_num: maximum nº of requests per captian
	semaphore: used to limit the concurrent requests
	mydict: dictionary used to keep track of the wordlist indexes
	q: list used to keep track of the results
	progress_bar: used to display progress and RPS rate
	captain_num: used for prettier debugging
	"""
	global stop_event # we can acess stop_event
	global thread_num # we can access thread_num
	global visited_urls #we can access visited urls
	global headers
	lines_len = len(lines)
	extensions_len = len(extensions)

	try:
		session = aiohttp.ClientSession(headers=headers)
	except:
		session = aiohttp.ClientSession()

	progress = 0
	total_urls = lines_len*extensions_len*len(q)
	
	while not all(value == lines_len for value in mydict.values()):
		#await asyncio.sleep(1) #used for throtelling
		previous_q_len = len(q)
		urls_to_try = set()
		if not stop_event.is_set():
			#Running the requests
			for j in q:
				for key in mydict.keys():
					index = mydict.get(key)
					try: #encapsulated into a try-except because we may get to the bottom of the wordlist
						for i in range(max_req_num):
							line = lines[index+i]
							line = line.rstrip()

							if '#' in line or len(line) == 0:
								urls_to_try.add(f"{base_url}{j}{random.randint(0,1000000)}")
							else:
								#Directories
								url = f"{base_url}{j}{line}"
								urls_to_try.add(url)
								for l in extensions:
									#files
									url = f"{base_url}{j}{line}{l}"
									urls_to_try.add(url)
					except:
						continue

			total_requests = 0
			for url in urls_to_try:
				if url not in visited_urls:
					total_requests += 1
					progress += 1
				else:
					continue

			start_time = time.time()
			results = await run_async_requests(urls_to_try, max_req_num, semaphore, mydict, session, q)
			end_time = time.time()
			elapsed_time = end_time - start_time
			if elapsed_time > 0 and total_requests > 0:
				rps = elapsed_time / total_requests
			else:
				rps = 0
			#progress += len(urls_to_try)
			current_q_len = len(q)
			if previous_q_len != current_q_len:
				difference = current_q_len - previous_q_len
				total_urls += difference*lines_len*extensions_len
			progress_bar.status(f"Perfomed requests: {progress} | Active Captains: {thread_num} | Max paralel requests: {max_req_num} | RPS: {rps:.2f}")

			#Update indexes
			for key in mydict.keys():
				if mydict.get(key) == lines_len:
					continue
				else:
					mydict[key] += 1
		else:
			print(f"Captain worker {captain_num} forcefully exiting")
			await session.close()
			progress_bar.success()
			return
	print(f"Captain worker {captain_num} ended its task, exiting...")
	await session.close()
	progress_bar.success()
	return

if __name__ == '__main__':
	#Global variables
	url = 'http://10.10.11.38:5000' #do not add the final / at the end, it matters!
	#/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
	wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
	#headers = {"Cookie": "Session=12345"}
	extensions = {'.php', '.txt'}
	stop_event = threading.Event()
	thread_num = 3
	max_req_num = 3
	visited_urls = set()
	valid_urls = set()
	signal.signal(signal.SIGINT, signal_handler) #Registering the signal handler
	tasks = []

	with open(wordlist , 'r') as file:
		lines = file.readlines()

	loop = asyncio.get_event_loop()
	semaphore = asyncio.Semaphore(max_req_num)  # Limit asynchronous requests
	
	# Initialize manager, queue and dictionary
	manager = Manager()
	q = manager.list()
	mydict = manager.dict()
	q.append("/")
	mydict["/"] = 0

	#Split the wordlist lines for each thread
	lines_num = int(len(lines) / thread_num) #type cast to round down
	chunks = [lines[i:i + lines_num] for i in range(0, len(lines), lines_num)]
	index = 0 # index to access chunks
	#print(f"thread_num = {thread_num} ; chunks_items = {len(chunks)} ; lines_num = {lines_num}")
	print("All the captain workers started, waiting for the results...")

	for captain in range(0, thread_num):
		#Distribute the cunks for each captain
		progress_bar = log.progress(f"Captain {captain}")
		#Submit tasks
		captain_num = captain
		lines_for_captain = chunks[index]
		task = loop.create_task(captain_worker(url, lines_for_captain, extensions, max_req_num, semaphore, mydict, q, progress_bar, captain_num))
		tasks.append(task)
		index += 1
	loop.run_until_complete(asyncio.gather(*tasks))