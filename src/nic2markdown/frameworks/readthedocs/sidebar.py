"""Extract sidebar navigation links from Read the Docs / Sphinx pages.

Parses <nav class="wy-nav-side"> to build a structured list of
navigation links with hierarchy information from toctree-* classes.
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..base import SidebarLink

# Import the generic formatting function (not framework-specific)
from ..mkdocs_material.sidebar import format_sidebar_markdown  # noqa: F401


def extract_sidebar_links(html: str, base_url: str = "") -> list[SidebarLink]:
    """Extract all navigation links from the left sidebar.

    Parses the Sphinx toctree navigation in <nav class="wy-nav-side"> and
    returns links with their nesting level derived from the toctree-lN class.

    Args:
        html: Full page HTML.
        base_url: Base URL for resolving relative hrefs.

    Returns:
        List of SidebarLink objects with href, text, and level.
    """
    soup = BeautifulSoup(html, "lxml")

    nav = soup.find("nav", class_="wy-nav-side")
    if nav is None:
        return []

    links: list[SidebarLink] = []
    toctree_re = re.compile(r"^toctree-l(\d+)$")

    for li in nav.find_all("li", class_=lambda c: c and any(toctree_re.match(cls) for cls in (c if isinstance(c, list) else [c]))):
        a = li.find("a", href=True)
        if a is None:
            continue

        href = a.get("href", "")
        text = a.get_text(strip=True)

        if not text or not href:
            continue

        # Resolve relative URLs
        if base_url and not href.startswith(("http://", "https://", "#", "mailto:")):
            href = urljoin(base_url, href)

        # Determine nesting level from the toctree-lN class
        level = 0
        li_classes = li.get("class", [])
        for cls in li_classes:
            m = toctree_re.match(cls)
            if m:
                level = int(m.group(1)) - 1  # toctree-l1 → level 0, l2 → 1, etc.
                break

        links.append(SidebarLink(href=href, text=text, level=level))

    return links
