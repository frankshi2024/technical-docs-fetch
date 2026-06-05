"""Read the Docs / Sphinx page detection."""

from bs4 import BeautifulSoup


META_NAMES = ("readthedocs-addons-api-version", "readthedocs-project-slug")


def detect(html: str) -> bool:
    """Return True if the HTML is a Read the Docs / Sphinx documentation page.

    Checks for <meta name="readthedocs-addons-api-version"> or
    <meta name="readthedocs-project-slug">.
    """
    soup = BeautifulSoup(html, "lxml")
    for name in META_NAMES:
        meta = soup.find("meta", attrs={"name": name})
        if meta is not None:
            return True
    return False


def get_version(html: str) -> str | None:
    """Extract a version identifier string, or None if not a Read the Docs page.

    Returns "sphinx-rtd" or "sphinx-rtd (project_slug/version_slug)" when the
    Read the Docs meta tags are present.
    """
    soup = BeautifulSoup(html, "lxml")
    project_meta = soup.find("meta", attrs={"name": "readthedocs-project-slug"})
    version_meta = soup.find("meta", attrs={"name": "readthedocs-version-slug"})

    if project_meta is None and version_meta is None:
        # Still check for addons-api-version as fallback
        addons = soup.find("meta", attrs={"name": "readthedocs-addons-api-version"})
        if addons is None:
            return None
        return "sphinx-rtd"

    project = project_meta.get("content", "").strip() if project_meta else ""
    version = version_meta.get("content", "").strip() if version_meta else ""

    if project and version:
        return f"sphinx-rtd ({project}/{version})"
    if project:
        return f"sphinx-rtd ({project})"
    if version:
        return f"sphinx-rtd ({version})"
    return "sphinx-rtd"
