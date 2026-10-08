import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

from requests.compat import urlsplit

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def normalize_url(url: str) -> str:
    parts = urlparse(url)
    normalized = parts.netloc + parts.path
    return normalized.rstrip("/").lower()

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def get_first_paragraph_from_html(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        p_tag = None
        main_tag = soup.find("main")
        if main_tag is not None:
            p_tag = main_tag.find("p")
        if p_tag is None:
            p_tag = soup.find("p")
        return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

def get_urls_from_html(html, base_url) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    link_list = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if isinstance(href, str):
            url = urljoin(base_url, href)
            link_list.append(url)
    return link_list

def get_images_from_html(html, base_url) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    link_list = []
    for link in soup.find_all('img'):
        src = link.get('src')
        if isinstance(src, str):
            url = urljoin(base_url, src)
            link_list.append(url)
    return link_list

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }

def get_html(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "BootCrawler/1.0 (learning project)"},
        timeout=20,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"HTTP error: {response.status_code}")

    content_type = response.headers.get("content-type","")
    if "text/html" not in content_type:
        raise RuntimeError(f"Unexpected content type: {content_type}")

    return response.text

def crawl_page(base_url: str, current_url: str | None = None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    base_url_obj = urlsplit(base_url)
    current_url_obj = urlsplit(current_url)
    if current_url_obj.netloc != base_url_obj.netloc:
        return page_data

    norm_current_url = normalize_url(current_url)

    if norm_current_url in page_data:
        return page_data

    print(f"Crawling: {current_url}")
    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"Error fetching {current_url}: {e}")
        return page_data

    page_data[norm_current_url] = extract_page_data(html, current_url)

    for link in page_data[norm_current_url]['outgoing_links']:
        crawl_page(base_url, link, page_data)

    return page_data
