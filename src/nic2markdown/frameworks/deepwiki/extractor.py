"""Extract the main content from a DeepWiki HTML page.

DeepWiki pages are rendered by Next.js with Tailwind-styled divs.
There is no dedicated <article> or <main> tag. We use the h1 with
data-header="true" to locate the content area.
"""

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
    # Remove copy-link buttons from headings
    for btn in soup.find_all("button", attrs={"aria-label": "Copy link to header"}):
        btn.extract()

    # Remove empty template tags (React suspense boundaries)
    for template in soup.find_all("template"):
        template.extract()

    # Remove SVG icons inside headings (they are copy-link icons)
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        for svg in h.find_all("svg"):
            svg.extract()

    # Remove "dismiss" buttons from info boxes
    for btn in soup.find_all("button"):
        if btn.find("span", class_="sr-only") and btn.find("svg"):
            # Only remove if it looks like a dismiss/close button
            sr = btn.find("span", class_="sr-only")
            if sr and sr.get_text(strip=True) in ("Dismiss", "Close"):
                btn.extract()


class DeepwikiExtractor:
    """Extract article content from DeepWiki pages."""

    def extract(self, html: str, base_url: str = "") -> str:
        """Extract content inner HTML from the full page HTML.

        Strategy:
        1. Find the h1 with data-header="true"
        2. Walk up to find the nearest container div that holds all
           content headings (h1-h6 with data-header="true")
        3. Extract that container's inner HTML

        Raises ExtractionError if no h1 with data-header="true" is found.
        """
        soup = BeautifulSoup(html, "lxml")

        # Find the main h1 heading
        h1 = soup.find("h1", attrs={"data-header": "true"})
        if h1 is None:
            raise ExtractionError(
                "Error: Could not find DeepWiki content. "
                "No h1 heading with data-header='true' found."
            )

        # Strategy: Find all heading elements with data-header="true",
        # then find the deepest common ancestor div that contains all of them.
        # This gives us the "content area" div, not the outer flex container
        # which also wraps sidebars.

        # Find all heading elements with data-header="true"
        all_headings = soup.find_all(attrs={"data-header": "true"})
        all_headings = [h for h in all_headings if h.name in ("h1", "h2", "h3", "h4", "h5", "h6")]

        # Walk up from h1 and collect all ancestor divs
        content_div = None
        candidate = h1.parent
        while candidate is not None and candidate.name:
            if candidate.name == "div":
                # Check how many headings this div contains
                contained = sum(1 for h in all_headings if h in candidate.descendants)
                if contained == len(all_headings):
                    # This div contains all headings — it might be the content area.
                    # But it could also be the outer flex container. We want the
                    # innermost one that contains all headings.
                    if content_div is None:
                        content_div = candidate
                    # content_div is already set; the first one we find (closest to h1)
                    # is the innermost, so we keep it and stop looking higher.
                    break
            candidate = candidate.parent

        if content_div is None:
            # Fallback: find the nearest div that contains h1
            candidate = h1.parent
            while candidate is not None and candidate.name:
                if candidate.name == "div":
                    content_div = candidate
                    break
                candidate = candidate.parent

        if content_div is None:
            # Ultimate fallback: just use the h1's parent
            content_div = h1.parent

        _remove_noise(content_div)
        _fix_relative_urls(content_div, base_url)

        return content_div.decode_contents()
