# Philosophy 101 — GitHub Pages Reading Library

**Status:** Approved for implementation
**Date:** 2026-10-14<br>
**Repository:** [melvinvarghese/philosophy-101](https://github.com/melvinvarghese/philosophy-101)<br>
**Publishing target:** GitHub Pages, `main` branch, repository root, built with GitHub Pages' supported Jekyll flow

## 1. Product purpose

Philosophy 101 is an approachable guide for curious beginners. It uses short explanations, everyday examples, and reflection questions to help readers think for themselves rather than memorize dense theory. The repository's existing ten-volume structure is the foundation; the first site release makes that library easier to discover and read. More content can be added over time.

## 2. Project facts and constraints

- The public repository currently contains ten volume folders and 32 Markdown articles, plus a root README.
- Existing articles include compact introductions to logic, metaphysics, knowledge, mind, ethics, politics, aesthetics, historical figures, and the meaning of life.
- The current writing is intentionally concise and conversational. The first release must not rewrite article prose or invent new chapters.
- Hosting is GitHub Pages from `main` and the repository root. The site must work under the project base path `https://melvinvarghese.github.io/philosophy-101/`.
- Use GitHub Pages' built-in Jekyll support and supported plugins only. Avoid a separate server, database, login, paid hosting service, or required GitHub Actions build workflow.
- Keep the site static and lightweight; no analytics or tracking scripts are included in this first release.

## 3. Scope

### In scope

- A welcoming homepage that introduces the guide, gives newcomers a clear starting point at Volume 1: The Toolbox, and links to all ten volumes.
- A table-of-contents page for each volume.
- A focused reading page for each existing article.
- Clear breadcrumbs and previous/next chapter navigation.
- A distinct but restrained treatment for each article's reflection question.
- Responsive layouts for phones, tablets, and desktop.
- Basic page-specific metadata for clear browser titles, social sharing, and search snippets.
- Preserve the current article text while adding only the Jekyll metadata/layout structure required to publish it.

### Out of scope for the first release

- Writing or expanding the philosophy content.
- Accounts, comments, quizzes, course progress, saved notes, or recommendations based on a reader profile.
- A search service, database, backend API, analytics, advertising, or paid feature.
- Reorganizing the ten-volume editorial structure.

## 4. Information architecture and reader flow

1. **Homepage (`/philosophy-101/`)** — concise purpose statement, a prominent “Start with the Toolbox” path, an easy-to-scan set of ten volume cards, and three “choose by question” links to existing articles about freedom, knowledge, and meaning. Do not imply that the guide has content it does not yet contain.
2. **Volume pages (`/philosophy-101/volumes/<slug>/`)** — volume title and short introduction, followed by the articles in their existing reading order. Show chapter numbering and title so readers can judge the sequence at a glance.
3. **Article pages (`/philosophy-101/reading/<volume-slug>/<article-slug>/`)** — volume breadcrumb, article title, legible body, reflection prompt, and previous/next links. Include a return link to the volume contents.
4. **Navigation** — keep a compact top-level route back to the library and a footer link back to the repository. Every article must be reachable from the homepage through its volume, and every interior page must have a route back.

The route structure should remain stable as articles are added. Each article's current Markdown file remains the content source of truth; the site must not keep a second manually edited copy of its prose.

## 5. Visual direction

Use an inviting editorial reading-room look that makes the reader feel like a philosopher, not a student opening a textbook:

- Warm ivory or soft paper for reading surfaces, deep ink for text, with restrained terracotta and muted blue accents.
- Expressive serif display/headline type paired with a highly readable sans-serif for body copy and navigation.
- Narrow, comfortable article measure with generous line spacing and whitespace.
- Reflection questions visually distinct from the main explanation without resembling a test or worksheet.
- Volume cards and navigation should suggest a well-organized personal library; keep ornament secondary to the writing.
- Favor the selected light editorial direction over a heavy dark theme. Ensure the design remains legible and cohesive at narrow phone widths.
- Prefer system font stacks and locally authored CSS so the reading experience does not depend on a third-party font or asset service.

## 6. Static implementation approach

- Use Jekyll's built-in Markdown/Liquid/layout support and GitHub Pages' supported build environment.
- Keep the current `Vol-01-...` through `Vol-10-...` folders as the source organization.
- Add a small amount of page metadata/front matter to existing article files so Jekyll can render them through a shared article layout without changing their prose.
- Add shared layouts/includes for the home, volume contents, and article templates, and a small data file for volume order and each volume's article order/titles. The data file may reference the existing article sources but must not duplicate article bodies.
- Use base-URL-aware links throughout so navigation works under the repository path as well as in local previews.
- Use static CSS and minimal JavaScript only if a specific approved interaction cannot be handled with native links or Jekyll templates. No JavaScript is needed for the core reading flow.
- Keep the root README useful for contributors and link to the published reading site after it is verified.

Jekyll's official documentation confirms that GitHub Pages builds Markdown/HTML with layouts, accepts YAML front matter for page metadata and layouts, and restricts server-side plugins to supported ones. The implementation should stay within those documented capabilities.

## 7. Accessibility, responsiveness, and performance

- Use semantic headings, landmarks, descriptive link text, a skip link, visible keyboard focus, and a logical tab order.
- Ensure text and accent colors meet WCAG AA contrast for normal text; do not use color alone to distinguish navigation state.
- Respect reduced-motion preferences; avoid motion that is not needed for reading.
- Test at phone width and desktop width, including direct loading of interior routes and refreshes.
- Keep initial page weight modest: no large decorative images, analytics, client-side framework, or unnecessary external requests.

## 8. SEO and sharing

- Give the homepage, volume pages, and articles descriptive, non-duplicated titles and meta descriptions based on their real content.
- Use a consistent page hierarchy and crawlable ordinary links; provide canonical URLs and Open Graph fields where practical under the Pages base path.
- No ranking position is guaranteed. SEO work is limited to accurate metadata, clear headings, descriptive URLs, and indexable page content.

## 9. Acceptance criteria

- The homepage and all ten volume pages load from GitHub Pages under `/philosophy-101/`.
- All 32 current articles render as individual pages using the approved reading layout; no article copy is lost or silently rewritten.
- Each volume contents list links to its articles in repository order; every article's breadcrumbs and previous/next links resolve correctly, including the first and last article in each volume.
- Internal navigation uses the correct project base path and works when an interior URL is opened directly or refreshed.
- The approved palette/type hierarchy is responsive and readable on phone and desktop; keyboard focus and skip navigation are visible and functional.
- The generated site uses only GitHub Pages-supported Jekyll features and needs no backend or required custom Actions build.
- Site pages contain no analytics/tracking code or third-party font dependency.

## 10. Verification plan

- Build locally with the same GitHub Pages/Jekyll dependency versions wherever practical, and inspect build output for errors or missing pages.
- Check generated routes and links for all 10 volumes and 32 articles, including base-path behavior and previous/next boundaries.
- Run an accessibility spot-check for heading structure, keyboard navigation, focus visibility, contrast, and narrow-screen layout.
- After publication, verify the homepage, one volume page, first/middle/last article pages, page metadata, and repository-to-site navigation at the public GitHub Pages URL.

## 11. Decisions captured

- Make philosophy accessible to curious beginners with concise explanations, relatable examples, and reflection prompts.
- Build the first version as a webpage; add more content later.
- Begin with a reader-first library rather than a guided course or magazine-style discovery experience.
- Preserve the current 10-volume structure and article wording in the first release.
- Publish fully on GitHub Pages using built-in Jekyll from `main`/root.
- Use a warm ivory, deep-ink, terracotta/blue editorial reading-room palette with expressive serif headings, readable sans-serif body text, a narrow reading column, and a mobile-friendly layout.

## References

- [GitHub Docs: About GitHub Pages and Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll)
- [GitHub Docs: Adding content to your GitHub Pages site using Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/adding-content-to-your-github-pages-site-using-jekyll)
- [Jekyll Docs: Front Matter](https://jekyllrb.com/docs/front-matter/)
- [Philosophy 101 repository](https://github.com/melvinvarghese/philosophy-101)
