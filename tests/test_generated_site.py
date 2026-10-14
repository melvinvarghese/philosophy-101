from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import unittest


SITE_ROOT = Path(__file__).resolve().parents[1] / "_site"
SITE_BASEURL = "/philosophy-101"


def site_output_path(url_or_relative_path: str) -> Path | None:
    path = urlsplit(url_or_relative_path).path
    if path == SITE_BASEURL:
        path = "/"
    elif path.startswith(f"{SITE_BASEURL}/"):
        path = path[len(SITE_BASEURL):]
    path = path.lstrip("/")
    output = (SITE_ROOT / path).resolve()
    if output != SITE_ROOT.resolve() and SITE_ROOT.resolve() not in output.parents:
        return None
    if urlsplit(url_or_relative_path).path.endswith("/") or output.is_dir():
        output /= "index.html"
    return output


def read_site_file(relative_path: str) -> str:
    output = site_output_path(relative_path)
    if output is None:
        raise ValueError(f"Path is outside the generated site: {relative_path}")
    return output.read_text(encoding="utf-8")


def site_file_exists(url_or_relative_path: str) -> bool:
    output = site_output_path(url_or_relative_path)
    return output is not None and output.is_file()


def count_html_tags(html: str, tag: str) -> int:
    class Counter(HTMLParser):
        def __init__(self):
            super().__init__()
            self.count = 0

        def handle_starttag(self, tag_name, attrs):
            if tag_name == tag:
                self.count += 1

    parser = Counter()
    parser.feed(html)
    return parser.count


class TestSiteShell(unittest.TestCase):
    def test_site_file_exists_accepts_raw_and_deployed_paths(self):
        self.assertTrue(site_file_exists("/assets/css/site.css"))
        self.assertTrue(site_file_exists("/philosophy-101/assets/css/site.css"))

    def test_homepage_uses_shared_shell(self):
        self.assertTrue(site_file_exists("index.html"))
        html = read_site_file("index.html")
        self.assertIn('lang="en"', html)
        self.assertIn('name="viewport"', html)
        self.assertEqual(count_html_tags(html, "main"), 1)
        self.assertIn('class="skip-link"', html)
        self.assertIn('class="site-header"', html)
        self.assertIn('class="site-footer"', html)
        self.assertIn("<title>", html)
        self.assertIn('name="description"', html)
        self.assertIn('/philosophy-101/assets/css/site.css', html)


if __name__ == "__main__":
    unittest.main()
