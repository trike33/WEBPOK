import requests as r
import sys
import json
from pwn import *
import time
import threading
import traceback
from urllib.parse import urlparse
from multiprocessing import Manager
import asyncio
import aiohttp
import random
from colorama import Fore, Style
from modules.json_format import *
from bs4 import BeautifulSoup
from modules.helper import *

gau_timer_event = False # for gau

#for rec fuzzer
rec_stop_event = threading.Event()
rec_timer_event = threading.Event()
visited_urls = set()
valid_urls = set()

async def fetch_get(session, url, params, semaphore):
    async with semaphore:
        async with session.get(url, params=params) as response:
            return await response.text(), response.status

async def fetch_post(session, url, params, semaphore):
    async with semaphore:
        async with session.post(url, data=params) as response:
            return await response.text(), response.status

async def param_get_bruteforce(url, wordlist, max_req_num, headers, timeout, testvalue):
    semaphore = asyncio.Semaphore(max_req_num)
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for param in wordlist:
            params = {param: testvalue}
            tasks.append(fetch_get(session, url, params, semaphore))
        
        responses = await asyncio.gather(*tasks)
        return responses

async def param_post_bruteforce(url, wordlist, max_req_num, headers, timeout, testvalue):
    semaphore = asyncio.Semaphore(max_req_num)
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for param in wordlist:
            params = {param: testvalue}
            tasks.append(fetch_post(session, url, params, semaphore))
        
        responses = await asyncio.gather(*tasks)
        return responses

def bruteforce_post_params(url, wordlist, max_req_num, headers, timeout, testvalue):
    if len(headers) != 0:
        key, value = header.split(":", 1)
        custom_header[key.strip()] = value.strip()
    else:
        headers = {"User-Agent": "WEBPOK"}

    if len(testvalue) != 0:
        testvalue = testvalue
    else:
        testvalue = "test_value"

    method = "POST"
    calibraton_length = calibraton(url, headers, method)

    print(f"{Fore.MAGENTA}\tBase URL >>> {url}")
    print(f"{Fore.MAGENTA}\tWordlist >>> {wordlist}")
    print(f"{Fore.MAGENTA}\tMaximum paralel requests >>> {max_req_num}")
    print(f"{Fore.MAGENTA}\tHeaders >>> {headers}")
    print(f"{Fore.MAGENTA}\tTimeout >>> {timeout}s")
    print(f"{Fore.MAGENTA}\tTest value >>> {testvalue}")
    print(f"{Fore.MAGENTA}\tMethod >>> {method}")
    print(f"{Fore.MAGENTA}\tCalibration length >>> {calibraton_length}\n")

    with open(wordlist, 'r') as file:
        wordlist = [line.strip() for line in file.readlines()]
    
    start_time = time.time()
    responses = asyncio.run(param_post_bruteforce(url, wordlist, max_req_num, headers, timeout, testvalue))
    end_time = time.time()

    for response, status in responses:
        if len(response) != calibraton_length and status != 404:
            print(f'Status: {status}, Response Length: {len(response)}')
    
    print(f'Time taken: {end_time - start_time} seconds')

    input("Awaiting to return to main menu...")

def bruteforce_get_params(url, wordlist, max_req_num, headers, timeout, testvalue):

    if len(headers) != 0:
        key, value = header.split(":", 1)
        custom_header[key.strip()] = value.strip()
    else:
        headers = {"User-Agent": "WEBPOK"}

    if len(testvalue) != 0:
        testvalue = testvalue
    else:
        testvalue = "test_value"

    method = "GET"
    calibraton_length = calibraton(url, headers, method)

    print(f"{Fore.MAGENTA}\tBase URL >>> {url}")
    print(f"{Fore.MAGENTA}\tWordlist >>> {wordlist}")
    print(f"{Fore.MAGENTA}\tMaximum paralel requests >>> {max_req_num}")
    print(f"{Fore.MAGENTA}\tHeaders >>> {headers}")
    print(f"{Fore.MAGENTA}\tTimeout >>> {timeout}s")
    print(f"{Fore.MAGENTA}\tTest value >>> {testvalue}")
    print(f"{Fore.MAGENTA}\tMethod >>> {method}")
    print(f"{Fore.MAGENTA}\tCalibration length >>> {calibraton_length}\n")

    with open(wordlist, 'r') as file:
        wordlist = [line.strip() for line in file.readlines()]
    
    start_time = time.time()
    responses = asyncio.run(param_get_bruteforce(url, wordlist, max_req_num, headers, timeout, testvalue))
    end_time = time.time()

    for response, status in responses:
        if len(response) != calibraton_length and status != 404:
            print(f'Status: {status}, Response Length: {len(response)}')
    
    print(f'Time taken: {end_time - start_time} seconds')

    input("Awaiting to return to main menu...")

def find_hidden_fields(urls, headers):
    """
    Function used to find hidden fields in HTML source code
    urls: urls to check
    headers: custom headers to use(if any)
    """
    if len(headers) != 0:
        key, value = header.split(":", 1)
        custom_header[key.strip()] = value.strip()
    else:
        headers = {"User-Agent": "WEBPOK"}
    
    for url in urls:
        response = r.get(url, headers=headers, verify=False)
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all hidden input fields
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})

        # Extract name and value attributes
        hidden_params = {input_tag['name']: input_tag['value'] for input_tag in hidden_inputs}

        # Display the hidden parameters
        print("Hidden Parameters; FORMAT >>> param_name: param_value")
        for name, value in hidden_params.items():
            print(f"{name}: {value}")

        input("\nAwaiting to continue to main menu...")

async def second_counter(timer_bar):
    """
    Asynchronous function to count and display elapsed seconds.
    """
    start_time = time.time()
    global rec_timer_event
    while not rec_stop_event.is_set():
        elapsed_seconds = int(time.time() - start_time)
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        timer_bar.status(f"Elapsed time: {hours:02}:{minutes:02}:{seconds:02}")
        await asyncio.sleep(1)
        if rec_timer_event.is_set():
            timer_bar.success()
            return

def match_check(response, match):
    """
    REMEMBER THAT A -1 ON match MEANS TO SKIP THAT PATTERN
    Function used to check matching patterns
    input: response object
    returns: bool; True means a match has been found and False a match hasn't been found
    """
    if match["size"] != -1:
        if response.status == match["status_code"] and response.headers.get("Content-Length") == match["size"]:
            return True
        else:
            return False
    
    if response.status == match["status_code"]:
        return True
    else:
        return False

def filter_check(response, filtering):
    """
    REMEMBER THAT A -1 ON filtering MEANS TO SKIP THAT PATTERN
    Function used to check filtering patterns
    input: response object
    returns: bool; True means a filter has been found and False a filter hasn't been found
    """
    if filtering["size"] != -1:
        if filtering["status_code"] != -1:
            #status and length check
            if response.headers.get("Content-Length") == filtering["size"] and response.status == filtering["status_code"]:
                return True
            else:
                return False
        else:
            #only length check
            if response.headers.get("Content-Length") == filtering["size"]:
                return True
            else:
                return False
    
    if filtering["status_code"] != -1:
        if filtering["size"] != -1:
            #status and length check
            if response.headers.get("Content-Length") == filtering["size"] and response.status == filtering["status_code"]:
                return True
            else:
                return False
        else:
            #only status check
            if response.status == filtering["status_code"]:
                return True
            else:
                return False

async def fetch_url(url, session, semaphore, mydict, visited_urls, valid_urls, q, progress_bar, progress1, match, filtering):
    """
    Asynchronous function to fetch data from a URL
    url: url to fetch
    session: session object used to reuse connections
    semaphore: used to limit the concurrent requests
    mydict: dictionary that we need to update if 200 is found
    visited_urls: set used to avoid visiting the same url twice
    valid_urls: update with full urls
    q: list to update with relative paths if 200 is found
    match: matching patterns
    filtering: filter patterns
    """
    global rec_stop_event
    if rec_stop_event.is_set():
        print("Stop event detected, exiting...")
        return
    if url not in visited_urls:
        visited_urls.add(url)
        async with semaphore:  # Limit concurrent requests
                try:
                    start_time = time.time()
                    async with session.get(url, ssl=False) as response:
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        rps = 1 / elapsed_time
                        progress_bar.status(f"Total Perfomed requests: {progress1} | RPS: {rps:.2f}")
                        #print(f"Fetching {url} - Status: {response.status}")
                        if match_check(response, match) and not filter_check(response, filtering):
                            print(f"{Fore.GREEN}URL: {url} [Status: {response.status} | Size: {response.headers.get('Content-Length')}]")
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
                                mydict[url_path] = -1
                        return
                except asyncio.TimeoutError:
                    print(f"{Fore.RED}Request to {url} timed out!")
                    return
                except Exception as e:
                    print(f"{Fore.RED}An error occurred:")
                    traceback.print_exc()
                    return
    else:
        return


async def run_async_requests(urls, max_req_num, semaphore, mydict, session, q, progress_bar, progress1, match, filtering):
    """
    Function to run the async tasks
    urls: urls to try asyncrhonously
    max_req_num: used to limit asynchoronous requests
    semaphore: used to limit the concurrent requests
    mydict: dictionary that we need to update if 200 is found
    progress_bar: used to keep track of the progess
    session: session object created by each captain
    q: list to update if 200 is found
    match: matching patterns
    filtering: filter patterns
    """
    global visited_urls
    global valid_urls
    global stop_event

    tasks = [fetch_url(url, session, semaphore, mydict, visited_urls, valid_urls, q, progress_bar, progress1, match, filtering) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

async def captain_worker(base_url, lines, extensions, max_req_num, semaphore, timeout, q, progress_bar, captain_num, match, filtering):
    """
    Asynchronous function responsible for organizing the run_async_requests function workload, each captain
    is responsible for its progress bar
    base_url: base_url to construct urls from
    lines: directories to attempt
    extensions: extensions to attempt
    max_req_num: maximum nº of requests per captian
    semaphore: used to limit the concurrent requests
    mydict: dictionary used to keep track of the wordlist indexes
    timeout: timeout used for http requests
    q: list used to keep track of the results
    progress_bar: used to display progress and RPS rate
    captain_num: used for prettier debugging
    match: matching patterns
    filtering: filtering patterns
    """
    global rec_stop_event # we can acess stop_event
    global thread_num # we can access thread_num
    global visited_urls #we can access visited urls
    global headers
    lines_len = len(lines)
    extensions_len = len(extensions)
    timeout = aiohttp.ClientTimeout(total=timeout) # timeout
    mydict = dict()
    mydict["/"] = 0

    try:
        session = aiohttp.ClientSession(headers=headers, timeout=timeout)
    except:
        session = aiohttp.ClientSession(timeout=timeout)

    progress1 = 0
    total_urls = lines_len*extensions_len*len(q)
    
    while not all(value == lines_len for value in mydict.values()):
        await asyncio.sleep(2) #used for throtelling
        previous_q_len = len(q)
        urls_to_try = set()
        if not rec_stop_event.is_set():
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
                    progress1 += 1
                else:
                    continue
            start_time = time.time()
            results = await run_async_requests(urls_to_try, max_req_num, semaphore, mydict, session, q, progress_bar, progress1, match, filtering)
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
            #progress_bar.status(f"Perfomed requests: {progress} | Active Captains: {thread_num} | Max paralel requests: {max_req_num} | RPS: {rps:.2f}")

            #Update indexes
            for key in mydict.keys():
                if mydict.get(key) == lines_len:
                    continue
                else:
                    mydict[key] += max_req_num
        else:
            print(f"{Fore.MAGENTA}Captain worker {captain_num} forcefully exiting")
            await session.close()
            progress_bar.success()
            return
    print(f"{Fore.MAGENTA}Captain worker {captain_num} ended its task, exiting...")
    await session.close()
    progress_bar.success()
    return

def rec_fuzz(base_url, wordlist, extensions, max_req_num, timeout, headers, thread_num, match, filtering):
    #Setting up global vars
    base_url = base_url.rstrip("/")
    if len(headers) != 0:
        key, value = header.split(":", 1)
        custom_header[key.strip()] = value.strip()
    else:
        headers = {"User-Agent": "WEBPOK"}
    tasks = []

    with open(wordlist , 'r') as file:
        lines = file.readlines()

    loop = asyncio.get_event_loop()
    semaphore = asyncio.Semaphore(max_req_num)  # Limit asynchronous requests
    
    # Initialize manager, queue and dictionary
    manager = Manager()
    q = manager.list()
    
    #Always start from the root
    q.append("/") 

    #Split the wordlist lines for each thread
    lines_num = int(len(lines) / thread_num) #type cast to round down
    chunks = [lines[i:i + lines_num] for i in range(0, len(lines), lines_num)]
    index = 0 # index to access chunks
    #print(f"thread_num = {thread_num} ; chunks_items = {len(chunks)} ; lines_num = {lines_num}")
    print(f"{Fore.MAGENTA}\tBase URL >>> {base_url}")
    print(f"{Fore.MAGENTA}\tWordlist >>> {wordlist}")
    print(f"{Fore.MAGENTA}\tCaptains number >>> {thread_num}")
    print(f"{Fore.MAGENTA}\tMax paralel requests >>> {max_req_num}")
    print(f"{Fore.MAGENTA}\tTimeout >>> {timeout}s")
    print(f"{Fore.MAGENTA}\tHeaders >>> {headers}")
    print(f"{Fore.MAGENTA}\tMatcher >>> {match}") 
    print(f"{Fore.MAGENTA}\tFilter >>> {filtering}\n")     
    print(f"{Fore.MAGENTA}All the captain workers started, waiting for the results...")

    # Add the second counter as a background task
    timer_bar = log.progress("Timer")
    timer_task = loop.create_task(second_counter(timer_bar))

    for captain in range(0, thread_num):
        #Distribute the cunks for each captain
        progress_bar = log.progress(f"Captain {captain}")
        #Submit tasks
        captain_num = captain
        lines_for_captain = chunks[index]
        task = loop.create_task(captain_worker(base_url, lines_for_captain, extensions, max_req_num, semaphore, timeout, q, progress_bar, captain_num, match, filtering))
        tasks.append(task)
        index += 1

# Run "captain" tasks concurrently
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        # Ensure the timer task is stopped cleanly after all other tasks
        rec_timer_event.set()  # Signal to stop the timer
        loop.run_until_complete(timer_task)  # Ensure timer task finishes
        loop.close()

    input("Awaiting to return to main menu...")

def gau(host):
    with_subs = False
    progress_bar = log.progress("Collecting URLs...")
    urls = waybackurls(host, with_subs, progress_bar)
    print(f'[+]Found {len(urls)} URLs!')
    parsed_url = urlparse(host)
    output_file = "master.json"
    result = set()
    for url in urls:
        result.add(url[0])
    write_to_json(result, output_file)
    print(f"[+]Results sucessfully saved into master.json!")

def update_progress_bar(progress_bar, start_time):
    global gau_timer_event
    while True:
        if gau_timer_event:
            break
        else:
            elapsed_time = time.time() - start_time
            progress_bar.status(f"Seconds waiting: {elapsed_time}")
            time.sleep(1)  # Update every second

def waybackurls(host, with_subs, progress_bar):
    if with_subs:
        url = 'http://web.archive.org/cdx/search/cdx?url=*.%s/*&output=json&fl=original&collapse=urlkey' % host
    else:
        url = 'http://web.archive.org/cdx/search/cdx?url=%s/*&output=json&fl=original&collapse=urlkey' % host
    
    # Start the progress bar in a separate thread
    start_time = time.time()
    global gau_timer_event
    progress_thread = threading.Thread(target=update_progress_bar, args=(progress_bar, start_time))
    progress_thread.start()
    #print("thread started")
    
    try:
        #print("try entered")
        r = requests.get(url)
        print("[+] urls gathered sucessfully!")
        gau_timer_event = True
        progress_thread.join()
        progress_bar.success()
    except:
        gau_timer_event = True
        progress_thread.join()
        traceback.print_exc()
    results = r.json()
    return results[1:]
