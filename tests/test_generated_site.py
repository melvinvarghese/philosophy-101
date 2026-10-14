from pathlib import Path
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit
import unittest


SITE_ROOT = Path(__file__).resolve().parents[1] / "_site"
SITE_BASEURL = "/philosophy-101"
VOLUME_SLUGS = (
    "the-toolbox", "metaphysics", "epistemology", "the-mind", "ethics",
    "politics", "aesthetics", "the-ancients", "the-moderns", "meaning-of-life",
)
VOLUME_IDS = tuple(f"vol-{index:02d}-{slug}" for index, slug in enumerate(VOLUME_SLUGS, start=1))
VOLUME_SOURCE_DIRS = (
    "Vol-01-The-Toolbox", "Vol-02-Metaphysics", "Vol-03-Epistemology",
    "Vol-04-The-Mind", "Vol-05-Ethics", "Vol-06-Politics",
    "Vol-07-Aesthetics", "Vol-08-The-Ancients", "Vol-09-The-Moderns",
    "Vol-10-Meaning-of-Life",
)


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


class ClassedLinkCollector(HTMLParser):
    def __init__(self, class_name: str):
        super().__init__()
        self.class_name = class_name
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag != "a" or self.current is not None:
            return
        attributes = dict(attrs)
        if self.class_name in attributes.get("class", "").split():
            self.current = {"href": attributes.get("href", ""), "text": ""}

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current)
            self.current = None


def classed_links(html: str, class_name: str) -> list[dict[str, str]]:
    parser = ClassedLinkCollector(class_name)
    parser.feed(html)
    return parser.links


def volume_card_links(html: str) -> list[str]:
    return [link["href"] for link in classed_links(html, "volume-card")]


def question_path_links(html: str) -> list[str]:
    return [link["href"] for link in classed_links(html, "question-link")]


def source_article_titles(source_dir: str) -> list[str]:
    files = sorted(Path(source_dir).glob("*.md"), key=lambda path: int(path.name[:2]))
    titles = []
    for path in files:
        match = re.search(r"^# (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            titles.append(match.group(1))
    return titles


def volume_article_titles(html: str) -> list[str]:
    return [link["text"].strip() for link in classed_links(html, "article-link")]


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


class TestVolumeNavigation(unittest.TestCase):
    def test_homepage_links_all_ten_volumes(self):
        html = read_site_file("index.html")
        self.assertEqual(len(volume_card_links(html)), 10)
        self.assertEqual(len(set(volume_card_links(html))), 10)
        self.assertEqual(
            volume_card_links(html),
            [f"/philosophy-101/volumes/{slug}/" for slug in VOLUME_SLUGS],
        )

    def test_homepage_links_to_existing_questions(self):
        html = read_site_file("index.html")
        links = question_path_links(html)
        self.assertEqual(len(links), 3)
        self.assertIn('/philosophy-101/reading/metaphysics/determinism-vs-free-will/', links)
        self.assertIn('/philosophy-101/reading/epistemology/the-gettier-problem/', links)
        self.assertIn('/philosophy-101/reading/meaning-of-life/the-meaning-of-life/', links)

    def test_volume_pages_exist_at_stable_urls(self):
        missing = [slug for slug in VOLUME_SLUGS if not site_file_exists(f"volumes/{slug}/index.html")]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
