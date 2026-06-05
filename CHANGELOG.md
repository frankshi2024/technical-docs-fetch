# Changelog

## [0.2.0] — 2026-06-05

### Added
- **Read the Docs (Sphinx)** framework support
  - Detects `<meta name="readthedocs-addons-api-version">` signatures
  - Extracts content from `<div role="main">`
  - Converts Sphinx admonitions, `highlight-*` code blocks, `<span class="pre">` inline code
  - Parses `toctree-lN` sidebar hierarchy
- **DeepWiki** framework support
  - Detects via `<script type="application/ld+json">` (publisher: DeepWiki)
  - Extracts content anchored on `h1[data-header="true"]`
  - Handles Mermaid bailout templates, heading copy-link buttons
  - Parses right-sidebar TOC anchor links
- **TECH.md** — standalone technical documentation (architecture, framework guide, test structure)
- Project renamed to `technical-docs-fetch`

### Changed
- **Install scripts**: skill now installed to `~/.agents/skills/nic2markdown` (was `~/.config/agents/skills/nic2markdown`)
- README rewritten: purpose-first layout, background moved to end
- Gateway router cleaned up with `_CONVERTER_NAME_MAP` and per-framework version extraction
- All install script and documentation URLs updated to `technical-docs-fetch`

### Tests
- 147 tests total (was 46): +49 ReadTheDocs, +46 DeepWiki, +4 gateway

---

## [0.1.0] — 2026-05-18

### Added

- **Initial release** — core MkDocs Material → GFM Markdown conversion pipeline
- `validator.py`: Detect MkDocs Material pages via `<meta name="generator">`
- `fetcher.py`: Download HTML via httpx with redirect handling
- `extractor.py`: Extract `<article class="md-content__inner md-typeset">` from full page; fix relative URLs; remove headerlink anchors and code-copy buttons
- `converter.py`: HTML → Markdown via `markdownify` with custom pre/post-processing:
  - **Admonitions**: 11-type mapping to GFM alerts (`> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!CAUTION]`)
  - **Headings**: `<strong>` / `<em>` unwrapping inside `<h1>`-`<h6>`
  - **Task lists**: `<li class="task-list-item">` → `- [ ]` / `- [x]`
  - **Code blocks**: `<div class="highlight"><pre><code>` → fenced ` ``` `
  - **MathJax**: arithmatex `<span>`/`<div>` → `$`/`$$` delimiters
  - **Tabbed sets**: multi-code-block with label annotations
  - **Footnotes**: `[^n]` / `[^n]:` format
  - **Relative links**: resolved to absolute URLs
- `writer.py`: Timestamped naming (`<stem>.<yyyymmddhhmmss>.md`)
- `cli.py`: argparse-based CLI
- 37 unit tests covering validator, extractor, and converter logic
- Project scaffolding: uv-managed dependencies, git-init
