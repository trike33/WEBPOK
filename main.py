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
    sys.exit(0)


if __name__ == '__main__':
	#Registering the signal handler
	signal.signal(signal.SIGINT, signal_handler)
	init(autoreset=True) #initialize colorama colors
	unique_urls = set()  # Use a set to store unique URLs across scans
	scope_urls = set() # set used to track the target scope(if provided)
	count = 0 #variable used to only ask things the first time
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #disable unsecure HTTPS warning
	while True:
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
		print("1. Search info disclosures from a file containing URLs")
		print("2. Enter web surface discovery mode")
		print("3. Enter hidden web discovery mode")
		print("4. Print the tree view of the target/targets URL(usefull for small sites)")
		print("5. Save the results into master.json")
		print("6. Check for uniqueness in the master.json file(useful when master.json is not empty)")
		print("7. Parse the info disclosures results from module 1(useful to avoid false positives)")
		print("8. Exit")
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
			print(banner)
			print("Entering mode 1...")
			inputfile = input("Please enter the file to read the URLs from or enter to load master.json urls: ")
			if not inputfile:
				inputfile = "master.json"
			print("1. Priority level 1: Checks for comments and keywords on live URLs | not recommended for large sites")
			print("2. Priority level 2: Checks for uncommon extensions on live URLs")
			print("3. Performs the 2 priority levels")
			print("4. Go back\n")
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
				else:
					scope_urls.add(scope)
			print("1. Check robots and sitemaps(recursively)")
			print("2. Basic HTML/Javascript crawl")
			print("3. Advanced HTML/Javascript crawl(headless browser)")
			print("4. All(not implemented yet)")
			print("5. Go back")
			results = set()
			second_choice = input("Please enter the mode you would like to use(1,2,3,4,5,6):")

			if second_choice == "1":
				input2 = input("Please enter the robots/sitemap URL or filename(with robots/sitemap URLs): ")
				if '://' not in input2:
					try:
						with open(inputfile, 'r') as file:
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
					unique_urls.add(results)
					print(f"{Fore.GREEN}URLs sucessfully saved!")
			elif second_choice == "2":
				url = input(f"{Fore.YELLOW}Please enter the root URL or the file containing the root URLs of the site you want to analyze: ")
				max_depth = input(f"{Fore.YELLOW}Please enter the maxiumum depth level of recursion or press enter to leave empty: ")
				if len(max_depth) == 0:
					max_depth = -1 
				skip = input(f"{Fore.YELLOW}Press s to skip URL validation or enter to validate URLs: ")
				header = input(f"{Fore.YELLOW}Please enter one custom header(if any): ")
				print(f"{Fore.YELLOW} Example -> Cookie: PHPSession=1234567890")
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
				result = recursive_parsing(start_urls, thread_num, scope_urls, int(max_depth), skip, header)
				unique_urls.update(result)
			
			elif second_choice == "6":
				count = goback(count)
			else:
				print(f"{Fore.RED}Please enter a valid option!")
		elif int(main_choice) == 3:
			#deep scan
			banner = (f"""{Fore.MAGENTA}

 ██████╗ ██╗  ██╗ █████╗ ███████╗████████╗██╗  ██╗   ██╗    ██╗    ██╗██╗  ██╗██╗███████╗██████╗ ███████╗██████╗ ███████╗
██╔════╝ ██║  ██║██╔══██╗██╔════╝╚══██╔══╝██║  ╚██╗ ██╔╝    ██║    ██║██║  ██║██║██╔════╝██╔══██╗██╔════╝██╔══██╗██╔════╝
██║  ███╗███████║███████║███████╗   ██║   ██║   ╚████╔╝     ██║ █╗ ██║███████║██║███████╗██████╔╝█████╗  ██████╔╝███████╗
██║   ██║██╔══██║██╔══██║╚════██║   ██║   ██║    ╚██╔╝      ██║███╗██║██╔══██║██║╚════██║██╔═══╝ ██╔══╝  ██╔══██╗╚════██║
╚██████╔╝██║  ██║██║  ██║███████║   ██║   ███████╗██║       ╚███╔███╔╝██║  ██║██║███████║██║     ███████╗██║  ██║███████║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝        ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝
       Mode 3: Hidden web discovery mode | Development
       Looking in the shadows...                                                                                                               

""")
			print(banner)
			print("1. Recursive fuzzer")
			print("2. Fetch known URLs from internet archives")
			continue
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

			print(banner)
			input("Press enter to continue: ")
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
			print(banner)
			input("Press enter to continue: ")
			#write the results to a json file
			write_to_json(unique_urls, 'master.json')
			print(f"{Fore.GREEN}Results sucessfully written to {os.getcwd()}/master.json")
			unique_urls.clear()
			print(f"{Fore.GREEN}URLs in memory flushed sucessfully!")

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
        Mode 7: Smartly view the results from module 1
        An Unmatched Vision for Strategic Mastery                                                                                                    

""")
			print(banner)
			print("1. Extension and keywords check on URLs")
			print("2. Find guessable parameters in URLs")
			print("3. Go back")
			hawlucha_input = input("Please enter the option you would like to use: ")
			inputfile = input("Please enter the file containing the results to analyze or press enter to analyze all the saved results file: ")
			urls_to_process = set()
			urls_to_process.clear()
			if not inputfile:
				inputfiles = ['snorlax_result.txt', 'pidgey_results.txt', 'pidgey_results_sensitive.txt']
				for file in inputfiles:
					if os.path.exists(file):
						try:
							with open(file, 'r') as file:
								lines = file.readlines()
								for line in lines:
									line = line.rstrip()
									urls_to_process.add(line)
						except:
							print_exc.traceback()
					else:
						print(f"{Fore.RED}File {file} not found!")
			
			if hawlucha_input == "1":
				ext_keyword_check(urls_to_process)

			elif hawlucha_input == "2":
				sys.exit(1)

			elif hawlucha_input == "3":
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
			print(banner)
			sys.exit(0)
		else:
			print(f"{Fore.RED}please enter a valid choice")