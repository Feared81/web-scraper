import sys
from crawl import crawl_page


def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)

    base_url = sys.argv[1]
    print(f"starting crawl of: {base_url}")
    page_data = crawl_page(base_url)

    print(f"\nNumber of pages found: {len(page_data)}")
    for page in page_data.values():
        print(f"- {page['url']}")
        print(f"    heading: {page['heading']}")
        print(f"    links: {len(page['outgoing_links'])}, images: {len(page['image_urls'])}")



if __name__ == "__main__":
    main()
