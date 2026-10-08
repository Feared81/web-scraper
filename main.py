import sys
import asyncio
from async_crawler import crawl_site_async


async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    print(f"starting crawl of: {base_url}")
    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)

    print(f"\nNumber of pages found: {len(page_data)}")
    for page in page_data.values():
        print(f"- {page['url']}")
        print(f"    heading: {page['heading']}")
        print(f"    links: {len(page['outgoing_links'])}, images: {len(page['image_urls'])}")


if __name__ == "__main__":
    asyncio.run(main())
