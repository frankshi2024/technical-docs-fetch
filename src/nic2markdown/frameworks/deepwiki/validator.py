"""DeepWiki page detection."""

import json
import re

from bs4 import BeautifulSoup


def detect(html: str) -> bool:
    """Return True if the HTML is a DeepWiki documentation page.

    Checks for the Schema.org ld+json script with DeepWiki publisher,
    and also checks for data-header="true" on headings as a secondary signal.
    """
    soup = BeautifulSoup(html, "lxml")

    # Primary check: ld+json script with DeepWiki publisher
    script = soup.find("script", type="application/ld+json")
    if script and script.string:
        try:
            data = json.loads(script.string)
            if (
                isinstance(data, dict)
                and data.get("@type") == "TechArticle"
                and isinstance(data.get("publisher"), dict)
                and data["publisher"].get("name") == "DeepWiki"
            ):
                return True
        except (json.JSONDecodeError, TypeError, AttributeError):
            # If JSON parsing fails, fall back to string search
            if '"publisher":{"name":"DeepWiki"}' in script.string or \
               '"name":"DeepWiki"' in script.string:
                return True

    # Secondary check: data-header="true" on headings
    heading = soup.find(attrs={"data-header": "true"})
    if heading and heading.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return True

    return False


def get_version(html: str) -> str | None:
    """Return the framework identifier for DeepWiki pages.

    Returns "DeepWiki" if the page is a DeepWiki page, None otherwise.
    """
    if detect(html):
        return "DeepWiki"
    return None
