import requests as r
import json
import traceback

def hawlucha_file():
	"""
	Function used to read results files, master.json or custom
	returns urls_to_process
	"""
	urls_to_process = set()
	inputfile = input("Please enter the file containing the results to analyze, or press enter to analyze all the saved results file, or m for master.json: ")
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
	elif inputfile == "m":
		try:
			with open("master.json", 'r') as file:
				urls = json.load(file)
				for url in urls:
					url = url.rstrip()
					urls_to_process.add(url)
		except:
			traceback.print_exc()

	else:
		if os.path.exists(inputfile):
			try:
				with open(inputfile, 'r') as file:
					lines = file.readlines()
					for line in lines:
						line = line.rstrip()
						urls_to_process.add(line)
			except:
				traceback.print_exc()
		else:
			print(f"{Fore.RED}File {file} not found!")

	return urls_to_process

def matcher():
	"""
	Function used to define matching patterns
	returns a dictionary with the following elements: { status_code: <int>, size: <int> }
	default values are:
	{ status_code: 200, size: -1 }
	-1 means to not use that matching pattern
	"""
	match = dict()
	status_code = input("Please enter the matching status code(default 200): ")
	if len(status_code) != 0:
		match["status_code"] = status_code
	else:
		match["status_code"] = 200

	size = input("Please enter the response size match(enter to leave empty): ")
	if len(size) != 0:
		match["size"] = size

	else:
		match["size"] = -1

	return match

def filtering_input():
	"""
	Function used to define filtering patterns
	returns a dictionary with the following elements: { status_code: <int>, size: <int> }
	default values are:
	{ status_code: -1, size: -1 }
	-1 means to not use that filtering pattern
	"""
	filtering = {}
	status_code = input("Please enter the filtering status code or enter to leave empty: ")
	if len(status_code) != 0:
		filtering["status_code"] = status_code
	else:
		filtering["status_code"] = -1

	size = input("Please enter the response size filter(enter to leave empty): ")
	if len(size) != 0:
		filtering["size"] = size

	else:
		filtering["size"] = -1

	return filtering

def calibraton(url, headers, method):
    """
    Function used to get the normal length of a response
    """
    if method == "GET":
        response = r.get(url=url, headers=headers)
        return len(response.text)
    elif method == "POST":
        response = r.post(url=url, headers=headers)
        return len(response.text)
    else:
        print(f"{Fore.RED}Bad method specified(must be GET or POST) {method}")
