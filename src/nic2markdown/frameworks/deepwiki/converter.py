"""HTML → GFM Markdown converter for DeepWiki pages.

Uses markdownify for the base conversion, with pre- and post-processing
to handle DeepWiki-specific structures like headings with copy-link buttons,
code blocks, Mermaid diagrams, and links.
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter

from ..base import BaseConverter, SidebarLink


class _ArticleMdConverter(MarkdownConverter):
    """Custom markdownify converter tailored for DeepWiki articles."""

    def __init__(self, base_url: str = "", **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url

    def convert_a(self, el: Tag, text: str, parent_tags: list[str]) -> str:
        # Skip empty links and anchor-only links
        href = el.attrs.get("href", "")
        if not text.strip() and href.startswith("#"):
            return ""
        return super().convert_a(el, text, parent_tags)

    def convert_img(self, el: Tag, text: str, parent_tags: list[str]) -> str:
        src = el.attrs.get("src", "")
        if src and self.base_url and not src.startswith(("http://", "https://", "data:")):
            src = urljoin(self.base_url, src)
        alt = el.attrs.get("alt", "")
        return f"![{alt}]({src})"


# ── Preprocessing ──────────────────────────────────────────────────────

def _preprocess_headings(soup: BeautifulSoup) -> None:
    """Clean DeepWiki heading elements.

    - Remove copy-link buttons from within headings
    - Unwrap bold/italic/em inside headings
    - Remove data-header and class="group" attributes
    """
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        # Remove copy-link buttons
        for btn in h.find_all("button", attrs={"aria-label": "Copy link to header"}):
            btn.extract()
        # Remove remaining SVG icons
        for svg in h.find_all("svg"):
            svg.extract()
        # Unwrap bold/italic
        for tag in h.find_all(["strong", "b", "em", "i"]):
            tag.unwrap()
        # Remove data-header and group class
        if h.has_attr("data-header"):
            del h["data-header"]
        classes = h.get("class", [])
        if "group" in classes:
            classes.remove("group")
        if classes:
            h["class"] = classes
        else:
            del h["class"]


def _preprocess_code_blocks(soup: BeautifulSoup) -> None:
    """Normalize DeepWiki code blocks for markdownify.

    DeepWiki uses <pre class="..."><code>...</code></pre>.
    The language class may be on the <code> element.
    Markdownify handles this naturally, but we ensure the structure is clean.
    """
    for pre in soup.find_all("pre"):
        code = pre.find("code")
        if code:
            # Ensure code is the direct child — if there are wrappers, unwrap
            pass


def _preprocess_mermaid(soup: BeautifulSoup) -> None:
    """Handle Mermaid diagrams in DeepWiki pages.

    If a <pre> contains a <template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING">,
    the Mermaid diagram didn't render server-side. Replace with a comment.
    """
    for pre in soup.find_all("pre"):
        template = pre.find("template", attrs={"data-dgst": "BAILOUT_TO_CLIENT_SIDE_RENDERING"})
        if template:
            comment = soup.new_string("<!-- Mermaid diagram (not rendered server-side) -->")
            pre.replace_with(comment)

    # Also check for mermaid class on pre elements
    for pre in soup.find_all("pre", class_=lambda c: c and "mermaid" in " ".join(c) if isinstance(c, list) else "mermaid" in str(c)):
        # Leave mermaid content as-is; markdownify will handle as code block
        pass


def _preprocess_links(soup: BeautifulSoup) -> None:
    """Ensure links are absolute where possible.

    GitHub source links are preserved as-is. Other relative links
    will be fixed in postprocessing.
    """
    pass  # Links are fixed in postprocessing via regex


def _preprocess_tables(soup: BeautifulSoup) -> None:
    """Unwrap responsive table wrappers around <table> elements."""
    # Look for divs that contain only a table
    for div in soup.find_all("div"):
        children = list(div.children)
        # If a div has only one child and it's a table, unwrap
        non_empty = [c for c in children if isinstance(c, Tag) or (isinstance(c, str) and c.strip())]
        if len(non_empty) == 1 and isinstance(non_empty[0], Tag) and non_empty[0].name == "table":
            div.unwrap()


def _preprocess(soup: BeautifulSoup) -> None:
    _preprocess_headings(soup)
    _preprocess_code_blocks(soup)
    _preprocess_mermaid(soup)
    _preprocess_links(soup)
    _preprocess_tables(soup)


# ── Postprocessing ─────────────────────────────────────────────────────

def _postprocess_whitespace(text: str) -> str:
    """Collapse 3 or more consecutive newlines to 2."""
    return re.sub(r"\n{3,}", "\n\n", text)


def _postprocess_relative_links(text: str, base_url: str) -> str:
    """Fix relative links in markdown [text](url) syntax."""
    if not base_url:
        return text

    def _fix_link(m: re.Match) -> str:
        link_text = m.group(1)
        url = m.group(2)
        if url.startswith(("http://", "https://", "#", "mailto:", "data:")):
            return m.group(0)
        full = urljoin(base_url, url)
        return f"[{link_text}]({full})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _fix_link, text)


def _postprocess(text: str, base_url: str = "") -> str:
    text = _postprocess_whitespace(text)
    if base_url:
        text = _postprocess_relative_links(text, base_url)
    return text.strip() + "\n"


# ── Main Converter Class ───────────────────────────────────────────────

class DeepwikiConverter(BaseConverter):
    """Converter for DeepWiki documentation pages."""

    @staticmethod
    def detect(html: str) -> bool:
        from .validator import detect as _detect
        return _detect(html)

    def extract_article(self, html: str, base_url: str) -> str:
        from .extractor import DeepwikiExtractor
        extractor = DeepwikiExtractor()
        return extractor.extract(html, base_url)

    def convert(self, article_html: str, base_url: str = "") -> str:
        soup = BeautifulSoup(article_html, "lxml")
        _preprocess(soup)
        md_converter = _ArticleMdConverter(base_url=base_url, heading_style="ATX")
        md = md_converter.convert_soup(soup)
        return _postprocess(md, base_url=base_url)

    def extract_sidebar_links(self, html: str, base_url: str) -> list[SidebarLink]:
        from .sidebar import extract_sidebar_links as _extract
        return _extract(html, base_url)
