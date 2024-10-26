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

def recursive_parsing(start_url, thread_num, scope, max_depth, skip, header):
	"""
	Step 1: Recursively parse HTML and Javascript files with threads
	Step 2: Validate all the URLs found with threads
	scope: list of url that we must adhere to
	max_depth: maximum depth to recurs at
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
	if len(header) != 0:
		key, value = header.split(":", 1)
		custom_header[key.strip()] = value.strip()

	# Initialize the progress bar
	progress_bar = log.progress("Collecting URLs...")
			
	#Initialize a Thread-safe lock for shared variables
	lock = Lock()
	start_time = time.time()

	with lock:
		for url in start_url:
			print(f"{Fore.CYAN}Processing URL: {url}")
			# Using ThreadPoolExecutor to handle multithreading
			with ThreadPoolExecutor(max_workers=thread_num) as executor:
				while True:
					with open('pidgey_results.txt', 'a') as file:
						for url_to_check in urls_to_check:
							path = urlparse(url_to_check).path
							extension = '.' + path.split('.')[-1] if '.' in path else ''
							if extension in valid_extensions:
								sensitive_urls.add(url_to_check)
							else:
								normal_urls.add(url_to_check)
								file.write(url_to_check+'\n')
					if len(normal_urls) > 10:
						print(f"{Fore.YELLOW}{len(normal_urls)} written to pidgey_results.txt file!")

					with open('pidgey_results_sensitive.txt', 'a') as file:
						for j in sensitive_urls:
							file.write(j + '\n')
					if len(sensitive_urls) > 0:
						print(f"{Fore.YELLOW}{len(sensitive_urls)} URLs written to pidgey_results_sensitive.txt file!")

					if depth == max_depth:
						print(f"{Fore.RED}Maximum depth reached at {depth}")
						break
					temp_urls.clear()
					for i in new_urls:
						temp_urls.add(i)
					new_urls.clear()

					print(f"{Fore.CYAN}Recursing at depth: {depth}")
					if len(temp_urls) != 0:
						for url in temp_urls:
							future_tasks = [executor.submit(link_scraping, url, visited_urls, urls_to_check, new_urls, scope, progress_bar, start_time, custom_header,lock)]
								
						for future in as_completed(future_tasks): #wait until all threads had ended
							result = future.result() #collect results
						if len(new_urls) == 0:
							break
					else:
						future_tasks = [executor.submit(link_scraping, url, visited_urls, urls_to_check, new_urls, scope, progress_bar, start_time, custom_header,lock)]
						for future in as_completed(future_tasks): #wait until all threads had ended
							result = future.result() #collect results
						if len(new_urls) == 0:
							break
					print(f"{Fore.GREEN}Found {len(new_urls)} new URLs at depth: {depth}")
					depth += 1

	progress_bar.success()
	if len(urls_to_check) != 0:
		print(f"{Fore.GREEN}Found {len(urls_to_check)} new URLs to check!")

	if skip == "s":
		return urls_to_check
	
	# Initialize the 2nd progress bar
	progress_bar = log.progress("Checking valid URLs")
	total_urls = len(urls_to_check)
	progress_bar.max = total_urls
	start_time = time.time()

	result = set() # urls to return to main

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
	
	print(f"{Fore.GREEN}Found {len(result)} valid URLs!")	
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
	progress_bar.sucess()
	
	return result








