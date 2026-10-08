# Web Scraper
 
A command-line web crawler written in Python. Give it a starting URL and it crawls every page it can reach on the same domain, collecting each page's heading, first paragraph, outgoing links, and image URLs, then writes everything to a JSON report.
 
Built as part of Boot.dev's *Build a Web Scraper* guided project.
 
## Features
 
- **Asynchronous crawling** with `asyncio` and `aiohttp`, fetching many pages at once
- **Concurrency limit** (semaphore) so the crawler stays polite to the server
- **Page limit** to stop a crawl after a set number of pages
- **Same-domain only**: it never follows links off the starting site
- **URL normalization** so `http://`, `https://`, trailing slashes, and capitalization variants of a URL count as one page
- **HTML parsing** with Beautiful Soup: heading (`<h1>`, falling back to `<h2>`), first paragraph (preferring `<main>`), links, and images, with relative URLs converted to absolute ones
- **Error handling** for failed requests (HTTP errors and non-HTML responses are skipped and reported)
- **JSON report** of everything it found, written to `report.json`
- **Unit tests** written test-first (TDD) with `unittest`
## Requirements
 
- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management
Dependencies (installed automatically by uv): `aiohttp`, `beautifulsoup4`, `requests`.
 
## Setup
 
```bash
git clone <this-repo-url>
cd web-scraper
uv sync
```
 
## Usage
 
```bash
uv run main.py <url> [max_concurrency] [max_pages]
```
 
| Argument | Required | Default | Description |
|---|---|---|---|
| `url` | yes | n/a | The website to crawl |
| `max_concurrency` | no | 5 | Maximum number of requests in flight at once |
| `max_pages` | no | 50 | Maximum number of pages to crawl |
 
Example:
 
```bash
uv run main.py https://example.com 3 25
```
 
This crawls `example.com` with at most 3 simultaneous requests, stopping after 25 pages. While it runs, it prints each page as it is crawled, then a summary of what it found. The full results are saved to `report.json`.
 
**Please crawl responsibly.** Only crawl sites you own or have permission to crawl, keep concurrency low, and respect the site's terms.
 
## Report format
 
`report.json` is a list of pages, sorted by URL. Each page looks like this:
 
```json
{
  "url": "https://example.com/about",
  "heading": "About Us",
  "first_paragraph": "We build things.",
  "outgoing_links": ["https://example.com/", "https://example.com/contact"],
  "image_urls": ["https://example.com/images/team.jpg"]
}
```
 
## Running the tests
 
```bash
uv run python -m unittest
```
 
## Project structure
 
| File | Purpose |
|---|---|
| `main.py` | Command-line entry point |
| `crawl.py` | URL normalization and HTML extraction functions |
| `async_crawler.py` | The `AsyncCrawler` class and `crawl_site_async` |
| `json_report.py` | Writes the JSON report |
| `test_crawl.py` | Unit tests |
 
## How it works
 
1. `main.py` reads the command-line arguments and starts `crawl_site_async`.
2. `AsyncCrawler` fetches the starting page and extracts its data.
3. Each link found on the page (on the same domain, not yet visited) gets its own task, run concurrently up to the concurrency limit.
4. The crawl stops when there are no more pages to visit or the page limit is reached.
5. The collected data is written to `report.json`.
