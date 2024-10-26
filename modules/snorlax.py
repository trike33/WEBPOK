import requests
import re 
import json
from colorama import Fore, Style, init
from urllib.parse import urlparse
import os
from pwn import *
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock	

def priority2(inputfile, thread_num):
    # Shared variables
    valid_urls = []
    result = []
    invalid_codes = [404, 403, 401, 300, 301, 302, 303]
    valid_extensions = {
        '.xls', '.xml', '.xlsx', '.json', '.pdf', '.sql', '.doc', '.docx', '.pptx', '.txt', '.zip', 
        '.tar.gz', '.tgz', '.bak', '.7z', '.rar', '.log', '.cache', '.secret', '.db', '.backup', '.yml',
        '.gz', '.config', '.csv', '.yaml', '.md', '.md5', '.tar', '.xz', '.7zip', '.p12', '.pem', '.key',
        '.crt', '.csr', '.sh', '.pl', '.py', '.java', '.class', '.jar', '.war', '.ear', '.sqlitedb',
        '.sqlite3', '.dbf', '.db3', '.accdb', '.mdb', '.sqlcipher', '.gitignore', '.env', '.ini', '.conf',
        '.properties', '.plist', '.cfg'
    }

    # Thread-safe lock for shared variables
    lock = Lock()

    try:
        # Read the input file
        if inputfile == "master.json":
            with open(inputfile, 'r') as file:
                urls = json.load(file)
        with open(inputfile, 'r') as file:
            urls = file.readlines()
            file.close()
    except:
        print(f"{Fore.RED}Unable to load the provided file!")

    # Initialize the progress bar
    progress_bar = log.progress("Checking valid URLs")
    total_urls = len(urls)
    progress_bar.max = total_urls
    start_time = time.time()

    # Number of threads to use (e.g., 10)
    num_threads = thread_num

    # Function to be executed by each thread
    def process_url(url, idx):
        url = url.strip()  # Clean up URL
        if not url:
            return

        try:
            # Make the request
            response = requests.get(url, verify=False)

            # Check if the response is valid
            if response.status_code not in invalid_codes and "redir" not in response.text.lower():
                with lock:
                    if url not in valid_urls:
                        valid_urls.append(url)

        except requests.exceptions.RequestException as e:
            print(f"URL: {url} | Error: {e}")

        # Update progress bar and RPS after processing each URL
        elapsed_time = time.time() - start_time
        rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
        progress_bar.status(f"Processed {idx + 1}/{total_urls} URLs | RPS: {rps:.2f}")

    # Using ThreadPoolExecutor to handle multithreading
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(process_url, url, idx): idx for idx, url in enumerate(urls)}

        # Wait for all threads to complete
        for future in as_completed(futures):
            try:
                future.result()  # This will raise any exceptions from the thread
            except Exception as exc:
                idx = futures[future]
                print(f"Thread handling URL at index {idx} raised an exception: {exc}")

    # Finish the progress bar
    progress_bar.success()
    print(f"{Fore.RED}Found {len(valid_urls)} valid URLs!")

    # Process valid URLs for file extensions
    for item in valid_urls:
        path = urlparse(item).path
        extension = '.' + path.split('.')[-1] if '.' in path else ''
        if extension in valid_extensions:
            print(f"{Fore.RED}" + item + "\n\n\n\n\n")
            result.append(item)

    with open('snorlax_result.txt','a') as file:
        for i in result:
            file.write(result + '\n')
        file.close()
    print(f"{Fore.GREEN}Priority 2: Results sucessfully saved into {os.getcwd()}/snorlax_result.txt")
    
    # Return the result list to main
    return result

def priority1(inputfile, thread_num):
    keywords = [
    "username", "user", "userid", "user_id", "user_name", "login", "login_id",
    "account", "account_name", "uid", "email", "email_address", "email_id",
    "first_name", "last_name", "full_name", "nickname", "useraccount", "display_name",
    "profile_name", "userlogin", "credentials", "principal", "api_user", "username_field",
    "password", "pass", "passphrase", "passkey", "secret", "secret_key", "auth", "auth_code",
    "authentication", "passwd", "pwd", "password_hash", "password_hashing", "user_password",
    "encrypted_password", "old_password", "new_password", "confirm_password", "retype_password",
    "reset_password", "password_reset", "password_recovery", "password_reset_link",
    "password_reset_token", "login_password", "temporary_password", "recovery_code",
    "api_key", "api_secret", "api_token", "auth_token", "access_token", "api_access_key",
    "bearer_token", "oauth_token", "oauth_key", "session_token", "session_key",
    "client_secret", "client_id", "client_key", "token", "access_key", "api_access",
    "api_credentials", "api_auth", "token_key", "jwt", "jwt_secret", "jwt_token", "api_id",
    "api_user", "api_pass", "api_passcode", "app_key", "app_secret", "user_token",
    "user_secret", "refresh_token", "session_cookie", "access_secret", "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY", "GCP_PROJECT_ID", "GCP_SERVICE_ACCOUNT", "DB_PASSWORD",
    "DB_USERNAME", "DB_HOST", "DB_PORT", "MYSQL_PASSWORD", "POSTGRES_PASSWORD", "REDIS_PASSWORD",
    "DATABASE_URL", "DATABASE_PASS", "DATABASE_USER", "DB_CONFIG", "MONGO_URI", "MONGO_PASS",
    "MONGO_USER", "RDS_PASSWORD", "S3_BUCKET", "S3_SECRET_KEY", "GITHUB_TOKEN", "SLACK_API_TOKEN",
    "API_SECRET_KEY", "ENV_SECRET", "SERVER_KEY", "SSH_KEY", "SSH_PRIVATE_KEY", "SSH_PUBLIC_KEY",
    "PGP_PRIVATE_KEY", "PGP_PUBLIC_KEY", "GOOGLE_CLOUD_KEY", "GITHUB_ACCESS_TOKEN",
    "TWITTER_API_KEY", "TWITTER_API_SECRET", "JWT_SECRET", "OAUTH_CLIENT_SECRET", "OAUTH_CLIENT_ID",
    "config", "configuration", "settings", "config_file", "config_json", "config_yaml", "config_env",
    "settings_file", "secret_config", "secretfile", "credentials_file", "api_credentials", "keyring",
    "keystore", "passwordfile", "keyfile", "backup", "backup_password", "backup_credentials",
    "old_password", "backup_key", "backup_secret", "archived_password", "backup_config",
    "previous_password", "old_config", "recovery_password", "default_password", "default_credentials",
    "backup_auth"
]
    valid_urls = []
    json_urls = []
    result = set()
    invalid_codes = [404, 403, 401]
    lock = Lock()  # To protect shared resources like valid_urls
    
    try:
        # Read the input file
        if inputfile == "master.json":
            with open(inputfile, 'r') as file:
                urls = json.load(file)
                file.close()
        with open(inputfile, 'r') as file:
            urls = file.readlines()
            file.close()
    except:
        print(f"{Fore.RED}Unable to load the provided file!")

    # Initialize the progress bar
    progress_bar = log.progress("Checking valid URLs")
    total_urls = len(urls)
    progress_bar.max = total_urls
    start_time = time.time()

    # Number of threads to use (e.g., 10)
    num_threads = thread_num

    # Function to process URLs in threads
    def check_url(url, idx):
        url = url.strip()
        if not url:
            return

        try:
            response = requests.get(url, verify=False, allow_redirects=True)

            if response.status_code not in invalid_codes:
                with lock:
                    if response.url not in valid_urls:
                        valid_urls.append(response.url)
                
                # Perform additional actions with valid URLs
                """result_comments = search_comments(valid_urls)
                result_keywords = search_keywords(valid_urls, keywords)

                # Check for .json URLs
                for url in valid_urls:
                    path = urlparse(url).path
                    extension = '.' + path.split('.')[-1] if '.' in path else ''
                    if extension == ".json":
                        json_urls.append(url)

                # Search for keywords in JSON URLs
                result_json = search_json(json_urls, keywords)

                #Store the results into result list to return to main
                for i in result_comments:
                    result.append(i)
                for i in result_keywords:
                    result.append(i)
                for i in result_json:
                    result.append(i)"""

        except requests.exceptions.RequestException as e:
            print(f"URL: {url} | Error: {e}")

        # Update the progress bar and RPS calculation
        elapsed_time = time.time() - start_time
        rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
        progress_bar.status(f"Processed {idx + 1}/{total_urls} URLs | RPS: {rps:.2f}")

    # Using ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(check_url, url, idx): idx for idx, url in enumerate(urls)}

        # Process results as threads complete
        for future in as_completed(futures):
            try:
                future.result()  # Will raise an exception if the thread encountered one
            except Exception as exc:
                idx = futures[future]
                print(f"Thread handling URL at index {idx} raised an exception: {exc}")

    # Finish the progress bar
    progress_bar.success()
    print(f"{Fore.GREEN}Found {len(valid_urls)} live URLs!")

    # Perform additional actions with valid URLs
    
    result_comments = search_comments(valid_urls, keywords)
    result_keywords = search_keywords(valid_urls, keywords)

    # Check for .json URLs
    for url in valid_urls:
        path = urlparse(url).path
        extension = '.' + path.split('.')[-1] if '.' in path else ''
        if extension == ".json":
            json_urls.append(url)

    # Search for keywords in JSON URLs
    result_json = search_json(json_urls, keywords)
    for i in result_comments:
    	result.append(i)
    for i in result_keywords:
    	result.append(i)
    for i in result_json:
    	result.append(i)
    print(f"{Fore.GREEN}Priority 1: Results sucessfully saved into {os.getcwd()}/snorlax_result.txt file!")


    return result
def search_comments(urls, keywords):
    result = []
    progress_bar = log.progress("Checking comments in URLs")
    total_urls = len(urls)
    progress_bar.max = total_urls
    start_time = time.time()

    for idx,url in enumerate(urls):
        path = urlparse(url).path
        extension = '.' + path.split('.')[-1] if '.' in path else ''
        response = requests.get(url, verify=False)
		
		#update progress bar
        progress_bar.status(idx + 1)  # idx starts from 0, so add 1 to it
        elapsed_time = time.time() - start_time
        rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
        progress_bar.status(f"Made {idx + 1}/{total_urls} requests | RPS: {rps:.2f}")

        if "html" in response.headers["Content-Type"].lower() or extension == '.html':
            search_pattern = re.compile(r'<!--[\s\S]*?-->', re.MULTILINE)
            matches = search_pattern.findall(response.text)
            if matches:
                for match in matches:
                    if any(keyword in match for keyword in keywords):  # Ensure this line is indented correctly
                        #print(f"{Fore.GREEN}HTML Comment: {match.strip()} in URL: {url}")
                        with open('snorlax_result.txt', 'a') as file:
                            file.write(match + "\n")
                        result.add(url)  # This should be aligned with the print statement	
        if "javascript" in response.headers["Content-Type"].lower() or extension == '.js':
            search_pattern = re.compile(r'//.*?$|/\*[\s\S]*?\*/', re.MULTILINE)
            matches = search_pattern.findall(response.text)
            if matches:
                for match in matches:
                    if any(keyword in match for keyword in keywords):
                    #print(f"{Fore.GREEN}JavaScript Comment: {match.strip()} in URL: {url}")
                        with open('snorlax_result.txt', 'a') as file:
                            file.write(match + "\n")		
                        result.add(url)	
	#finish the progress bar
    progress_bar.success()
    print(f"{Fore.GREEN}Found {len(result)} HTML/javascript comments in live URLs")
    return result

def search_keywords(urls, keywords):
    result = []
    progress_bar = log.progress("Checking keywords in URLs")
    total_urls = len(urls)
    progress_bar.max = total_urls
    start_time = time.time()

    for idx,url in enumerate(urls):
        response = requests.get(url, verify=False)

		#update progress bar
        progress_bar.status(idx + 1)  # idx starts from 0, so add 1 to it
        elapsed_time = time.time() - start_time
        rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
        progress_bar.status(f"Made {idx + 1}/{total_urls} requests | RPS: {rps:.2f}")

        search_pattern = re.compile(r'(' + '|'.join(keywords) + r')[:\s]*([A-Za-z0-9_\-]+)', re.IGNORECASE)
        matches = search_pattern.findall(response.text)
        if matches:
            for match in matches:
                if match[0].strip() != match[1].strip():
                    if len(match[0].strip()) > 10: 
					   #print(f"{Fore.GREEN}Found: keyword: {match[0].strip()}, Value: {match[1].strip()} in URL: {url}")
                        with open('snorlax_result.txt', 'a') as file:
                            file.write("Found: keyword: "+match[0].strip()+", Value: "+match[1].strip()+" in URL: "+url+"\n")
                        result.add(url)

	#finish the progress bar
    progress_bar.success()
    print(f"{Fore.GREEN}Found {len(result)} keywords in live URLs")
    return result				

def search_json(urls, keywords):
    result = []
    progress_bar = log.progress("Checking keywords in URLs")
    total_urls = len(urls)
    progress_bar.max = total_urls
    start_time = time.time()

    for idx,url in enumerate(urls):
        response = requests.get(url, verify=False)

		#update progress bar
        progress_bar.status(idx + 1)  # idx starts from 0, so add 1 to it
        elapsed_time = time.time() - start_time
        rps = (idx + 1) / elapsed_time if elapsed_time > 0 else 0
        progress_bar.status(f"Made {idx + 1}/{total_urls} requests | RPS: {rps:.2f}")
        json_data = json.loads(response.text)
        for key in json_data:
            if key in keywords:
				#print(f"{Fore.GREEN}JSON Match found! Key: '{key}' | Value: '{data[key]}' on URL: {url}")
                with open('snorlax_result.txt', 'a') as file:
                    file.write(match + "\n")
                result.add(url)
	#finish the progress bar
    progress_bar.success()
    print(f"{Fore.GREEN}Found {len(result)} keywords JSON files")
    return result
	

"""
def writejson(unique_urls):
	#process the urls sequentially, no threading
	parsed_urls = process_urls(unique_urls)

	#write the results to a json file
	write_to_json(parsed_urls, 'master.json')
	print(f"{Fore.GREEN}Results sucessfully written to {os.getcwd()}/musiglof_results.json")
	"""