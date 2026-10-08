import unittest
from crawl import (
    get_first_paragraph_from_html, get_heading_from_html,
    get_images_from_html, normalize_url, get_urls_from_html,
    extract_page_data
)

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        actual = normalize_url("https://www.boot.dev/blog/path")
        self.assertEqual(actual, "www.boot.dev/blog/path")

    def test_normalize_url_slash(self):
        actual = normalize_url("https://www.boot.dev/blog/path/")
        self.assertEqual(actual, "www.boot.dev/blog/path")

    def test_normalize_url_http(self):
        actual = normalize_url("http://www.boot.dev/blog/path")
        self.assertEqual(actual, "www.boot.dev/blog/path")

    def test_normalize_url_uppercase(self):
        actual = normalize_url("HTTPS://WWW.BOOT.DEV/BLOG/PATH")
        self.assertEqual(actual, "www.boot.dev/blog/path")

    def test_normalize_url_not_path(self):
        actual = normalize_url("https://www.boot.dev")
        self.assertEqual(actual, "www.boot.dev")

    def test_normalize_url_fragment(self):
        actual = normalize_url("https://www.boot.dev/blog/path#comments")
        self.assertEqual(actual, "www.boot.dev/blog/path")

    def test_normalize_url_query_string(self):
        actual = normalize_url("https://www.boot.dev/blog?page=2")
        self.assertEqual(actual, "www.boot.dev/blog")

    def test_normalize_url_port(self):
        actual = normalize_url("https://www.boot.dev:8080/blog")
        self.assertEqual(actual, "www.boot.dev:8080/blog")

    def test_normalize_url_multiple_trailing_slashes(self):
        actual = normalize_url("https://www.boot.dev/blog//")
        self.assertEqual(actual, "www.boot.dev/blog")

    def test_normalize_url_no_www_stays_different(self):
        actual = normalize_url("https://boot.dev/blog")
        self.assertEqual(actual, "boot.dev/blog")

    def test_get_heading_from_html_h1(self):
        html = "<html><body><h1>Test Title</h1></body></html>"
        self.assertEqual(get_heading_from_html(html),"Test Title")

    def test_get_heading_from_html_h2_fallback(self):
        html = "<html><body><h2>Subtitle</h2></body></html>"
        self.assertEqual(get_heading_from_html(html), "Subtitle")

    def test_get_heading_from_html_prefers_h2(self):
        html = "<body><h2>Second</h2><h1>First</h1></body>"
        self.assertEqual(get_heading_from_html(html),"First")

    def test_get_heading_from_html_none(self):
        html = "<html><body><p>No headings here</p></body></html>"
        self.assertEqual(get_heading_from_html(html), "")

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_main(self):
            # fallback: no <main>, so use the first <p> anywhere
            input_body = """<html><body>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </body></html>"""
            self.assertEqual(
                get_first_paragraph_from_html(input_body), "First paragraph."
            )

    def test_get_first_paragraph_from_html_no_paragraph(self):
            input_body = "<html><body><h1>Title</h1></body></html>"
            self.assertEqual(get_first_paragraph_from_html(input_body), "")

    def test_get_first_paragraph_from_html_main_multiple_paragraphs(self):
            # only the FIRST <p> inside <main>
            input_body = """<html><body>
                <main>
                    <p>Main one.</p>
                    <p>Main two.</p>
                </main>
            </body></html>"""
            self.assertEqual(
                get_first_paragraph_from_html(input_body), "Main one."
            )

    def test_get_first_paragraph_from_html_main_without_paragraph(self):
            # decision: <main> exists but has no <p>, so fall back to the first <p> in the page
            input_body = """<html><body>
                <p>Outside paragraph.</p>
                <main><h2>No paragraph here</h2></main>
            </body></html>"""
            self.assertEqual(
                get_first_paragraph_from_html(input_body), "Outside paragraph."
            )

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
            input_url = "https://crawler-test.com"
            input_body = '<html><body><a href="/blog/post"><span>Post</span></a></body></html>'
            actual = get_urls_from_html(input_body, input_url)
            expected = ["https://crawler-test.com/blog/post"]
            self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple_links(self):
            input_url = "https://crawler-test.com"
            input_body = """<html><body>
                <a href="https://crawler-test.com/one">One</a>
                <a href="/two">Two</a>
                <a href="/three">Three</a>
            </body></html>"""
            actual = get_urls_from_html(input_body, input_url)
            expected = [
                "https://crawler-test.com/one",
                "https://crawler-test.com/two",
                "https://crawler-test.com/three",
            ]
            self.assertEqual(actual, expected)

    def test_get_urls_from_html_mixed_absolute_and_relative(self):
            input_url = "https://crawler-test.com"
            input_body = '<a href="/local">Local</a><a href="https://other.com/page">Other</a>'
            actual = get_urls_from_html(input_body, input_url)
            expected = ["https://crawler-test.com/local", "https://other.com/page"]
            self.assertEqual(actual, expected)

    def test_get_urls_from_html_no_links(self):
            input_body = "<html><body><p>No links here</p></body></html>"
            actual = get_urls_from_html(input_body, "https://crawler-test.com")
            self.assertEqual(actual, [])

    def test_get_urls_from_html_anchor_without_href(self):
        # decision: <a> tags with no href are skipped
        input_body = '<a name="top">Top</a><a href="/real">Real</a>'
        actual = get_urls_from_html(input_body, "https://crawler-test.com")
        self.assertEqual(actual, ["https://crawler-test.com/real"])

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
            input_url = "https://crawler-test.com"
            input_body = '<img src="https://cdn.example.com/pic.jpg" alt="Pic">'
            actual = get_images_from_html(input_body, input_url)
            self.assertEqual(actual, ["https://cdn.example.com/pic.jpg"])

    def test_get_images_from_html_multiple_images(self):
            input_url = "https://crawler-test.com"
            input_body = """<html><body>
                <img src="/one.png" alt="One">
                <img src="/images/two.jpg" alt="Two">
                <img src="https://other.com/three.gif" alt="Three">
            </body></html>"""
            actual = get_images_from_html(input_body, input_url)
            expected = [
                "https://crawler-test.com/one.png",
                "https://crawler-test.com/images/two.jpg",
                "https://other.com/three.gif",
            ]
            self.assertEqual(actual, expected)

    def test_get_images_from_html_missing_alt(self):
            # alt is optional, so the image should still be found
            input_body = '<img src="/no-alt.png">'
            actual = get_images_from_html(input_body, "https://crawler-test.com")
            self.assertEqual(actual, ["https://crawler-test.com/no-alt.png"])

    def test_get_images_from_html_missing_src(self):
            # decision: an <img> with no src is skipped
            input_body = '<img alt="Broken"><img src="/ok.png" alt="OK">'
            actual = get_images_from_html(input_body, "https://crawler-test.com")
            self.assertEqual(actual, ["https://crawler-test.com/ok.png"])

    def test_get_images_from_html_no_images(self):
            input_body = "<html><body><p>No images here</p></body></html>"
            actual = get_images_from_html(input_body, "https://crawler-test.com")
            self.assertEqual(actual, [])

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty_page(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links_and_images(self):
        input_url = "https://crawler-test.com/blog"
        input_body = """<html><body>
            <h1>Blog</h1>
            <p>Welcome.</p>
            <a href="/one">One</a>
            <a href="https://other.com/two">Two</a>
            <img src="/a.png" alt="A">
            <img src="https://cdn.example.com/b.jpg" alt="B">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com/blog",
            "heading": "Blog",
            "first_paragraph": "Welcome.",
            "outgoing_links": [
                "https://crawler-test.com/one",
                "https://other.com/two",
            ],
            "image_urls": [
                "https://crawler-test.com/a.png",
                "https://cdn.example.com/b.jpg",
            ],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_fallbacks(self):
        # h2 used when there's no h1, and <main> paragraph preferred
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h2>Subheading</h2>
            <p>Outside paragraph.</p>
            <main><p>Main paragraph.</p></main>
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(actual["heading"], "Subheading")
        self.assertEqual(actual["first_paragraph"], "Main paragraph.")

    def test_extract_page_data_relative_resolution_uses_page_url(self):
        input_url = "https://crawler-test.com"
        input_body = '<a href="/x">X</a><img src="/y.png">'
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(actual["outgoing_links"], ["https://crawler-test.com/x"])
        self.assertEqual(actual["image_urls"], ["https://crawler-test.com/y.png"])

if __name__ == "__main__":
    unittest.main()
