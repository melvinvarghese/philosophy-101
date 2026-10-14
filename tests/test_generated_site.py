from pathlib import Path
from html.parser import HTMLParser
from dataclasses import dataclass
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


class ArticleTitleCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag != "span":
            return
        attributes = dict(attrs)
        if "article-link__title" in attributes.get("class", "").split():
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.current is not None:
            self.titles.append("".join(self.current).strip())
            self.current = None


def volume_article_titles(html: str) -> list[str]:
    parser = ArticleTitleCollector()
    parser.feed(html)
    return parser.titles


def normalize_smart_quotes(text: str) -> str:
    return text.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))


def article_source_files() -> list[Path]:
    return sorted(Path().glob("Vol-*/[0-9][0-9]-*.md"))


def article_heading(path: Path) -> str:
    match = re.search(r"^# (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else ""


@dataclass(frozen=True)
class ArticleRecord:
    title: str
    description: str
    volume_id: str
    order: int
    permalink: str


class ArticleMetadataReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts = []
        self.title = ""
        self.description = ""
        self.volume_id = ""
        self.order = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta" and attributes.get("name") == "description":
            self.description = attributes.get("content", "")
        elif tag == "article" and "reading-article" in attributes.get("class", "").split():
            self.volume_id = attributes.get("data-volume-id", "")
            try:
                self.order = int(attributes.get("data-order", "0"))
            except ValueError:
                self.order = 0
        elif tag == "h1":
            self.in_title = True

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "h1" and self.in_title:
            self.title = "".join(self.title_parts).strip()
            self.in_title = False


def generated_article_pages() -> list[ArticleRecord]:
    records = []
    for html_path in sorted(SITE_ROOT.glob("reading/**/index.html")):
        parser = ArticleMetadataReader()
        parser.feed(html_path.read_text(encoding="utf-8"))
        relative = html_path.relative_to(SITE_ROOT).as_posix()
        permalink = "/" + relative.removeprefix("reading/").removesuffix("/index.html")
        permalink = "/reading/" + permalink.removeprefix("/") + "/"
        records.append(ArticleRecord(
            title=parser.title,
            description=parser.description,
            volume_id=parser.volume_id,
            order=parser.order,
            permalink=permalink,
        ))
    return records


def article_pages_for_volume(volume_id: str) -> list[ArticleRecord]:
    return sorted((page for page in generated_article_pages() if page.volume_id == volume_id), key=lambda page: page.order)


def read_site_page(url_path: str) -> str:
    output = site_output_path(url_path)
    return output.read_text(encoding="utf-8") if output and output.is_file() else ""


def site_url(permalink: str) -> str:
    return f"{SITE_BASEURL}{permalink}"


class DocumentMetadataReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.in_title = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attributes.get("name") == "description":
            self.description = attributes.get("content", "")

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self.in_title:
            self.title = "".join(self.title_parts).strip()
            self.in_title = False


class AnchorCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href is not None:
                self.hrefs.append(href)


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        element_id = dict(attrs).get("id")
        if element_id:
            self.ids.add(element_id)


def library_html_pages() -> list[Path]:
    return sorted(path for path in SITE_ROOT.rglob("*.html") if path.is_file())


def page_title(path: Path) -> str:
    parser = DocumentMetadataReader()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.title


def page_description(path: Path) -> str:
    parser = DocumentMetadataReader()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.description


def local_links(path: Path) -> list[str]:
    parser = AnchorCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    links = []
    for href in parser.hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or parsed.path.startswith("mailto:") or parsed.path.startswith("tel:"):
            continue
        if parsed.path or not parsed.fragment:
            links.append(href)
    return links


def local_fragments(path: Path) -> list[str]:
    parser = AnchorCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    fragments = []
    for href in parser.hrefs:
        parsed = urlsplit(href)
        if parsed.fragment and not parsed.scheme and not parsed.netloc and not parsed.path:
            fragments.append(parsed.fragment)
    return fragments


def element_ids(path: Path) -> set[str]:
    parser = IdCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.ids


def target_exists_in_site(href: str) -> bool:
    path = urlsplit(href).path
    if path == SITE_BASEURL:
        path = "/"
    elif path.startswith(f"{SITE_BASEURL}/"):
        path = path[len(SITE_BASEURL):]
    elif path.startswith("/"):
        return False
    output = (SITE_ROOT / path.lstrip("/")).resolve()
    if output != SITE_ROOT.resolve() and SITE_ROOT.resolve() not in output.parents:
        return False
    if path.endswith("/") or output.is_dir():
        output /= "index.html"
    return output.is_file()


def css_color(name: str) -> tuple[int, int, int]:
    css = read_site_file("assets/css/site.css")
    match = re.search(rf"--{re.escape(name)}\s*:\s*#([0-9a-fA-F]{{6}})", css)
    if not match:
        raise AssertionError(f"CSS custom property --{name} is missing or not a six-digit hex color")
    value = match.group(1)
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> float:
    def luminance(color):
        channels = []
        for component in color:
            channel = component / 255
            channels.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def article_link_href(html: str, class_name: str) -> str | None:
    links = classed_links(html, class_name)
    return links[0]["href"] if links else None


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

    def test_homepage_volume_numbers_are_two_digits(self):
        html = read_site_file("index.html")
        numbers = re.findall(r'<span class="volume-card__number">([^<]+)</span>', html)
        self.assertEqual(numbers, [f"Volume {number:02d}" for number in range(1, 11)])

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


class TestArticlePages(unittest.TestCase):
    def test_all_32_articles_render_from_existing_sources(self):
        sources = article_source_files()
        generated = generated_article_pages()
        self.assertEqual(len(sources), 32)
        self.assertEqual(len(generated), 32)
        for page in generated:
            self.assertTrue(site_file_exists(page.permalink))
            self.assertIn(page.title, read_site_page(page.permalink))

    def test_article_metadata_is_complete_and_unique(self):
        records = generated_article_pages()
        self.assertEqual(len(records), 32)
        self.assertTrue(all(record.title and record.permalink and record.volume_id in VOLUME_IDS and record.order > 0 for record in records))
        self.assertEqual(len({record.permalink for record in records}), 32)
        self.assertEqual(len({(record.volume_id, record.order) for record in records}), 32)
        self.assertTrue(all(record.description for record in records))
        self.assertEqual(len({record.description for record in records}), 32)
        for record in records:
            html = read_site_page(record.permalink)
            self.assertIn('class="reading-article"', html)
            self.assertIn(f'data-volume-id="{record.volume_id}"', html)
            self.assertIn(f'data-order="{record.order}"', html)

    def test_article_titles_match_existing_headings(self):
        source_titles = {normalize_smart_quotes(article_heading(path)) for path in article_source_files()}
        generated_titles = {normalize_smart_quotes(record.title) for record in generated_article_pages()}
        self.assertEqual(generated_titles, source_titles)

    def test_article_has_one_h1(self):
        for page in generated_article_pages():
            html = read_site_page(page.permalink)
            self.assertEqual(count_html_tags(html, "h1"), 1)

    def test_article_layout_shows_breadcrumb_and_reflection(self):
        html = read_site_page("/reading/the-toolbox/logic-101-validity/")
        self.assertIn('class="breadcrumb"', html)
        self.assertIn('id="reflection"', html)
        self.assertIn('Is their logic broken, or are their facts wrong?', html)

    def test_article_without_reflection_renders_normally(self):
        html = read_site_page("/reading/the-toolbox/logical-fallacies/")
        self.assertIn("Ad Hominem", html)
        self.assertNotIn('id="reflection"', html)

    def test_previous_next_stay_within_volume(self):
        for volume_id in VOLUME_IDS:
            pages = article_pages_for_volume(volume_id)
            for index, page in enumerate(pages):
                html = read_site_page(page.permalink)
                previous = article_link_href(html, "previous-article")
                next_page = article_link_href(html, "next-article")
                expected_previous = None if index == 0 else site_url(pages[index - 1].permalink)
                expected_next = None if index == len(pages) - 1 else site_url(pages[index + 1].permalink)
                self.assertEqual(previous, expected_previous)
                self.assertEqual(next_page, expected_next)

    def test_each_volume_lists_articles_in_repository_order(self):
        for slug, source_dir in zip(VOLUME_SLUGS, VOLUME_SOURCE_DIRS):
            html = read_site_file(f"volumes/{slug}/index.html")
            self.assertEqual(volume_article_titles(html), source_article_titles(source_dir))


class TestSiteQuality(unittest.TestCase):
    def test_every_library_page_has_title_and_description(self):
        pages = library_html_pages()
        titles = [page_title(page) for page in pages]
        descriptions = [page_description(page) for page in pages]
        self.assertTrue(all(titles))
        self.assertEqual(len(titles), len(set(titles)))
        self.assertTrue(all(descriptions))
        self.assertEqual(len(descriptions), len(set(descriptions)))
        for page in pages:
            html = page.read_text(encoding="utf-8")
            self.assertIn('rel="canonical"', html)
            self.assertIn('property="og:title"', html)
            self.assertIn('property="og:description"', html)
            self.assertIn('property="og:url"', html)

    def test_internal_links_resolve_under_baseurl(self):
        for page in library_html_pages():
            for href in local_links(page):
                self.assertTrue(href.startswith(f"{SITE_BASEURL}/"), href)
                self.assertTrue(target_exists_in_site(href), href)

    def test_every_page_has_one_primary_heading(self):
        for page in library_html_pages():
            self.assertEqual(count_html_tags(page.read_text(encoding="utf-8"), "h1"), 1, str(page))

    def test_in_page_fragments_resolve(self):
        for page in library_html_pages():
            ids = element_ids(page)
            for fragment in local_fragments(page):
                self.assertIn(fragment, ids, f"{page}: #{fragment}")

    def test_shell_has_skip_link_landmarks_and_focus_style(self):
        html = read_site_file("index.html")
        css = read_site_file("assets/css/site.css")
        self.assertIn('class="skip-link"', html)
        self.assertIn("<main", html)
        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        paper = css_color("paper")
        self.assertGreaterEqual(contrast_ratio(css_color("ink"), paper), 4.5)
        self.assertGreaterEqual(contrast_ratio(css_color("quiet-ink"), paper), 4.5)
        self.assertGreaterEqual(contrast_ratio(css_color("terracotta"), paper), 4.5)
        self.assertGreaterEqual(contrast_ratio(css_color("blue"), paper), 4.5)

    def test_no_tracking_or_remote_font_requests(self):
        for page in library_html_pages():
            content = page.read_text(encoding="utf-8")
            self.assertNotIn("googletagmanager.com", content)
            self.assertNotIn("google-analytics.com", content)
            self.assertNotIn("fonts.googleapis.com", content)
        css = read_site_file("assets/css/site.css")
        self.assertNotIn("fonts.googleapis.com", css)


if __name__ == "__main__":
    unittest.main()
