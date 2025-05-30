import requests
import time
from urllib.parse import urlparse, urljoin, urlunparse
import re
import traceback

def scope_check(scope, parsed_url):
	"""
	Function that checks if a url is in scope or not
	scope: set that contains the scope
	parsed_url: url previously parsed with urlparse()
	"""
	#scope check
	for i in scope:
		scope_url = urlparse(i)
		if len(scope_url.path) < 1: # no path
			if parsed_url.scheme+"://"+parsed_url.netloc not in scope:
				return False
			else:
				return True
		else:
			if any(parsed_url.netloc in netloc for netloc in scope):
				if parsed_url.path.count("/") < scope_url.path.count("/"):
					return False
				else:
					return True
			else:
				return False

def validate_urls(result, url, idx, progress_bar, start_time, total_urls, lock):
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
	with lock:
		try:
    		# Make the request
			response = requests.get(url=url, verify=False, allow_redirects=True)
			if response.status_code == 200:
				result.add(response.url)

		except requests.exceptions.RequestException as e:
			print(f"URL: {url} | Error: {e}")

		# Update progress bar and RPS after processing each URL
		elapsed_time = time.time() - start_time
		rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
		progress_bar.status(f"Processed {idx + 1}/{total_urls} URLs | RPS: {rps:.2f}")

#Global counters for link_scraping
total_requests = 0
new_urls_count = 0

async def link_scraping(url, visited_urls, urls_to_check, new_urls, scope, progress_bar, session, semaphore):
	"""
	Gathers links from HTML files
	url_packs: url packs that we must make concurrently
	visited_urls: set used to avoid infinite loops
	urls_to_check: set used to keep track of the all the new unique urls(all depths)
	new_urls: set used to keep track of the newly discovered URLs at this depth(only our current depth)
	scope: set or string used to keep the tool in scope
	progress_bar: used to update the progress bar
	session: aiohttp session
	semaphore used to limit http requests
	"""
	global total_requests, new_urls_count

	if url in visited_urls:
		return

	visited_urls.add(url)
	parsed_url = urlparse(url)

	#scope check
	if scope_check(scope, parsed_url):
		async with semaphore:
			try:
				start_time = time.time()
				async with session.get(url, ssl=False) as response:
					content_type = response.headers.get('Content-Type', '')
					
					#ensure we only parse html or js files
					if "html" or "javascript" in content_type:
						try:
							content = await response.text()
						except:
							await response.read()
							return
					else:
						return

					elapsed_time = time.time() - start_time
					if elapsed_time > 0:
						rps = 1 / elapsed_time
					else:
						rps = 0

					# 1. Full URL regex pattern
					full_url_pattern = r'https?://[^\s"\'<>]+'
					match1 = re.findall(full_url_pattern, content)

					# 2. Relative URL regex pattern
					relative_url_pattern = r'(?:href|src|action|data-[\w-]+)\s*=\s*["\']((?:\./|\../|/)[^"\'>?#]*)["\']'
					match2 = re.findall(relative_url_pattern, content)

					# 3, HTML attributes regex pattern
					pattern = r'\b(?:href|src-\w+)="([^"]*)"'
					match3 = re.findall(pattern, content)

					# 3. Concatenated URL regex pattern (within JavaScript)
					#concat_url_pattern = r'["\'](https?://|/)[^"\']*["\']\s*\+\s*["\'][^"\']*["\']'
					#match3 = re.findall(concat_url_pattern, response.text)

					if match1:
						#Full URLs
						for match in match1:
							parsed_match = urlparse(match)
							if scope_check(scope, parsed_match):
								urls_to_check.add(match)
								new_urls.add(match)
								new_urls_count += 1

					if match2:
						#Relative URLs
						for match in match2:
							parsed_url = urlparse(url)
							if parsed_url.path[0] != "/":
								full_url = parsed_url.scheme+"://"+parsed_url.netloc+parsed_url.path+"/"+match
							else:
								full_url = parsed_url.scheme+"://"+parsed_url.netloc+parsed_url.path+match
							parsed_full_url = urlparse(full_url)
							if scope_check(scope, parsed_full_url):
								urls_to_check.add(full_url)
								new_urls.add(full_url)
								new_urls_count += 1

					if match3:
						#HTML attributes URL
						for link in match3:
							if len(link) != 0:
								if 'http' not in link: #relative path
									if link[0] != "/":
										full_link = url+'/'+link
									else:
										full_link = url+link
									new_urls.add(full_link)
									urls_to_check.add(full_link)
								else: # full path
									new_urls.add(link)
									urls_to_check.add(link)
							else:
								continue
						

					#Update the progress bar
					total_requests += 1  # Increment total requests

					progress_bar.status(f"Processed Requests: {total_requests} | New URLs found: {len(urls_to_check)} | RPS: {rps:.2f}")

			except Exception as e:
				print(f"Error processing {url}: {e}")
				#traceback.print_exc()
	else:
		return
