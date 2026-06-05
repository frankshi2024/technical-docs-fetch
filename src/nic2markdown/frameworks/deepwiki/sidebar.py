"""Extract sidebar navigation links from DeepWiki pages.

DeepWiki's right sidebar contains an "On this page" TOC with
anchor links to heading IDs. These links follow the structure:
  - h2 headings at level 0
  - h3 headings at level 1
  etc.
"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..base import SidebarLink
from ..mkdocs_material.sidebar import format_sidebar_markdown  # noqa: F401


def extract_sidebar_links(html: str, base_url: str = "") -> list[SidebarLink]:
    """Extract "On this page" TOC links from the DeepWiki right sidebar.

    Looks for anchor links (a[href^='#']) that point to heading IDs.
    Determines nesting level based on the heading level (h2=0, h3=1, etc.).

    Args:
        html: Full page HTML.
        base_url: Base URL for resolving relative hrefs.

    Returns:
        List of SidebarLink objects with href, text, and level.
    """
    soup = BeautifulSoup(html, "lxml")

    links: list[SidebarLink] = []

    # Strategy: Find all anchor links that point to heading IDs
    # and correspond to headings with data-header="true"

    # Build a map of heading id -> heading level
    heading_levels: dict[str, int] = {}
    for h_tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        for heading in soup.find_all(h_tag, attrs={"data-header": "true"}):
            heading_id = heading.get("id", "")
            if heading_id:
                level = int(h_tag[1])  # h1 -> 1, h2 -> 2, etc.
                heading_levels[heading_id] = level

    # Find all anchor links with href starting with "#"
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if not href.startswith("#"):
            continue

        text = a.get_text(strip=True)
        if not text:
            continue

        heading_id = href[1:]  # Remove leading '#'

        # Determine level from the heading it points to
        heading_level = heading_levels.get(heading_id)
        if heading_level is None:
            continue

        # Map heading level to sidebar nesting level:
        # h1 -> 0, h2 -> 0, h3 -> 1, h4 -> 2, etc.
        if heading_level <= 2:
            level = 0
        else:
            level = heading_level - 2

        # Resolve relative URLs
        if base_url and not href.startswith(("http://", "https://", "#", "mailto:")):
            href = urljoin(base_url, href)

        links.append(SidebarLink(href=href, text=text, level=level))

    return links
