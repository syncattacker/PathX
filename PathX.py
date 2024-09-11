import argparse
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError
from colorama import Fore, Style, init

init()

parser = argparse.ArgumentParser(description='Directory Brute-Forcer')
parser.add_argument('--url', '-u', required=True, help='Base URL to brute force')
parser.add_argument('--wordlist', '-w', required=True, help='Path to wordlist file')
parser.add_argument('--ignore-status-code', '-i', type=int, default=None, help='Status code to ignore (default is all 5xx)')
parser.add_argument('--verbose', action='store_true', default=True, help='Enable verbose output')
parser.add_argument('--rate-limit', type=int, default=16, help='Number of requests per second')
parser.add_argument('--mode', '-m', choices=['dir', 'sub'], default='dir', help='Mode of operation: dir for directory and sub for subdomain')
parser.add_argument('--output', '-o', help='File to save found URLs')
parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (minimum is 10)')
args = parser.parse_args()

# Ensure timeout is not less than 10 seconds
timeout = max(args.timeout, 10)

statusCodes = set(range(200, 209)) | set(range(300, 309)) | {401, 403}

def dirSubBuster(baseURL : str, word : str, ignore_status_code : int, mode : str, outputFile : str, errors : int) -> None:
    url = f"{baseURL}/{word}" if mode == 'dir' else f"{word}.{baseURL}"
    try:
        response = requests.get(url, timeout=timeout)
        if ignore_status_code and response.status_code == ignore_status_code:
            return
        if response.status_code in statusCodes:
            message = f"[FOUND] [{time.strftime('%H:%M:%S')}] {url} (STATUS CODE : {response.status_code}) (CONTENT LENGTH : {len(response.content)})"
            print(Fore.GREEN + message + Style.RESET_ALL)
            if outputFile:
                with open(outputFile, 'a') as f:
                    f.write(f"{url} (STATUS CODE : {response.status_code}) (CONTENT LENGTH : {len(response.content)})\n")
    except (ConnectionError, Timeout, HTTPError, RequestException):
        errors[0] += 1
        pass

def banner(url : str, timeout : int, rate_limit : int) -> None:
    print("""
    ____        __  __   _  __
   / __ \____ _/ /_/ /_ | |/ /
  / /_/ / __ `/ __/ __ \|   / 
 / ____/ /_/ / /_/ / / /   |  
/_/    \__,_/\__/_/ /_/_/|_|  

""")
    print("v1.0.0 - BETA")
    print("By @syncattacker")
    print("-----------------------------------------------")
    print("METHOD : GET")
    print(f"URL : {url}")
    print(f"TIMEOUT : {timeout}")
    print(f"RATE LIMIT : {rate_limit}")
    print(f"STATUS CODE : 200-209, 300-309, 401, 403")
    print("-----------------------------------------------")

def main():
    banner(args.url, timeout, args.rate_limit)
    startTime = time.time()
    errors = [0]
    try:
        with open(args.wordlist, 'r', encoding = "latin1") as file:
            words = [line.strip() for line in file]
        total_requests = len(words)
        print(Fore.BLUE + f"[INFO] [{time.strftime('%H:%M:%S')}] TOTAL REQUESTS : {total_requests}" + Style.RESET_ALL)
        delay = 1 / args.rate_limit
        with ThreadPoolExecutor(max_workers=args.rate_limit) as executor:
            futures = []
            for word in words:
                futures.append(executor.submit(dirSubBuster, args.url, word, args.ignore_status_code, args.mode, args.output, errors))
                time.sleep(delay)
            for future in as_completed(futures):
                future.result()
    except KeyboardInterrupt:
        print(Fore.RED + f"[ERROR] [{time.strftime('%H:%M:%S')}] KEYBOARD INTERRUPT TRIGGERED!" + Style.RESET_ALL)
        exit()
    completionTime = time.time()
    timeTaken = completionTime - startTime
    print(Fore.BLUE + f"[INFO] [{time.strftime('%H:%M:%S')}] ELAPSED TIME : {timeTaken:.2f}" + Style.RESET_ALL)
    print(Fore.RED + f"[ERROR] [{time.strftime('%H:%M:%S')}] ERRORS ENCOUNTERED : {errors[0]}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
