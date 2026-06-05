"""HTML → GFM Markdown converter for Read the Docs / Sphinx pages.

Uses markdownify for the base conversion, with pre- and post-processing
to handle Sphinx-specific structures like admonitions, code blocks,
inline code, and tables.
"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter

from ..base import BaseConverter, SidebarLink
from .validator import detect as _detect
from ..mkdocs_material.converter import (
    ADMONITION_MAP,
    _postprocess_admonitions,
    _postprocess_whitespace,
    _postprocess_relative_links,
)


# ── Custom markdownify converter ────────────────────────────────────────


def _extract_code_language(el: Tag) -> str:
    """Callback for markdownify to extract language from <code> class."""
    code = el.find("code")
    if code is None:
        code = el
    for cls in code.get("class", []):
        if cls.startswith("language-"):
            return cls[len("language-"):]
    return ""


class _ArticleMdConverter(MarkdownConverter):
    """Custom markdownify converter tailored for Sphinx articles."""

    def __init__(self, base_url: str = "", **kwargs):
        kwargs.setdefault("code_language_callback", _extract_code_language)
        super().__init__(**kwargs)
        self.base_url = base_url

    def convert_a(self, el: Tag, text: str, parent_tags: list[str]) -> str:
        classes = el.attrs.get("class", [])
        if "headerlink" in classes:
            return ""
        return super().convert_a(el, text, parent_tags)

    def convert_img(self, el: Tag, text: str, parent_tags: list[str]) -> str:
        src = el.attrs.get("src", "")
        if src and self.base_url and not src.startswith(("http://", "https://", "data:")):
            src = urljoin(self.base_url, src)
        alt = el.attrs.get("alt", "")
        return f"![{alt}]({src})"


# ── Preprocessing ───────────────────────────────────────────────────────

def _preprocess_admonitions(soup: BeautifulSoup) -> None:
    """Convert Sphinx admonition divs to the <!--admon:TYPE--> marker system."""
    for div in soup.find_all("div", class_="admonition"):
        classes = div.get("class", [])
        ad_type = "note"
        for cls in classes:
            if cls != "admonition" and cls in ADMONITION_MAP:
                ad_type = cls
                break

        gfm_type = ADMONITION_MAP.get(ad_type, "NOTE")

        title_p = div.find("p", class_="admonition-title")
        if title_p:
            title_text = title_p.get_text(strip=True)
            title_p.extract()
            if title_text:
                strong_tag = soup.new_tag("strong")
                strong_tag.string = title_text
                p_tag = soup.new_tag("p")
                p_tag.append(strong_tag)
                div.insert(0, p_tag)

        inner = div.decode_contents()
        new_tag = soup.new_tag("admon")
        new_tag["data-type"] = gfm_type
        marker_start = soup.new_string(f"<!--admon:{gfm_type}-->")
        marker_end = soup.new_string("<!--/admon-->")
        new_tag.append(marker_start)
        new_tag.append(BeautifulSoup(inner, "html.parser"))
        new_tag.append(marker_end)
        div.replace_with(new_tag)


def _extract_language_from_highlight(div: Tag) -> str:
    """Extract the language from a Sphinx highlight div class.

    Classes like 'highlight-yaml', 'highlight-python', 'highlight-default'
    yield 'yaml', 'python', etc. 'highlight-default' means no language.
    """
    for cls in div.get("class", []):
        if cls.startswith("highlight-") and cls != "highlight-default":
            return cls[len("highlight-"):]
    return ""


def _preprocess_code_blocks(soup: BeautifulSoup) -> None:
    """Convert Sphinx highlight divs to standard <pre><code> with language class.

    Sphinx pattern:
      <div class="highlight highlight-yaml"><div class="highlight">
        <pre><span></span><span class="linenos"> 1</span>code...</pre>
      </div></div>

    Also handles <div class="highlight-yaml notranslate"> variant.
    """
    for div in soup.find_all("div", class_="highlight"):
        # Skip if this is an inner highlight div (nested inside another highlight)
        parent = div.parent
        if parent and parent.name == "div" and "highlight" in (parent.get("class") or []):
            continue

        # Determine the language — check both the outer and inner div
        lang = _extract_language_from_highlight(div)
        if not lang and parent and parent.name == "div":
            lang = _extract_language_from_highlight(parent)

        pre = div.find("pre")
        if pre is None:
            continue

        # Remove line number spans
        for linenos in pre.find_all("span", class_="linenos"):
            linenos.extract()

        # Remove empty <span></span> that pygments sometimes adds
        for span in pre.find_all("span"):
            if not span.get_text(strip=True) and not span.find_all():
                span.unwrap()

        code_text = pre.get_text()

        # Build replacement
        code_tag = soup.new_tag("code")
        if lang:
            code_tag["class"] = [f"language-{lang}"]
        code_tag.string = code_text

        pre_tag = soup.new_tag("pre")
        pre_tag.append(code_tag)

        # Replace the outer highlight structure
        outer = parent if (parent and parent.name == "div" and "highlight" in (parent.get("class") or [])) else div
        outer.replace_with(pre_tag)


def _preprocess_tables(soup: BeautifulSoup) -> None:
    """Unwrap table wrappers that Sphinx may add."""
    for wrapper in soup.find_all("div", class_="table-wrapper"):
        wrapper.unwrap()


def _preprocess_inline_code(soup: BeautifulSoup) -> None:
    """Unwrap <span class="pre"> inside Sphinx inline code elements.

    Sphinx pattern: <code class="docutils literal notranslate"><span class="pre">text</span></code>
    """
    for code in soup.find_all("code", class_=lambda c: c and "docutils" in c):
        for span in code.find_all("span", class_="pre"):
            span.unwrap()


def _preprocess_headings(soup: BeautifulSoup) -> None:
    """Unwrap inline formatting inside headings."""
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        for bold in tag.find_all(["strong", "b", "em", "i"]):
            bold.unwrap()


def _preprocess(soup: BeautifulSoup) -> None:
    _preprocess_headings(soup)
    _preprocess_admonitions(soup)
    _preprocess_code_blocks(soup)
    _preprocess_tables(soup)
    _preprocess_inline_code(soup)


# ── Postprocessing ──────────────────────────────────────────────────────

def _postprocess(text: str, base_url: str = "") -> str:
    text = _postprocess_admonitions(text)
    text = _postprocess_whitespace(text)
    if base_url:
        text = _postprocess_relative_links(text, base_url)
    return text.strip() + "\n"


# ── Main Converter Class ────────────────────────────────────────────────

class ReadthedocsConverter(BaseConverter):
    """Converter for Read the Docs / Sphinx documentation pages."""

    @staticmethod
    def detect(html: str) -> bool:
        return _detect(html)

    def extract_article(self, html: str, base_url: str) -> str:
        from .extractor import ReadthedocsExtractor
        extractor = ReadthedocsExtractor()
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
