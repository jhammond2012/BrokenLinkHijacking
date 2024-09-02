import requests
from urllib.parse import urlparse, urljoin
import urllib3
from bs4 import BeautifulSoup
import colorama
import sys
import argparse
import random
import threading
from time import sleep

colorama.init()

headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"}

to_verify_ssl_cert = False  # Change it to True if SSL errors are thrown
urllib3.disable_warnings()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
RED = colorama.Fore.RED
BLUE = colorama.Fore.BLUE
CYAN = colorama.Fore.CYAN

social_list = ["twitter.com", "facebook.com", "instagram.com", "linkedin.com", "youtube.com", "twitch.com", "twitch.tv", "discord.com", "slack.com", "soundcloud.com", "medium.com",
               "vimeo.com", "skype.com", "pinterest.com", "ct.pinterest.com", "snapchat.com", "telegram", "t.me", "telegram.com", "clickcease.com", "wistia.com", "adjust.com", "github.com"]

inbound_urls = set()
outbound_urls = set()
current_inbound_urls = set()
broken_urls = set()
social_urls = []
number_of_broken_link = 0
total_urls_visited = 0

def banner():
    version = "1.0"
    ascii_banner = """
     ____            _                _     _       _
    | __ ) _ __ ___ | | _____ _ __   | |   (_)_ __ | | __
    |  _ \| '__/ _ \| |/ / _ \ '_ \  | |   | | '_ \| |/ /
    | |_) | | | (_) |   <  __/ | | | | |___| | | | |   <
    |____/|_|  \___/|_|\_\___|_| |_| |_____|_|_| |_|_|\_\\

     _   _ _  _            _               _   _   _
    | | | (_)(_) __ _  ___| | _____ _ __  | | | | | |
    | |_| | || |/ _` |/ __| |/ / _ \ '__| | | | | | |
    |  _  | || | (_| | (__|   <  __/ |    |_| |_| |_|
    |_| |_|_|/ |\__,_|\___|_|\_\___|_|    (_) (_) (_)
           |__/
    """
    print(ascii_banner)
    print(f"{RED}                        Version-", version)

def random_ua():
    UAS = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
           "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
           "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
           "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1",
           "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36"
           )
    ua = UAS[random.randrange(len(UAS))]
    ua = str(ua)
    headers['user-agent'] = ua

def is_valid(url):
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme) and parsed.scheme in ['http', 'https']
    except Exception as e:
        print(f"{RED} ERROR Parsing URL {url} {RESET}\n{e}")
        sys.exit()

def main_webpage_links(url):
    try:
        urls = set()
        random_ua()
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(url, headers=headers, verify=to_verify_ssl_cert).content, "html.parser")
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                continue
            if href in inbound_urls:
                continue
            if domain_name not in href:
                if href not in outbound_urls:
                    if verbosity:
                        print(f"{BLUE}[!] Outbound link: {href}{RESET}")
                    outbound_urls.add(href)
                    social_domain = str(urlparse(href).netloc)
                    if social_domain and social_domain.strip('www.') in social_list:
                        social_urls.append(href)
                continue
            if verbosity:
                print(f"{GREEN}[*] Inbound link: {href}{RESET}")
            urls.add(href)
            inbound_urls.add(href)

        for img_tag in soup.findAll('img'):
            href = img_tag.attrs.get('src')
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                continue
            if href in inbound_urls:
                continue
            if domain_name not in href:
                if href not in outbound_urls:
                    if verbosity:
                        print(f"{GRAY}[!] Outbound Image link: {href}{RESET}")
                    outbound_urls.add(href)
                    social_domain = str(urlparse(href).netloc)
                    if social_domain and social_domain.strip('www.') in social_list:
                        social_urls.append(href)
                continue
            if verbosity:
                print(f"{GRAY}[!] Inbound Image link: {href}{RESET}")
            inbound_urls.add(href)

        return urls
    except KeyboardInterrupt:
        print(f"{RED} Keyboard Interrupt detected{RESET} ")
        sys.exit()

def crawl(url):
    try:
        global total_urls_visited
        total_urls_visited += 1
        links = main_webpage_links(url)
        for link in links:
            random_ua()
            crawl(link)
    except KeyboardInterrupt:
        print(f"{RED} Keyboard Interrupt detected{RESET} ")
        sys.exit()
    except Exception as e:
        print(f"{RED} ERROR While Crawling {RESET}\n{e} ")
        sys.exit()

def status_check(url):
    try:
        r = requests.get(url, headers=headers, verify=to_verify_ssl_cert)
        if r.status_code == 404:
            global number_of_broken_link
            number_of_broken_link += 1
            print(f"{RED}[!] BROKEN LINK: {url}{RESET}")
        if r.status_code == 301 or r.status_code == 302 or r.status_code == 401 or r.status_code == 403 or r.status_code == 429 or r.status_code == 500 or r.status_code == 503:
            print(f"{CYAN}[!] HTTP ERROR : {url}{r.status_code}{RESET}")
    except KeyboardInterrupt:
        print(f"{RED} Keyboard Interrupt detected{RESET} ")
        sys.exit()
    except Exception as e:
        print(f"{CYAN}[!] UNABLE TO CONNECT : {url}{RESET}\n{e}")

def process_subdomains(subdomains):
    for subdomain in subdomains:
        subdomain = subdomain.strip()
        print(f"{BLUE}[*] Scanning Subdomain: {subdomain}{RESET}")
        crawl(subdomain)
        print(f"{BLUE}[*] Scanning completed for: {subdomain}{RESET}")

def main_proc(deep):
    threads = []

    if deep == 1:
        links = main_webpage_links(url)
        print("")
        search_msg()
        for link in outbound_urls:
            link = str(link)
            threads.append(threading.Thread(target=status_check, args=(link,)))
    elif deep == 2:
        links = main_webpage_links(url)
        print("")
        search_msg()
        for link in links:
            link = str(link)
            threads.append(threading.Thread(target=crawl, args=(link,)))
    elif deep == 3:
        links = main_webpage_links(url)
        print("")
        search_msg()
        for link in links:
            link = str(link)
            threads.append(threading.Thread(target=crawl, args=(link,)))
            threads.append(threading.Thread(target=status_check, args=(link,)))

    print(f"{BLUE}[*] Total number of threads : {len(threads)}{RESET}")
    random.shuffle(threads)
    for thread in threads:
        thread.start()
        sleep(random.uniform(0.1, 1.5))
    for thread in threads:
        thread.join()

    print(f"\n{GREEN}[*] Total URLs visited: {total_urls_visited}{RESET}")
    print(f"{RED}[*] Total Broken Links: {number_of_broken_link}{RESET}")
    print(f"{CYAN}[*] Total Outbound URLs: {len(outbound_urls)}{RESET}")
    print(f"{BLUE}[*] Total Inbound URLs: {len(inbound_urls)}{RESET}")

def search_msg():
    print(f"{GREEN}[*] Starting the scan...{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple web crawler to find broken links and check HTTP statuses.")
    parser.add_argument("-u", "--url", type=str, help="The URL to crawl.", required=False)
    parser.add_argument("-d", "--depth", type=int, default=2, choices=[1, 2, 3], help="Depth of crawling (1-3).")
    parser.add_argument("-s", "--subdomains", type=str, help="File containing subdomains to scan.", required=False)

    args = parser.parse_args()

    banner()
    verbosity = True
    if args.url:
        url = args.url
        if not is_valid(url):
            print(f"{RED} Invalid URL {url}{RESET}")
            sys.exit()
        print(f"{BLUE}[*] Starting scan for URL: {url}{RESET}")
        main_proc(args.depth)
    elif args.subdomains:
        try:
            with open(args.subdomains, "r") as file:
                subdomains = file.readlines()
                print(f"{BLUE}[*] Starting scan for subdomains from file: {args.subdomains}{RESET}")
                process_subdomains(subdomains)
        except FileNotFoundError:
            print(f"{RED} File not found: {args.subdomains}{RESET}")
            sys.exit()
    else:
        print(f"{RED} No URL or subdomains file provided. Use -u for URL or -s for subdomains file.{RESET}")
        sys.exit()
