"""
Website Watcher Script

This Python script is designed to monitor multiple website URLs specified in a 'urls.txt' file. It provides two primary options for monitoring websites: 
1. Watch (--watch): Check if a specific string pattern is present on the web page.
2. Unwatch (--unwatch): Check if a specific string pattern is absent on the web page.

The script supports the use of cookies and custom headers, which can be provided using the --cookies and --headers options. Cookies and headers are loaded from the specified files to make HTTP requests.

Usage:
    python website_watcher.py [URL] [-w WATCH_FILE] [-u UNWATCH_FILE] [-c COOKIES_FILE] [-b HEADERS_FILE]

Parameters:
    [URL]: The URL of the website you want to monitor.
    
    -w, --watch [WATCH_FILE]: The filename in the ./cre folder, containing patterns to discover for each website. Ordered. "IGNORE_ME_PLEASE" to ignore, for each site.
    
    -u, --unwatch [UNWATCH_FILE]: The filename in the ./cre folder, containing patterns to NOT discover for each website. Ordered. "IGNORE_ME_PLEASE" to ignore, for each site.
    
    -c, --cookies [COOKIES_FILE]: File containing cookies to include in the HTTP requests.
    
    -b, --headers [HEADERS_FILE]: File containing custom headers to include in the HTTP requests. Can be left empty.

Note:
- The script uses the 'requests' library for making HTTP requests.
- To ensure secure requests, SSL verification warnings are disabled.

Example Usage:
    python website_watcher.py urls.txt -c cookies.txt -w watch.txt -u unwatch.txt -b headers.txt

Date: 2021-09-18
"""

import requests
import argparse
from pathlib import Path
import json
import time
import os
import re

requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='Watch URL for change.')
parser.add_argument('url', type=str, help='URL to watch')
parser.add_argument('-w', '--watch', type=str, help='String to watch for')
parser.add_argument('-u', '--unwatch', type=str, help='String to unwatch for')
parser.add_argument('-c', '--cookies', type=str, help='File with cookies stored')
parser.add_argument('-b', '--headers', type=str, help='File with headers stored')
args = parser.parse_args()

## ----------------------
# Get URL args
if args.url is not None:
    url_file = Path(f"./cre/{args.url}")
    if url_file.is_file():
        with open(f"./cre/{args.url}") as file:
            urls = [line.rstrip() for line in file]
    else:
        print(f"URL file {args.url} isn't a file")
        exit(-1)        
else:
    print("URL is none")
    exit(-1)

# Set cookies
if args.cookies is not None:
    cook_file = Path(f"./cre/{args.cookies}")
    if cook_file.is_file():
        with open(f"./cre/{args.cookies}") as file:
            cookies = [json.loads(cookie) for cookie in file]
    else:
        print(f"Cookies file {args.cookies} isn't a file")
        exit(-1)
else:
    cookies = {}

# Set watch/unwatch
if args.watch is None and args.unwatch is None:
    print(f"Specify either watch or unwatch")
    exit(-1)

if args.watch is not None:
    watch_file = Path(f"./cre/{args.watch}")
    if watch_file.is_file():
        with open(f"./cre/{args.watch}") as file:
            watchs = [line.rstrip() for line in file]
else:
    watchs = [None for i in range(len(urls))]

if args.unwatch is not None:
    unwatch_file = Path(f"./cre/{args.unwatch}")
    if unwatch_file.is_file():
        with open(f"./cre/{args.unwatch}") as file:
            unwatchs = [line.rstrip() for line in file]
else:
    unwatchs = [None for i in range(len(urls))]

# Set mandatory headers
headerss = []
headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1",
}
if args.headers is not None:
    headers_file = Path(f"./cre/{args.headers}")
    if headers_file.is_file():
        with open(f"./cre/{args.headers}") as file:
            for h in file:
                new_head = {**headers.copy(), **json.loads(h)}
                headerss.append(new_head)

with open("./cre/checker.txt") as file:
    checkers = [c.rstrip() for c in file]

#cmd = "wsl-notify" - #os.system(f"wsl-notify 'Found in {urls[i][:10]}'")
cmd = 'powershell.exe New-BurntToastNotification -Text'
print("Running ...")

tries, errors, max_error_rate = 0, 0, 0.2
interval = 300
while True:
    try:
        tries += 1
        print(f'{tries}st pass, {errors} errors')

        for i in range(len(urls)):
            r = requests.get(urls[i], cookies=cookies[i], headers=headerss[i])

            # Detection
            if r.status_code == 200:
                if watchs[i] is not None and watchs[i] != "IGNORE_ME_PLEASE" and unwatchs[i] is not None and unwatchs[i] != "IGNORE_ME_PLEASE":
                    if watchs[i] in r.text and unwatchs[i] not in r.text:
                        os.system(f"{cmd} 'Found and unfound in {urls[i][:10]}'")
                elif watchs[i] is not None and watchs[i] != "IGNORE_ME_PLEASE" and watchs[i] in r.text:
                    os.system(f"{cmd} 'Found in {urls[i][:10]}'")
                elif unwatchs[i] is not None and unwatchs[i] != "IGNORE_ME_PLEASE" and unwatchs[i] not in r.text:
                    os.system(f"{cmd} 'Unfound in {urls[i][:10]}'")
            
                # Sanity check
                if checkers[i] != "IGNORE_ME_PLEASE" and checkers[i] not in r.text:
                  print(f"Issue : {checkers[i]} not found in {urls[i][:10]}")
                  os.system(f"{cmd} 'Issue : checker not found in {urls[i][:10]}'")
                  exit(-1)

            # Bad detection with status code
            elif r.status_code == 401 or r.status_code == 302:
                os.system(f"{cmd} 'Issue : {r.status_code} in {urls[i][:10]}'")
                exit(-1)

            # Error (eg 403)
            else:
                print(f"Error {r.status_code} for {urls[i]}")
                errors += 1
            
            # Check error rate for every loop
            if errors/(tries*len(urls)) >= max_error_rate and tries > 10:
                os.system(f"{cmd} 'We've got {errors} errors, last error : {r.status_code}, aborting ...'")
                print(f"More than {errors} errors, last error : {r.status_code}, aborting ...")
                exit(-1)
    except KeyboardInterrupt:
        print("Can't quit while working on the results.")
    try:
        time.sleep(interval)
    except KeyboardInterrupt:
        print("Exiting ...")
        break
print("Out of loop, goodbye")
exit(0)