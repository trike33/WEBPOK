import requests
import re
from colorama import Fore, Style
from urllib.parse import urljoin
from modules.threads import *
from threading import Lock
from pwn import *
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
import asyncio
import aiohttp

pidgey_timer_event = threading.Event() #event to stop the timer

async def second_counter(timer_bar):
	"""
	Asynchronous function to count and display elapsed seconds.
	"""
	start_time = time.time()
	global pidgey_timer_event
	while True:
		elapsed_seconds = int(time.time() - start_time)
		hours = elapsed_seconds // 3600
		minutes = (elapsed_seconds % 3600) // 60
		seconds = elapsed_seconds % 60
		timer_bar.status(f"Elapsed time: {hours:02}:{minutes:02}:{seconds:02}")
		await asyncio.sleep(1)
		if pidgey_timer_event.is_set():
			timer_bar.success()
			return


async def recursive_parsing(start_url, scope, max_depth, skip, header, timeout, max_req_num):
	"""
	Step 1: Recursively parse HTML and Javascript files with threads
	Step 2: Validate all the URLs found with threads
	start_url: url to start from
	scope: list of url that we must adhere to
	max_depth: maximum depth to recurs at
	skip: instructs if the program must skip url validation
	header: custom header
	timeout: custom timeout value
	max_req_num: used to throttle asynchrhonous tasks
	"""
	#Global vars
	urls_to_check = set() # urls to check to be alive
	visited_urls = set() #set to avoid visiting the same page twice
	new_urls = set() # set used to know when to exit the thread pool
	temp_urls = set()
	depth = 0 # used to keep track of the depth processed
	valid_extensions = {
        '.xls', '.xml', '.xlsx', '.json', '.pdf', '.sql', '.doc', '.docx', '.pptx', '.txt', '.zip', 
        '.tar.gz', '.tgz', '.bak', '.7z', '.rar', '.log', '.cache', '.secret', '.db', '.backup', '.yml',
        '.gz', '.config', '.csv', '.yaml', '.md', '.md5', '.tar', '.xz', '.7zip', '.p12', '.pem', '.key',
        '.crt', '.csr', '.sh', '.pl', '.py', '.java', '.class', '.jar', '.war', '.ear', '.sqlitedb',
        '.sqlite3', '.dbf', '.db3', '.accdb', '.mdb', '.sqlcipher', '.gitignore', '.env', '.ini', '.conf',
        '.properties', '.plist', '.cfg'
    }
	sensitive_urls = set()
	normal_urls = set()
	custom_header = {}
	written_urls = set()
	if len(header) != 0:
		key, value = header.split(":", 1)
		custom_header[key.strip()] = value.strip()

	timeout = aiohttp.ClientTimeout(total=timeout) # timeout
	semaphore = asyncio.Semaphore(max_req_num)  # Limit asynchronous requests
	try:
		session = aiohttp.ClientSession(headers=headers, timeout=timeout)
	except:
		session = aiohttp.ClientSession(timeout=timeout)

	# Initialize the progress bar
	progress_bar = log.progress("Collecting URLs...")

	for url in start_url:
		print(f"{Fore.YELLOW}Processing URL: {url}")
		while True:
			await asyncio.sleep(2) #used for throtelling

			temp_urls.clear()
			for i in new_urls:
				temp_urls.add(i)
			new_urls.clear()

			sensitive_urls.clear()
			normal_urls.clear()

			#write results to pidgey file
			with open('pidgey_results.txt', 'a') as file:
				for url_to_check in urls_to_check:
					if url_to_check not in written_urls:
						path = urlparse(url_to_check).path
						extension = '.' + path.split('.')[-1] if '.' in path else ''
						if extension in valid_extensions:
							sensitive_urls.add(url_to_check)
							written_urls.add(url_to_check)
						else:
							normal_urls.add(url_to_check)
							written_urls.add(url_to_check)
							file.write(url_to_check+'\n')
					else:
						continue

			if len(normal_urls) > 0:
				print(f"{Fore.YELLOW}{len(normal_urls)} written to pidgey_results.txt file!")

			#Write sensitive results to pidgey file
			with open('pidgey_results_sensitive.txt', 'a') as file:
				for j in sensitive_urls:
					file.write(j + '\n')
			if len(sensitive_urls) > 0:
				print(f"{Fore.YELLOW}{len(sensitive_urls)} URLs written to pidgey_results_sensitive.txt file!")

			if depth == max_depth:
				print(f"{Fore.RED}Maximum depth reached at {depth}")
				break

			print(f"{Fore.CYAN}Recursing at depth: {depth}")
			if len(temp_urls) != 0:
				for url in temp_urls:
					await link_scraping(url, visited_urls, urls_to_check, new_urls, scope, progress_bar, session, semaphore)

				if len(new_urls) == 0:
					break
			else:
				await link_scraping(url, visited_urls, urls_to_check, new_urls, scope, progress_bar, session, semaphore)

				if len(new_urls) == 0:
					break

			print(f"{Fore.GREEN}Found {len(new_urls)} new URLs at depth: {depth}")
			depth += 1

	progress_bar.success()

	if len(urls_to_check) != 0:
		print(f"{Fore.GREEN}Found {len(urls_to_check)} new URLs to check!")

	if skip == "s":
		await session.close()
		return urls_to_check

	# Initialize the 2nd progress bar
	progress_bar = log.progress("Checking valid URLs")
	total_urls = len(urls_to_check)
	progress_bar.max = total_urls

	result = set() # urls to return to main

	for idx, url in enumerate(urls_to_check):
		await validate_urls_async(result, url, idx, progress_bar, total_urls, session, semaphore)
	
	print(f"{Fore.GREEN}Found {len(result)} valid URLs!")
	await session.close()
	progress_bar.success()
	return result

async def validate_urls_async(result, url, idx, progress_bar, total_urls, session, semaphore):
	"""
	Checks if a URL answers back with a 200 and it appends it to result set
	Input:
		result: the result set to update wheter a valid url is found or not
		url: the url that the thread must process
		idx: counter to update the progress bar and update the RPS rate
		progress_bar: the progress_bar object that each thread must update upon its end
		start_time: the time when the progress bar was initialized
		lock: variable used to keep a safe thread environment
		total_urls: the total urls requests to be made
	"""
	async with semaphore:
		await asyncio.sleep(2) #used for throtelling 
		try:
			start_time = time.time()
			async with session.get(url, ssl=False) as response:
				if response.status  == 200:
					result.add(response.url)

		except requests.exceptions.RequestException as e:
			print(f"URL: {url} | Error: {e}")

		# Update progress bar and RPS after processing each URL
		elapsed_time = time.time() - start_time
		rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
		progress_bar.status(f"Processed {idx + 1}/{total_urls} URLs | RPS: {rps:.2f}")

def pidgey_recurse(start_url, scope, max_depth, header, timeout, max_req_num, skip):
	"""
	Step 1: Recursively parse HTML and Javascript files with threads
	Step 2: Validate all the URLs found with threads
	start_url: list of base url to crawl
	scope: scope that we must adhere to
	max_depth: max_depth that we must reach
	header: custom headers if any
	timeout: timeout
	max_req_num: maximum paralalel requests
	skip: used to skip URL validation or not
	"""
	global pidgey_timer_event
	if skip == "s":
		url_validation_check = True
	else:
		url_validation_check = False

	tasks = []
	print(f"{Fore.CYAN}\tStart URL/s >>> {start_url}")
	print(f"{Fore.CYAN}\tScope >>> {scope}")
	print(f"{Fore.CYAN}\tMax depth >>> {max_depth}")
	print(f"{Fore.CYAN}\tHeader >>> {header}")
	print(f"{Fore.CYAN}\tTimeout >>> {timeout}")
	print(f"{Fore.CYAN}\tMaximum paralel requests >>> {max_req_num}")
	print(f"{Fore.CYAN}\tValidate found URLs >>> {url_validation_check}")

	loop = asyncio.get_event_loop()
	task = loop.create_task(recursive_parsing(start_url, scope, max_depth, skip, header, timeout, max_req_num))
	tasks.append(task)

	timer_bar = log.progress("Timer")
	timer_task = loop.create_task(second_counter(timer_bar))

	try:
		result = loop.run_until_complete(asyncio.gather(*tasks))
	finally:
		# Ensure the timer task is stopped cleanly after all other tasks
		pidgey_timer_event.set()  # Signal to stop the timer
		loop.run_until_complete(timer_task)  # Ensure timer task finishes
		loop.close()
		print("Crawler ended!")
		return result

def parse_robots_url(url, thread_num, result):
	"""
	Parses the given robots/sitemap URL
	can only parse one URL at a time
	"""
	urls_to_check = set()
	additional_sitemaps = set()
	response = requests.get(url=url, verify=False)
	parsed_url = urlparse(response.url)
	if response.status_code != 200:
		return result
	if 'text' in response.headers['Content-Type']:
		#We encountered a robots.txt file
		lines = response.text.splitlines()
		for line in lines:
			line = line.strip()
			if line.startswith('Allow:'):
				allow_path = f"{parsed_url.scheme}://{parsed_url.netloc}/{line[len('Allow:'):].strip()}"
				urls_to_check.add(allow_path)
			if line.startswith('Disallow:'):
				disallow_path = f"{parsed_url.scheme}://{parsed_url.netloc}/{line[len('Disallow:'):].strip()}"
				urls_to_check.add(disallow_path)
			if line.startswith('Sitemap:'):
				sitemap_path = line[len('Sitemap:'):].strip()
				additional_sitemaps.add(sitemap_path)

	if 'xml' in response.headers['Content-Type']:
		#We encountered a sitemap.xml file
		root = ET.fromstring(response.content)
		# Check if the sitemap contains other sitemaps (<sitemapindex>)
		for sitemap in root.findall('.//{*}sitemap'):
			loc = sitemap.find('{*}loc')
			if loc is not None:
				child_sitemap_url = loc.text.strip()
            	# Recursively parse the child sitemaps
				additional_sitemaps.add(child_sitemap_url)

    	# Collect URLs from <urlset> section
		for url in root.findall('.//{*}url'):
			loc = url.find('{*}loc')
			if loc is not None:
				url_loc = loc.text.strip()
				urls_to_check.add(url_loc)

	#URLs and sitemaps collected, now validate them
	print(f"{Fore.GREEN}Found {len(urls_to_check)} URLs to check and {len(additional_sitemaps)} additional_sitemaps")
	if len(additional_sitemaps) > 0:
		for sitemap in additional_sitemaps:
			parse_robots_url(sitemap, thread_num, result)
		additional_sitemaps.clear()
			
	# Initialize the progress bar
	progress_bar = log.progress("Checking valid URLs")
	total_urls = len(urls_to_check)
	progress_bar.max = total_urls
	start_time = time.time()
			
	#Initialize a Thread-safe lock for shared variables
	lock = Lock()

	# Using ThreadPoolExecutor to handle multithreading
	with ThreadPoolExecutor(max_workers=thread_num) as executor:
		futures = {executor.submit(validate_urls, result, url, idx, progress_bar, start_time, total_urls, lock): idx for idx, url in enumerate(urls_to_check)}
			# Wait for all threads to complete
		for future in as_completed(futures):
			try:
				future.result()  # This will raise any exceptions from the thread
			except Exception as exc:
				idx = futures[future]
				print(f"Thread handling URL at index {idx} raised an exception: {exc}")
	progress_bar.success()
	
	return result








