import requests
import sys
import json
from pwn import *
import time
import threading
import traceback

stop_threads = False

def update_progress_bar(progress_bar, start_time):
    global stop_threads
    while True:
        if stop_threads:
            break
        else:
            elapsed_time = time.time() - start_time
            progress_bar.status(f"Seconds waiting: {elapsed_time}")
            time.sleep(1)  # Update every second

def waybackurls(host, with_subs, progress_bar):
    global stop_threads
    if with_subs:
        url = 'http://web.archive.org/cdx/search/cdx?url=*.%s/*&output=json&fl=original&collapse=urlkey' % host
    else:
        url = 'http://web.archive.org/cdx/search/cdx?url=%s/*&output=json&fl=original&collapse=urlkey' % host
    
    # Start the progress bar in a separate thread
    start_time = time.time()
    progress_thread = threading.Thread(target=update_progress_bar, args=(progress_bar, start_time))
    progress_thread.start()
    #print("thread started")
    
    try:
        #print("try entered")
        r = requests.get(url)
        print("[+] urls gathered sucessfully!")
        stop_threads = True
        progress_thread.join()
        progress_bar.success()
    except:
        stop_threads = True
        progress_thread.join()
        traceback.print_exc()
    results = r.json()
    return results[1:]


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 2:
        print('Usage:\n\tpython3 waybackurls.py <url> <include_subdomains:optional>')
        sys.exit()

    host = sys.argv[1]
    with_subs = False
    if argc > 3:
        with_subs = True

    progress_bar = log.progress("Collecting URLs...")
    urls = waybackurls(host, with_subs, progress_bar)
    print(f'[+]Found {len(urls)} URLs!')
    #for url in urls:
        #print(url)
