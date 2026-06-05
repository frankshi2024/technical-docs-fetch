"""Extract the main article content from a Read the Docs / Sphinx HTML page."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup


class ExtractionError(Exception):
    """Raised when the article content cannot be found."""


def _fix_relative_urls(soup: BeautifulSoup, base_url: str) -> None:
    """Convert relative URLs in href/src attributes to absolute."""
    if not base_url:
        return

    for tag in soup.find_all(["a", "img", "link", "script"], href=True):
        href = tag["href"]
        if href and not href.startswith(("http://", "https://", "#", "mailto:", "data:", "javascript:")):
            tag["href"] = urljoin(base_url, href)

    for tag in soup.find_all(["img", "script", "source", "video"], src=True):
        src = tag["src"]
        if src and not src.startswith(("http://", "https://", "data:")):
            tag["src"] = urljoin(base_url, src)


def _remove_noise(soup: BeautifulSoup) -> None:
    """Remove elements that don't translate well to Markdown."""
    for a in soup.find_all("a", class_="headerlink"):
        a.extract()
    for a in soup.find_all("a", class_="toc-backref"):
        a.extract()
    for span in soup.find_all("span", class_="pre"):
        span.unwrap()


class ReadthedocsExtractor:
    """Extract article content from Read the Docs / Sphinx pages."""

    def extract(self, html: str, base_url: str = "") -> str:
        """Extract article inner HTML from the full page HTML.

        Looks for <div role="main"> which is the standard Sphinx content wrapper.

        Raises ExtractionError if no such div is found.
        """
        soup = BeautifulSoup(html, "lxml")

        main_div = soup.find("div", attrs={"role": "main"})
        if main_div is None:
            raise ExtractionError(
                "Error: Could not find main content div. "
                "The page may not be a standard Read the Docs / Sphinx page."
            )

        _remove_noise(main_div)
        _fix_relative_urls(main_div, base_url)

        return main_div.decode_contents()
