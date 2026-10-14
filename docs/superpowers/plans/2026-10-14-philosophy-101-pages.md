# Philosophy 101 GitHub Pages Implementation Plan

> **For agentic workers:** Implement this plan task-by-task in order. Each task includes exact files, interfaces, tests, and checkable steps. Steps use checkbox syntax for tracking.

**Goal:** Turn the existing ten-volume, 32-article Philosophy 101 repository into a welcoming, static, reader-first GitHub Pages site without rewriting the current articles.

**Architecture:** Use GitHub Pages' built-in Jekyll support from `main`/root. Keep the existing Markdown files as article sources, add front matter for page metadata, use shared layouts and a small volume data file, and publish ordinary base-path-aware HTML pages. Do not use a server, database, external build workflow, analytics, third-party fonts, or tracking scripts.

**Tech Stack:** GitHub Pages, Jekyll/Liquid, Kramdown, semantic HTML, CSS, Python 3 standard-library tests against `_site/`.

**Spec:** `docs/superpowers/specs/2026-10-14-philosophy-101-pages-design.md`

## Global Constraints

- Public site base path is `/philosophy-101/`.
- Preserve the existing ten volume folders and 32 article bodies; add only metadata needed to render them.
- Keep the site for curious beginners, using concise explanations, everyday examples, and reflection questions.
- Use paper `#F6F1E7`, ink `#24313F`, terracotta `#8B493A`, and muted blue `#315C7A`; maintain at least 4.5:1 contrast for normal text.
- Use `Georgia, "Times New Roman", serif` for display headings and `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` for body/navigation.
- Keep the article column narrow, readable, and phone-friendly.
- Use built-in GitHub Pages/Jekyll features and supported plugins only; publish from `main`/root.
- Do not add accounts, quizzes, course progress, comments, ads, analytics, remote fonts, or backend services.
- Do not merge to `main` or publish the implementation until the user approves the exact change set.

## Review Focus

- An article with missing or duplicate `title`, `volume_id`, or `order` metadata must fail validation rather than silently disappear or appear twice.
- The first and last articles in every volume must omit the unavailable previous/next link rather than link incorrectly.
- Directly loading or refreshing an interior URL under `/philosophy-101/` must work; internal links must not drop the repository base path.
- An article without a Reflection heading must still render its content and navigation without an invented prompt.
- Heading structure, contrast, keyboard focus, and navigation must remain usable at narrow phone widths and with a keyboard.

---

## File Structure

- `_config.yml` — site title, canonical URL, `/philosophy-101` base URL, Markdown settings, and build exclusions.
- `_data/volumes.yml` — ten ordered volume records with stable IDs, titles, slugs, short descriptions grounded in the README, and source folders.
- `_data/starting_questions.yml` — three simple reader questions mapped to existing article permalinks; no new article content.
- `_layouts/default.html` — document shell, metadata, skip link, shared header/footer, and stylesheet reference.
- `_layouts/home.html` — homepage composition and volume cards.
- `_layouts/volume.html` — volume heading and ordered article list.
- `_layouts/article.html` — article breadcrumb, body, Reflection styling, and previous/next links. Use the source Markdown's existing H1 as the sole visible page H1; the layout must not print a duplicate H1.
- `_includes/header.html` — site identity and library navigation.
- `_includes/footer.html` — compact repository link.
- `index.md` — homepage front matter and short introductory copy.
- `volumes/*.md` — ten metadata-only volume pages that select the volume layout and stable URL.
- `Vol-01-The-Toolbox/*.md` through `Vol-10-Meaning-of-Life/*.md` — existing article bodies plus YAML front matter (`title`, `description`, `volume_id`, `order`, `permalink`, `layout: article`).
- `assets/css/site.css` — responsive visual system, reading typography, focus states, and reduced-motion rules. Style the existing `### Reflection` heading and its immediately following paragraph using Kramdown's generated `id="reflection"`; do not duplicate or rewrite question text.
- `tests/__init__.py` — make the test directory importable by the standard library test runner.
- `tests/test_generated_site.py` — standard-library tests against generated HTML and the existing Markdown source set.
- `Gemfile` and `Gemfile.lock` — pin the currently supported `github-pages` gem version 232 for local build verification.
- `.gitignore` — exclude `_site/`, `.bundle/`, `vendor/bundle/`, `__pycache__/`, and `*.py[cod]` from commits.
- `README.md` — contributor instructions and the verified Pages URL while retaining the existing volume guide.

## Task 1: Jekyll Shell and Build Check

**Files:** Create `_config.yml`, `Gemfile`, `Gemfile.lock`, `.gitignore`, `_layouts/default.html`, `_includes/header.html`, `_includes/footer.html`, `assets/css/site.css`, `index.md`, `tests/__init__.py`, and `tests/test_generated_site.py`.

**Interfaces:** The default layout consumes `page.title`, `page.description`, `site.title`, `site.url`, and `site.baseurl`. It exposes a skip link, shared header/footer, and a stylesheet URL produced with Jekyll's `relative_url`. In `tests/test_generated_site.py`, define `read_site_file(relative_path: str) -> str`, `site_file_exists(url_or_relative_path: str) -> bool`, and `count_html_tags(html: str, tag: str) -> int`; the first two resolve paths under `_site/`. `site_file_exists` maps a raw Jekyll permalink such as `/reading/the-toolbox/logic-101-validity/` or deployed path `/philosophy-101/reading/the-toolbox/logic-101-validity/` to its `_site/.../index.html` output and also accepts a path such as `index.html`.

- [ ] **Step 1: Write the failing shell test**

  Create `tests/__init__.py` and `tests/test_generated_site.py`; import `unittest`, `Path`, and the helper functions. Add `class TestSiteShell(unittest.TestCase)` with `test_homepage_uses_shared_shell`, beginning with `self.assertTrue(site_file_exists("index.html"))` so the baseline failure is an assertion, then assert the generated page contains `lang="en"`, a viewport meta tag, one `main` landmark, a visible `skip-link`, a `site-header`, a `site-footer`, a page title, a meta description, and `/philosophy-101/assets/css/site.css`.

- [ ] **Step 2: Run the test and confirm the expected failure**

  Run `python3 -m unittest tests.test_generated_site.TestSiteShell.test_homepage_uses_shared_shell -v`.
  Expected before implementation: FAIL at the homepage-exists assertion because `_site/index.html` has not been generated.

- [ ] **Step 3: Add the minimal Jekyll configuration and pinned bundle**

  Set `url: https://melvinvarghese.github.io`, `baseurl: /philosophy-101`, and Kramdown as the Markdown engine. Add `gem "github-pages", "= 232"` to the Gemfile and resolve its lockfile.

- [ ] **Step 4: Implement the shared shell and placeholder homepage**

  Create semantic HTML with the agreed stable IDs/classes, skip link, `<header>`, `<main>`, `<footer>`, viewport metadata, title/description tags, and a base-path-aware stylesheet URL.

- [ ] **Step 5: Add responsive base styles**

  Define CSS custom properties `--paper: #F6F1E7`, `--ink: #24313F`, `--terracotta: #8B493A`, and `--blue: #315C7A`; use the global heading/body font stacks. Keep the reading column comfortable; add phone-width layout, visible keyboard focus, and reduced-motion handling. Do not request fonts or images from third-party hosts.

- [ ] **Step 6: Build and verify the shell test**

  Run `bundle install && bundle exec jekyll build && python3 -m unittest tests.test_generated_site.TestSiteShell -v`.
  Expected: PASS, with `_site/index.html` and `_site/assets/css/site.css` generated.

- [ ] **Step 7: Commit the shell task**

  Commit with message `feat: add Jekyll site shell`.

## Task 2: Homepage and Ten Volume Pages

**Files:** Create `_data/volumes.yml`, `_data/starting_questions.yml`, `_layouts/home.html`, `_layouts/volume.html`, and ten `volumes/*.md` pages; modify `index.md` and `tests/test_generated_site.py`.

**Interfaces:** Volume records use `id`, `title`, `slug`, `description`, and `source_dir`. `VOLUMES` defines these `(id, slug, source_dir)` records in order: `(vol-01-the-toolbox, the-toolbox, Vol-01-The-Toolbox)`, `(vol-02-metaphysics, metaphysics, Vol-02-Metaphysics)`, `(vol-03-epistemology, epistemology, Vol-03-Epistemology)`, `(vol-04-the-mind, the-mind, Vol-04-The-Mind)`, `(vol-05-ethics, ethics, Vol-05-Ethics)`, `(vol-06-politics, politics, Vol-06-Politics)`, `(vol-07-aesthetics, aesthetics, Vol-07-Aesthetics)`, `(vol-08-the-ancients, the-ancients, Vol-08-The-Ancients)`, `(vol-09-the-moderns, the-moderns, Vol-09-The-Moderns)`, `(vol-10-meaning-of-life, meaning-of-life, Vol-10-Meaning-of-Life)`. In `tests/test_generated_site.py`, define `VOLUME_SLUGS`, `VOLUME_IDS`, and `VOLUME_SOURCE_DIRS` as tuples matching those ordered records. Test helpers `volume_card_links(html: str) -> list[str]`, `question_path_links(html: str) -> list[str]`, `source_article_titles(source_dir: str) -> list[str]`, and `volume_article_titles(html: str) -> list[str]` parse expected/source and rendered order. The source helper reads top-level `.md` files sorted by their two-digit filename prefix and returns each existing first H1. The link helpers use Python's standard-library `html.parser`. Each volume page uses `layout: volume` and its matching `volume_id`. The volume layout consumes `site.pages | where: "layout", "article" | where: "volume_id", volume.id | sort: "order"`.

- [ ] **Step 1: Write the failing homepage and volume tests**

  Add `test_homepage_links_all_ten_volumes`, `test_homepage_links_to_existing_questions`, `test_volume_pages_exist_at_stable_urls`, and `test_each_volume_lists_articles_in_repository_order`.

  ```python
  class TestVolumeNavigation(unittest.TestCase):
      def test_homepage_links_all_ten_volumes(self):
          html = read_site_file("index.html")
          self.assertEqual(html.count('class="volume-card"'), 10)
          links = volume_card_links(html)
          self.assertEqual(len(links), 10)
          self.assertEqual(len(set(links)), 10)
          self.assertIn('/philosophy-101/volumes/the-toolbox/', links)

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

      def test_each_volume_lists_articles_in_repository_order(self):
          for (slug, source_dir) in zip(VOLUME_SLUGS, VOLUME_SOURCE_DIRS):
              html = read_site_file(f"volumes/{slug}/index.html")
              self.assertEqual(volume_article_titles(html), source_article_titles(source_dir))
  ```

- [ ] **Step 2: Run the focused tests and confirm the expected failure**

  Run `bundle exec jekyll build && python3 -m unittest tests.test_generated_site.TestVolumeNavigation -v`.
  Expected before implementation: volume metadata and stable routes are absent.

- [ ] **Step 3: Add ordered volume metadata and metadata-only pages**

  Add all ten current volume IDs, names, slugs, brief descriptions, and source directories using the current README text verbatim: The Toolbox — “Start here. Logic, arguing, and how to think.”; Metaphysics — “The weird stuff. God, simulations, and reality.”; Epistemology — “Knowledge. Truth, science, and skepticism.”; The Mind — “Consciousness, AI, and the Self.”; Ethics — “Right, wrong, and the gray areas.”; Politics — “Power, justice, and freedom.”; Aesthetics — “Art, beauty, and horror.”; The Ancients — “Where it all began (Greeks, Romans, etc.).”; The Moderns — “The thinkers who built the modern world.”; The Search for Meaning — “Existentialism, Nihilism, and Eastern Wisdom.” Add three reader-question records linking only to the existing determinism/free-will, Gettier-problem, and meaning-of-life articles. Create one page per volume with a stable permalink under `/volumes/<slug>/`.

- [ ] **Step 4: Build the homepage and volume contents layout**

  Render the approved concise introduction, a prominent “Start with the Toolbox” link, the three question-based entry links, and ten volume cards. Render each volume's ordered article list from article metadata; do not copy article bodies into the data file.

- [ ] **Step 5: Rebuild and verify all volume tests**

  Run `bundle exec jekyll build && python3 -m unittest tests.test_generated_site.TestVolumeNavigation -v`.
  Expected: PASS for ten volume routes, ten unique cards, and ordered contents.

- [ ] **Step 6: Commit the library-navigation task**

  Commit with message `feat: add philosophy volume navigation`.

## Task 3: Article Rendering and Reading Navigation

**Files:** Create `_layouts/article.html`; add front matter to all 32 existing article files across the ten volume folders; modify `tests/test_generated_site.py`.

**Interfaces:** Each article page exposes `title`, `description`, `volume_id`, sequential `order`, and `permalink`; the article layout selects adjacent pages with the same `volume_id`, omitting previous/next links when no adjacent page exists. Each generated article uses `<article class="reading-article" data-volume-id="..." data-order="...">`. Test helpers expose `article_source_files() -> list[Path]`, `generated_article_pages() -> list[ArticleRecord]`, `article_pages_for_volume(volume_id: str) -> list[ArticleRecord]`, `article_heading(path: Path) -> str`, `read_site_page(url_path: str) -> str`, `site_url(permalink: str) -> str`, and `article_link_href(html: str, class_name: str) -> str | None`. `generated_article_pages` reads the 32 generated `reading/**/index.html` files using their single H1, description meta tag, article data attributes, and output path; no YAML parser is needed. `ArticleRecord` has `title: str`, `description: str`, `volume_id: str`, `order: int`, and `permalink: str`; `read_site_page` resolves a route under `_site/` and reads its `index.html`.

- [ ] **Step 1: Write the failing article tests**

  Add `test_all_32_articles_render_from_existing_sources`, `test_article_metadata_is_complete_and_unique`, `test_article_titles_match_existing_headings`, `test_article_has_one_h1`, `test_article_layout_shows_breadcrumb_and_reflection`, `test_article_without_reflection_renders_normally`, and `test_previous_next_stay_within_volume`.

  ```python
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
          source_titles = {article_heading(path) for path in article_source_files()}
          generated_titles = {record.title for record in generated_article_pages()}
          self.assertEqual(generated_titles, source_titles)

      def test_article_has_one_h1(self):
          for page in generated_article_pages():
              html = read_site_page(page.permalink)
              self.assertEqual(count_html_tags(html, "h1"), 1)

      def test_article_layout_shows_breadcrumb_and_reflection(self):
          html = read_site_page("/reading/the-toolbox/logic-101-validity/")
          self.assertIn('class="breadcrumb"', html)
          self.assertIn('id="reflection"', html)
          self.assertIn("Is their logic broken, or are their facts wrong?", html)

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
  ```

- [ ] **Step 2: Run focused tests and confirm the expected failure**

  Run `bundle exec jekyll build && python3 -m unittest tests.test_generated_site.TestArticlePages -v`.
  Expected before implementation: article pages have no Jekyll layout metadata, and generated reading routes do not exist.

- [ ] **Step 3: Add article front matter without editing prose**

  For each file, add front matter containing the exact existing H1 title, a unique meta description based on the article's opening explanation, matching volume ID, `order` equal to the numeric filename prefix (01, 02, ...), `layout: article`, and a stable `/reading/<volume-slug>/<article-slug>/` permalink. Derive `article-slug` from the filename by removing its two-digit prefix and `.md`. Preserve all article body text; review the diff to confirm the change is limited to front matter.

- [ ] **Step 4: Implement article content and navigation**

  Render the volume breadcrumb, Markdown body, and previous/next links. Treat the article body's existing H1 as the page heading; the article layout must not add another H1. Style the Kramdown-generated `h3#reflection` and its next paragraph as the reflection callout, which naturally omits the callout when a source has no Reflection section.

- [ ] **Step 5: Rebuild and verify the article tests**

  Run `bundle exec jekyll build && python3 -m unittest tests.test_generated_site.TestArticlePages -v`.
  Expected: PASS for all 32 generated articles, existing titles/body, reflection presence where present, and volume-local navigation boundaries.

- [ ] **Step 6: Commit the article-reading task**

  Commit with message `feat: render philosophy articles for reading`.

## Task 4: Metadata, Accessibility, and Release Check

**Files:** Modify `_layouts/default.html`, `_layouts/home.html`, `_layouts/volume.html`, `_layouts/article.html`, `assets/css/site.css`, `README.md`, and `tests/test_generated_site.py`.

**Interfaces:** Every page supplies a nonempty title and description. Site/assets links use `relative_url`; canonical URLs use `absolute_url`. Test helpers expose `library_html_pages() -> list[Path]`, `page_title(path: Path) -> str`, `page_description(path: Path) -> str`, `local_links(path: Path) -> list[str]` (exclude external, `mailto:`, `tel:`, and fragment-only links), `local_fragments(path: Path) -> list[str]`, `element_ids(path: Path) -> set[str]`, `target_exists_in_site(href: str) -> bool`, `css_color(name: str) -> tuple[int, int, int]`, and `contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> float`; parse anchors using Python's standard-library `html.parser`.

- [ ] **Step 1: Write failing metadata, link, and accessibility tests**

  Add `test_every_library_page_has_title_and_description`, `test_internal_links_resolve_under_baseurl`, `test_in_page_fragments_resolve`, `test_shell_has_skip_link_landmarks_and_focus_style`, and `test_no_tracking_or_remote_font_requests`.

  ```python
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
                  self.assertTrue(href.startswith("/philosophy-101/"), href)
                  self.assertTrue(target_exists_in_site(href), href)

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
  ```

- [ ] **Step 2: Run tests and confirm the expected failure**

  Run `bundle exec jekyll build && python3 -m unittest tests.test_generated_site.TestSiteQuality -v`.
  Expected before implementation: missing per-page descriptions, unverified local links, or missing accessibility selectors cause failures.

- [ ] **Step 3: Add page-specific metadata and finish base-path links**

  Add concise descriptions grounded in actual page content, canonical URLs, and Open Graph title/description/URL fields. Use Jekyll URL filters for all internal links.

- [ ] **Step 4: Finish visual and keyboard polish**

  Verify contrast, keyboard focus, narrow-screen reflow, readable line length, and the reflection callout. Do not add unapproved features or external dependencies.

- [ ] **Step 5: Update contributor README and run full checks**

  Add local preview/build instructions and the verified Pages URL while preserving the existing volume guide. Run `bundle exec jekyll build`, `python3 -m unittest tests.test_generated_site -v`, and `git diff --check`.
  Expected: all 10 volumes and 32 articles generate; internal links resolve; every test passes; no whitespace errors remain.

  Start a local preview with `bundle exec jekyll serve --baseurl /philosophy-101`. At `http://127.0.0.1:4000/philosophy-101/`, verify the homepage, one volume page, first/middle/last article pages, and direct refresh of an interior route at 390px and 1440px viewport widths. Expected: navigation stays within `/philosophy-101/`, the page is readable and keyboard-operable, and no image, font, analytics, or tracking request is made.

- [ ] **Step 6: Commit final QA task**

  Commit with message `chore: verify Philosophy 101 Pages site`.

- [ ] **Step 7: Prepare the change set for user review**

  Summarize the branch diff and preview results. Do not merge to `main` or publish the implementation until the user approves the exact change set.

## Local Verification Commands

```bash
bundle exec jekyll build
python3 -m unittest tests.test_generated_site -v
git diff --check
```

## Publication Gate

GitHub Pages currently publishes from `main`/root. The feature branch can be built and previewed locally; merging it to `main` will make the new site public. Before that merge, show the user the reviewed change set and get approval to publish.
