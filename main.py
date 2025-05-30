#!/usr/bin/python3

import requests
import re 
import sys
import urllib3
from urllib.parse import urlparse
import json
from colorama import Fore, Style, init, Back
from modules.snorlax import *
from modules.json_format import *
import traceback
from modules.pidgey import *
import os
from modules.hawlucha import *
from modules.treecko import *
from modules.gengar import *
from modules.helper import *

def goback(count):
	count = count + 1
	return count

# Function to handle the signal
def signal_handler(sig, frame):
    banner = (f"""{Fore.RED}

████████╗ ██████╗  ██████╗ ██╗         ███████╗ █████╗ ██╗███╗   ██╗████████╗███████╗██████╗ 
╚══██╔══╝██╔═══██╗██╔═══██╗██║         ██╔════╝██╔══██╗██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
   ██║   ██║   ██║██║   ██║██║         █████╗  ███████║██║██╔██╗ ██║   ██║   █████╗  ██║  ██║
   ██║   ██║   ██║██║   ██║██║         ██╔══╝  ██╔══██║██║██║╚██╗██║   ██║   ██╔══╝  ██║  ██║
   ██║   ╚██████╔╝╚██████╔╝███████╗    ██║     ██║  ██║██║██║ ╚████║   ██║   ███████╗██████╔╝
   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═════╝ 
                                                                                             
{Fore.WHITE}Returning to pokeball...
""")
    print(banner)
    # Here you could also perform any necessary cleanup
    rec_stop_event.set() # for the threads or async tasks
    rec_timer_event.set()
    sys.exit(0)

def clear_screen():
	"""Helper function used to clear the screen"""
	os.system("clear") #change it to: "cls" if you are on windows

if __name__ == '__main__':
	#Registering the signal handler
	signal.signal(signal.SIGINT, signal_handler)
	stop_event = False
	init(autoreset=True) #initialize colorama colors
	unique_urls = set()  # Use a set to store unique URLs across scans
	scope_urls = set() # set used to track the target scope(if provided)
	count = 0 #variable used to only ask things the first time
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #disable unsecure HTTPS warning
	while True:
		clear_screen()
		banner = (f"""

{Fore.RED}██╗    ██╗███████╗██████╗ {Fore.WHITE}██████╗  ██████╗ ██╗  ██╗
{Fore.RED}██║    ██║██╔════╝██╔══██╗{Fore.WHITE}██╔══██╗██╔═══██╗██║ ██╔╝
{Fore.RED}██║ █╗ ██║█████╗  ██████╔╝{Fore.WHITE}██████╔╝██║   ██║█████╔╝ 
{Fore.RED}██║███╗██║██╔══╝  ██╔══██╗{Fore.WHITE}██╔═══╝ ██║   ██║██╔═██╗ 
{Fore.RED}╚███╔███╔╝███████╗██████╔╝{Fore.WHITE}██║     ╚██████╔╝██║  ██╗
{Fore.RED} ╚══╝╚══╝ ╚══════╝╚═════╝ {Fore.WHITE}╚═╝      ╚═════╝ ╚═╝  ╚═╝
                                                   

{Fore.YELLOW}  Web Discovery & Analysis Tool for Efficient Site Discovery
{Fore.GREEN}  By: Joan Fontbona Ardanaz | Priority-based Web Exploration | Version 1.0 | Development"""
		)
		print(banner)
		if count == 0:
			if os.path.exists('master.json'):
				print(f"{Fore.RED}A master.json file has been already found")
				choice = input("Press d to delete it or enter to continue: ")
				if choice == "d":
					os.remove('master.json')
				else:
					count = goback(count)
		print(f"{Fore.RED}\n┌" + "─" * 91 + "┐")
		print(f"{Style.BRIGHT}| "+"1. Search info disclosures from a file containing URLs"+" "*(90-54)+"|")
		print(f"{Style.BRIGHT}| "+"2. Enter web surface discovery mode"+" "*(90-35)+"|")
		print(f"{Style.BRIGHT}| "+"3. Enter hidden web discovery mode"+" "*(90-34)+"|")
		print(f"{Style.BRIGHT}| "+"4. Print the tree view of the target/targets URL(usefull for small sites)"+" "*(90-73)+"|")
		print(f"{Style.BRIGHT}| "+"5. Save the results into master.json"+" "*(90-36)+"|")
		print(f"{Style.BRIGHT}| "+"6. Check for uniqueness in the master.json file(useful when master.json is not empty)"+" "*(90-85)+"|")
		print(f"{Style.BRIGHT}| "+"7. Smartly view the results"+" "*(90-27)+"|")
		print(f"{Style.BRIGHT}| "+"8. Exit"+" "*(90-7)+"|")
		print(f"{Fore.RED}└" + "─" * 91 + "┘"+"\n")
		if len(unique_urls) != 0:
			print(f"{Fore.GREEN}Results sucessfully saved!")
		if count <= 1:
			thread_num = input("Please enter the number of thread you would like to use(default 1, max 100): ")
			if not thread_num:
				thread_num = 1
			try:
				thread_num = int(thread_num)
				if thread_num < 100:
					thread_num = thread_num
					count = goback(count)
				else:
					print(f"{Fore.RED}Please enter a valid thread number!")
					continue
			except ValueError:
				print(f"{Fore.RED}Invalid input, please enter an integrer!")
				continue
		main_choice = input("Please enter the mode you would like(1,2,3,4,5,6,7,8): ")
		if not main_choice:
			print(f"{Fore.RED}A valid option must be provided!")
			sys.exit(1)

		if len(scope_urls) == 0:
			input1 = input("Please enter the file or URL containing the target/targets scope(s to skip): ")
			if input1.lower() == "s":
				print(f"{Fore.YELLOW}Continuing without a scope...")
				count = goback(count)
			elif len(input1) == 0:
				print(f"{Fore.RED}A scope was not provided!")
				continue
			else:
				if '://' not in input1:
					try:
						with open(input1, 'r') as file:
							lines = file.readlines()
							for line in lines:
								line = line.strip()
								scope_urls.add(line)
							file.close()
					except:
						traceback.print_exc()
						count = goback(count)
				else:
					scope_urls.add(input1)
				print(f"{Fore.YELLOW}Scope sucessfully added!")

		if int(main_choice) == 1:
			banner = (f"""{Fore.CYAN}

███████╗███╗   ██╗ ██████╗ ██████╗  █████╗ ██╗      █████╗ ██╗  ██╗    ███████╗███╗   ██╗ ██████╗  ██████╗ ███████╗███████╗
██╔════╝████╗  ██║██╔═══██╗██╔══██╗██╔══██╗██║     ██╔══██╗╚██╗██╔╝    ██╔════╝████╗  ██║██╔═══██╗██╔═══██╗╚══███╔╝██╔════╝
███████╗██╔██╗ ██║██║   ██║██████╔╝███████║██║     ███████║ ╚███╔╝     ███████╗██╔██╗ ██║██║   ██║██║   ██║  ███╔╝ █████╗  
╚════██║██║╚██╗██║██║   ██║██╔══██╗██╔══██║██║     ██╔══██║ ██╔██╗     ╚════██║██║╚██╗██║██║   ██║██║   ██║ ███╔╝  ██╔══╝  
███████║██║ ╚████║╚██████╔╝██║  ██║██║  ██║███████╗██║  ██║██╔╝ ██╗    ███████║██║ ╚████║╚██████╔╝╚██████╔╝███████╗███████╗
╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
                                                                                                                           
"""
		f"{Fore.YELLOW}   Mode 1: Sensitive Information Discovery | Development\n\n"
		f"{Fore.GREEN}  Searching for credentials, tokens, and secrets...\n"
	)
			clear_screen()
			print(banner)
			print("Entering mode 1...")
			inputfile = input("Please enter the file to read the URLs from or enter to load master.json urls: ")
			if not inputfile:
				inputfile = "master.json"
			print(f"{Fore.CYAN}\n┌" + "─" * 91 + "┐")
			print(f"{Style.BRIGHT}| 1. Priority level 1: Checks for comments and keywords on live URLs(slower)"+" "*(90-74)+"|")
			print(f"{Style.BRIGHT}| 2. Priority level 2: Checks for uncommon extensions on live URLs"+" "*(90-64)+"|")
			print(f"{Style.BRIGHT}| 3. Performs the 2 priority levels"+" "*(90-33)+"|")
			print(f"{Style.BRIGHT}| 4. Go back"+" "*(90-10)+"|")
			print(f"{Fore.CYAN}└" + "─" * 91 + "┘"+"\n")
			print(f"{Fore.YELLOW}To save the scan results go back to the main menu and save them\n")
			priority_level = input("Please enter the priority level(1,2,3,4): ")
			if priority_level == "4":
				count = goback(count)
			elif priority_level == "1":
				results = priority1(inputfile, thread_num)
				unique_urls.update(results)
			elif priority_level == "2":
				results = priority2(inputfile, thread_num)
				unique_urls.update(results)
			elif priority_level == "3":
				results = priority1(inputfile, thread_num)
				unique_urls.update(results)
				results = priority2(inputfile, thread_num)
				unique_urls.update(results)
			else:
				print("Please enter a valid priority level")

		elif int(main_choice) == 2:
			#surface scan
			banner = (f"""{Fore.MAGENTA}

██████╗ ██╗██████╗  ██████╗ ███████╗██╗   ██╗    ██╗    ██╗██╗███╗   ██╗██████╗ 
██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝╚██╗ ██╔╝    ██║    ██║██║████╗  ██║██╔══██╗
██████╔╝██║██║  ██║██║  ███╗█████╗   ╚████╔╝     ██║ █╗ ██║██║██╔██╗ ██║██║  ██║
██╔═══╝ ██║██║  ██║██║   ██║██╔══╝    ╚██╔╝      ██║███╗██║██║██║╚██╗██║██║  ██║
██║     ██║██████╔╝╚██████╔╝███████╗   ██║       ╚███╔███╔╝██║██║ ╚████║██████╔╝
╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚══════╝   ╚═╝        ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═════╝ 
                                                                                
     {Fore.YELLOW}   Mode 2: Web Surface Explorer | Development\n
	 {Fore.GREEN}  Looking for developer intended public endpoints(or not so intented)\n
""")
			clear_screen()
			print(banner)
			if len(scope_urls) == 0:
				print(f"{Fore.RED}A scope must be entered in order to continue")
				scope = input("Please enter the scope(URL or file): ")
				if '://' not in scope:
					try:
						with open(scope, 'r') as file:
							lines = file.readlines()
							for line in lines:
								line = line.strip()
								scope_urls.add(line)
							print(f"{Fore.YELLOW}Scope sucessfully added!")
					except Exception:
						print(f"{Fore.RED}You must provide a scope")
						traceback.print_exc()
						sys.exit(1)
				else:
					scope_urls.add(scope)
			print(f"{Fore.MAGENTA}\n┌" + "─" * 91 + "┐")
			print(f"{Style.BRIGHT}| 1. Check robots and sitemaps(recursively)"+" "*(90-41)+"|")
			print(f"{Style.BRIGHT}| 2. Basic HTML/Javascript crawl(without browser)"+" "*(90-47)+"|")
			print(f"{Style.BRIGHT}| 3. Go back"+" "*(90-10)+"|")
			print(f"{Fore.MAGENTA}└" + "─" * 91 + "┘"+"\n")
			results = set()
			second_choice = input("Please enter the mode you would like to use(1,2,3):")

			if second_choice == "1":
				input2 = input("Please enter the robots/sitemap URL or filename(with robots/sitemap URLs): ")
				if '://' not in input2:
					try:
						with open(input2, 'r') as file:
							urls = file.readlines()
							for url in urls:
								url = url.rstrip()
					except:
						traceback.print_exc()
					
					results = parse_robots_url(url, thread_num, results)
					unique_urls.add(results)
					print(f"{Fore.GREEN}Found {len(results)} valid URLs!")
					print(f"{Fore.RED}No more robots/sitemap files found")
					print(f"{Fore.GREEN} URLs sucessfully saved!")
				else:
					results = parse_robots_url(input2, thread_num, results)
					print(f"{Fore.RED}No more robots/sitemap files found")
					print(f"{Fore.GREEN}Found {len(results)} valid URLs")
					for i in results:
						unique_urls.add(i)
					print(f"{Fore.GREEN}URLs sucessfully saved!")
					input("Awaiting to return to main menu...")
					
			elif second_choice == "2":
				url = input(f"{Fore.YELLOW}Please enter the root URL or the file containing the root URLs of the site you want to analyze: ")
				max_depth = input(f"{Fore.YELLOW}Please enter the maxiumum depth level of recursion or press enter to leave empty: ")
				if not max_depth:
					max_depth = -1
				skip = input(f"{Fore.YELLOW}Press s to skip URL validation or enter to validate URLs: ")
				print(f"{Fore.YELLOW} Example -> Cookie: PHPSession=1234567890")
				header = input(f"{Fore.YELLOW}Please enter one custom header(if any): ")
				if not header:
					header = "User-Agent: WEBPOK"
				timeout = input(f"{Fore.YELLOW}Please enter the timeout value in seconds(default=10s): ")
				if not timeout:
					timeout = int(10)
				max_req_num = input(f"{Fore.YELLOW}Please enter the maxiumum paralel requests number(default 1): ")
				if not max_req_num:
					max_req_num = int(1)
				start_urls = set()
				if '://' not in url:
					try:
						with open(url, 'r') as file:
							lines = file.readlines()
							for line in lines:
								line = line.strip()
								start_urls.add(line)
					except:
						traceback.print_exc()
				else:
					start_urls.add(url)
				result = pidgey_recurse(start_urls, scope_urls, int(max_depth), header, int(timeout), int(max_req_num), skip)
				for i in result:
					unique_urls.update(i)
				input("")
			
			elif second_choice == "3":
				count = goback(count)
			else:
				print(f"{Fore.RED}Please enter a valid option!")
		elif int(main_choice) == 3:
			#deep scan
			banner = (f"""{Fore.MAGENTA}

 ██████╗ ███████╗███╗   ██╗ ██████╗  █████╗ ██████╗     ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗███████╗
██╔════╝ ██╔════╝████╗  ██║██╔════╝ ██╔══██╗██╔══██╗    ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝
██║  ███╗█████╗  ██╔██╗ ██║██║  ███╗███████║██████╔╝    ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║███████╗
██║   ██║██╔══╝  ██║╚██╗██║██║   ██║██╔══██║██╔══██╗    ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║╚════██║
╚██████╔╝███████╗██║ ╚████║╚██████╔╝██║  ██║██║  ██║    ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝███████║
 ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝
	   
	Mode 3: Hidden web discovery mode | Development
    Looking in the shadows...                                                                                                               

""")
			clear_screen()
			print(banner)
			print(f"{Fore.MAGENTA}\n┌" + "─" * 91 + "┐")
			print(f"{Style.BRIGHT}| 1. Recursive fuzzer(only 1 URL at a time)"+" "*(90-41)+"|")
			print(f"{Style.BRIGHT}| 2. Fetch known URLs from internet archives"+" "*(90-42)+"|")
			print(f"{Style.BRIGHT}| 3. Find hidden input fields in HTML"+" "*(90-35)+"|")
			print(f"{Style.BRIGHT}| 4. Brute force GET parameters(1 param and 1 URL for now)"+" "*(90-56)+"|")
			print(f"{Style.BRIGHT}| 5. Brute force POST parameters(1 parm and 1 URL for now and only url-encoded data)"+" "*(90-82)+"|")
			print(f"{Style.BRIGHT}| 6. Go back"+" "*(90-10)+"|")
			print(f"{Fore.MAGENTA}└" + "─" * 91 + "┘"+"\n")
			gengar_input = input("Please enter the input you would like to use: ")
			if gengar_input == "1":
				gengar_url = input("Please enter the base URL or enter to use the scope: ")
				if not gengar_url:
					if not len(scope_urls) > 1:
						gengar_url = list(scope_urls)[0]
					else:
						print(f"{Fore.RED} The scope contains more than 1 URL!")
						count = goback()
				gengar_wd = input("Please enter the full path of the wordlist you would like to use: ")
				input_ext = input("Please enter the extensions you would like to use(comma-separated): ")
				if input_ext:
					gengar_ext = set()
					input_ext = [item.strip() for item in input_ext.split(',')]
					for ext in input_ext:
						if not ext.startswith('.'):
							ext = '.' + ext
							gengar_ext.add(ext)
						else:
							continue

				else:
					gengar_ext = set()
				gengar_max_req_num = input("Please enter the maxiumum paralel requests number(default 1): ")
				if not gengar_max_req_num:
					gengar_max_req_num = 1
				gengar_timeout = input("Please enter the timeout for the requests in seconds (default 10s): ")
				if not gengar_timeout:
					gengar_timeout = 10
				print("Example -> Cookie: PHPSession=1234567890")
				gengar_headers = input("Please enter the custom header you would like to use(if any): ")
				gengar_match = matcher()
				gengar_filter = filtering_input()
				rec_fuzz(gengar_url, gengar_wd, gengar_ext, int(gengar_max_req_num), int(gengar_timeout), gengar_headers, thread_num, gengar_match, gengar_filter)			
			
			elif gengar_input == "2":
				gengar_host = input("Please enter the host you would like to search for or enter to use the scope: ")
				if gengar_host:
					gau(gengar_host)
				else:
					for gengar_url in scope_urls:
						gau(gengar_url)
			elif gengar_input == "3":
				gengar_urls = set()
				gengar_option = input("Please enter the URL or filename containg URLs that you want to check: ")
				print("Example -> Cookie: PHPSession=1234567890")
				gengar_header = input("Please enter a custom header(if any): ")
				if "://" not in gengar_option:
					with open(gengar_option, 'r') as file:
						lines = file.readlines()
						for line in lines:
							line = line.rstrip()
							gengar_urls.add(line)
				else:
					gengar_urls.add(gengar_option)

				find_hidden_fields(gengar_urls, gengar_header)

			elif gengar_input == "4":
				gengar_url = input("Please enter the base URL or enter to use the scope: ")
				if not gengar_url:
					if not len(scope_urls) > 1:
						gengar_url = list(scope_urls)[0]
					else:
						print(f"{Fore.RED} The scope contains more than 1 URL!")
						count = goback()
				if gengar_url[-1] == "/":
					gengar_url = f"{gengar_url}/"

				gengar_wd = input("Please enter the full path of the wordlist you would like to use: ")
				gengar_max_req_num = input("Please enter the maxiumum paralel requests number(default 1): ")
				if not gengar_max_req_num:
					gengar_max_req_num = 1
				print("Example -> Cookie: PHPSession=1234567890")
				gengar_headers = input("Please enter the custom header you would like to use(if any): ")
				gengar_timeout = input("Please enter the timeout for the requests in seconds (default 10s): ")
				gengar_testvalue = input("Please enter the test value you want to use or enter(default is test_value): ")
				if not gengar_timeout:
					gengar_timeout = 10

				bruteforce_get_params(gengar_url, gengar_wd, gengar_max_req_num, gengar_headers, gengar_timeout, gengar_testvalue)
			elif gengar_input == "5":
				gengar_url = input("Please enter the base URL or enter to use the scope: ")
				if not gengar_url:
					if not len(scope_urls) > 1:
						gengar_url = list(scope_urls)[0]
					else:
						print(f"{Fore.RED} The scope contains more than 1 URL!")
						count = goback()
				if gengar_url[-1] == "/":
					gengar_url = f"{gengar_url}/"

				gengar_wd = input("Please enter the full path of the wordlist you would like to use: ")
				gengar_max_req_num = input("Please enter the maxiumum paralel requests number(default 1): ")
				if not gengar_max_req_num:
					gengar_max_req_num = 1
				print("Example -> Cookie: PHPSession=1234567890")
				gengar_headers = input("Please enter the custom header you would like to use(if any): ")
				gengar_timeout = input("Please enter the timeout for the requests in seconds (default 10s): ")
				gengar_testvalue = input("Please enter the test value you want to use or enter(default is test_value): ")
				if not gengar_timeout:
					gengar_timeout = 10

				bruteforce_post_params(gengar_url, gengar_wd, gengar_max_req_num, gengar_headers, gengar_timeout, gengar_testvalue)
			elif gengar_input == "6":
				count = goback(count)
			else:
				print(f"{Fore.RED}Please enter a valid choice for gengar!")
				goback(count)

		elif int(main_choice) == 4:
			banner = (f"""{Fore.GREEN}

████████╗██████╗ ███████╗███████╗ ██████╗██╗  ██╗ ██████╗     ██████╗  ██████╗  ██████╗ ████████╗███████╗
╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔════╝██║ ██╔╝██╔═══██╗    ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝██╔════╝
   ██║   ██████╔╝█████╗  █████╗  ██║     █████╔╝ ██║   ██║    ██████╔╝██║   ██║██║   ██║   ██║   ███████╗
   ██║   ██╔══██╗██╔══╝  ██╔══╝  ██║     ██╔═██╗ ██║   ██║    ██╔══██╗██║   ██║██║   ██║   ██║   ╚════██║
   ██║   ██║  ██║███████╗███████╗╚██████╗██║  ██╗╚██████╔╝    ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝
    
    Mode 4: Display saved URLs in a tree-view mode | Development
    Overviewing the targets...                                                                                            
""")
			clear_screen()
			print(banner)
			input("Press enter to load master.json: ")
			try:
				initialize_tkinter_treecko('master.json')
			except Exception:
				print(f"{Fore.RED}There was an error in processing your master.json:")
				traceback.print_exc()
		elif int(main_choice) == 5:
			#save the results to master.json
			banner = (f"""{Fore.YELLOW}

██████╗ ██╗██╗  ██╗ █████╗  ██████╗██╗  ██╗██╗   ██╗    ██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
██╔══██╗██║██║ ██╔╝██╔══██╗██╔════╝██║  ██║██║   ██║    ██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
██████╔╝██║█████╔╝ ███████║██║     ███████║██║   ██║    ██║   ██║███████║██║   ██║██║     ██║   
██╔═══╝ ██║██╔═██╗ ██╔══██║██║     ██╔══██║██║   ██║    ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║   
██║     ██║██║  ██╗██║  ██║╚██████╗██║  ██║╚██████╔╝     ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║   
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝       ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝   
                                                                                                
	Mode 5: Save the results into master.json | Development
	Keeping things organized...                                                                                                       

""")
			clear_screen()
			print(banner)
			input("Press enter to continue: ")
			#write the results to a json file
			if len(unique_urls) != 0:
				write_to_json(unique_urls, 'master.json')
				print(f"{Fore.GREEN}Results sucessfully written to {os.getcwd()}/master.json")
				unique_urls.clear()
				print(f"{Fore.GREEN}URLs in memory flushed sucessfully!")
				input("Awaiting to return to main...")
			else:
				print(f"{Fore.YELLOW}No unique urls in memory!")
				input("Awaiting to return to main...")
				goback(count)
				
		elif int(main_choice) == 6:
			banner = (f"""{Fore.MAGENTA}

██████╗ ██╗████████╗████████╗ ██████╗     ████████╗██╗    ██╗██╗███╗   ██╗███████╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
██╔══██╗██║╚══██╔══╝╚══██╔══╝██╔═══██╗    ╚══██╔══╝██║    ██║██║████╗  ██║██╔════╝    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
██║  ██║██║   ██║      ██║   ██║   ██║       ██║   ██║ █╗ ██║██║██╔██╗ ██║███████╗    ██║     ███████║█████╗  ██║     █████╔╝ 
██║  ██║██║   ██║      ██║   ██║   ██║       ██║   ██║███╗██║██║██║╚██╗██║╚════██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
██████╔╝██║   ██║      ██║   ╚██████╔╝       ██║   ╚███╔███╔╝██║██║ ╚████║███████║    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
╚═════╝ ╚═╝   ╚═╝      ╚═╝    ╚═════╝        ╚═╝    ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
                                                                                                                              
	Mode 6: Looking for duplicates in the master.json file  | Development
	Looking for twins...
""")
			clear_screen()
			print(banner)
			input(f"{Fore.MAGENTA}Press enter to continue: ")
			try:
				duplicates = find_duplicates_in_json('master.json')
				if duplicates:
					print(f"{Fore.MAGENTA}Found {len(duplicates)} duplicated URLs!")
					terciary_choice = input(f"{Fore.MAGENTA}Enter d to delete them from master.json or enter to go back: ")
					if not terciary_choice:
						count = goback(count)
						continue
					elif terciary_choice == "d":
						remove_duplicates_from_json('master.json', duplicates)
						continue
					else:
						print(f"{Fore.RED}Please enter a valid option")
						continue
				else:
					print(f"{Fore.MAGENTA}None duplicates were found!")
					input(f"{Fore.MAGENTA}Press enter to continue to main menu...")
					continue
			except Exception:
				print(f"{Fore.RED}There was an error while looking for or deleting duplicates")
				traceback.print_exc()
			#check for uniqueness in master.json
			sys.exit(0)
		elif int(main_choice) == 7:
			banner = (f"""{Fore.RED}

██╗  ██╗ █████╗ ██╗    ██╗██╗     ██╗   ██╗ ██████╗██╗  ██╗ █████╗     ███████╗██╗ ██████╗ ██╗  ██╗████████╗
██║  ██║██╔══██╗██║    ██║██║     ██║   ██║██╔════╝██║  ██║██╔══██╗    ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
███████║███████║██║ █╗ ██║██║     ██║   ██║██║     ███████║███████║    ███████╗██║██║  ███╗███████║   ██║   
██╔══██║██╔══██║██║███╗██║██║     ██║   ██║██║     ██╔══██║██╔══██║    ╚════██║██║██║   ██║██╔══██║   ██║   
██║  ██║██║  ██║╚███╔███╔╝███████╗╚██████╔╝╚██████╗██║  ██║██║  ██║    ███████║██║╚██████╔╝██║  ██║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    Mode 7: View the results smartly
    An Unmatched Vision for Strategic Mastery                                                                                                    

""")
			clear_screen()
			print(banner)
			print(f"{Fore.RED}\n┌" + "─" * 91 + "┐")
			print(f"{Style.BRIGHT}| 1. Extension and keywords check on URLs"+" "*(90-41+2)+"|")
			print(f"{Style.BRIGHT}| 2. Find guessable parameters in URLs(numeric)"+" "*(90-47+2)+"|")
			print(f"{Style.BRIGHT}| 3. Parse a Burp-comptabile JSON scope file"+" "*(90-44+2)+"|")
			print(f"{Style.BRIGHT}| 4. Go back"+" "*(90-12+2)+"|")
			print(f"{Fore.RED}└" + "─" * 91 + "┘"+"\n")
			hawlucha_input = input("Please enter the option you would like to use: ")
			if hawlucha_input == "1":
				urls_to_process = hawlucha_file()
				ext_keyword_check(urls_to_process)

			elif hawlucha_input == "2":
				guess_params(urls_to_process)

			elif hawlucha_input == "3":
				jsonfile = input("Please enter the Burp-comptabile JSON scope file: ")
				scope_view(jsonfile)

			elif hawlucha_input == "4":
				count = goback(count)
			else:
				print(f"{Fore.RED}You must enter a valid option!")

		elif int(main_choice) == 8:
			banner = (f"""{Fore.CYAN} 

██████╗ ██╗   ██╗███████╗██╗
██╔══██╗╚██╗ ██╔╝██╔════╝██║
██████╔╝ ╚████╔╝ █████╗  ██║
██╔══██╗  ╚██╔╝  ██╔══╝  ╚═╝
██████╔╝   ██║   ███████╗██╗
╚═════╝    ╚═╝   ╚══════╝╚═╝
                            
 	THANK YOU FOR USING OUR PROGRAM!
 	   WE HOPE TO SEE YOU AGAIN! """

    		)
			clear_screen()
			print(banner)
			sys.exit(0)
		else:
			print(f"{Fore.RED}please enter a valid choice")
