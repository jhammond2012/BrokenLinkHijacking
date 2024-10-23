# This Tool is made for educational purposes. Use at your own risk.

# Link Checker and Crawler

This Python script is designed to crawl a website, check for broken links, and report HTTP errors. It supports both single URLs and lists of subdomains.

## Features

- Crawl a website to find inbound and outbound links.
- Check the status of links to identify broken links and HTTP errors.
- Handle lists of subdomains from a file.
- Customizable depth of crawling.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/ya3raj/BrokenLinkHijacking.git
    cd BrokenLinkHijacking
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Crawling a Single URL

To crawl a single URL and check for broken links, use:

```sh
python link_checker_crawler.py -u http://example.com -d 2
```

To crawl multiple URL and check for broken links, use:

```sh
python link_checker_crawler.py -u subdomains.txt
```
## Inspired from `https://github.com/MayankPandey01/BrokenLinkHijacker`
