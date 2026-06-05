"""Tests for the Read the Docs sidebar link extraction."""

from nic2markdown.frameworks.readthedocs.sidebar import extract_sidebar_links
from nic2markdown.frameworks.mkdocs_material.sidebar import format_sidebar_markdown
from nic2markdown.frameworks.base import SidebarLink


RTD_WITH_SIDEBAR = """<!DOCTYPE html>
<html>
<head>
    <meta name="readthedocs-addons-api-version" content="1">
</head>
<body>
    <nav class="wy-nav-side">
        <div class="wy-menu wy-menu-vertical">
            <p class="caption">Getting started</p>
            <ul>
                <li class="toctree-l1">
                    <a class="reference internal" href="../tutorial/">Tutorial</a>
                </li>
                <li class="toctree-l1">
                    <a class="reference internal" href="../intro/">Introduction</a>
                </li>
            </ul>
            <p class="caption">Configuration</p>
            <ul class="current">
                <li class="toctree-l1">
                    <a class="reference internal" href="index.html">Overview</a>
                </li>
                <li class="toctree-l1 current">
                    <a class="current reference internal" href="#">Reference</a>
                    <ul>
                        <li class="toctree-l2">
                            <a class="reference internal" href="#settings">Settings</a>
                            <ul>
                                <li class="toctree-l3">
                                    <a class="reference internal" href="#version">version</a>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>
    <div role="main">
        <p>Content</p>
    </div>
</body>
</html>"""


class TestExtractSidebarLinks:
    def test_extracts_top_level_links(self):
        links = extract_sidebar_links(RTD_WITH_SIDEBAR)
        texts = {l.text for l in links}
        assert "Tutorial" in texts
        assert "Introduction" in texts
        assert "Overview" in texts

    def test_extracts_hierarchy_levels(self):
        links = extract_sidebar_links(RTD_WITH_SIDEBAR)
        levels = {l.text: l.level for l in links}
        # toctree-l1 → level 0, toctree-l2 → level 1, toctree-l3 → level 2
        assert levels.get("Tutorial") == 0
        assert levels.get("Settings") == 1
        assert levels.get("version") == 2

    def test_resolves_relative_urls(self):
        links = extract_sidebar_links(
            RTD_WITH_SIDEBAR,
            base_url="https://example.com/docs/"
        )
        for link in links:
            if link.text == "Tutorial":
                assert link.href == "https://example.com/tutorial/"
            elif link.text == "Overview":
                assert link.href == "https://example.com/docs/index.html"

    def test_no_sidebar_returns_empty(self):
        html = "<html><body>No sidebar</body></html>"
        links = extract_sidebar_links(html)
        assert links == []

    def test_current_page_marker_not_duplicated(self):
        """The 'current' page link (with href="#") should not duplicate."""
        links = extract_sidebar_links(RTD_WITH_SIDEBAR)
        # Reference link with href="#" should still be found
        assert any(l.text == "Reference" for l in links)

    def test_skips_links_without_href(self):
        html = """
        <nav class="wy-nav-side">
            <ul>
                <li class="toctree-l1"><a>No href</a></li>
                <li class="toctree-l1"><a href="../page1/">With href</a></li>
            </ul>
        </nav>
        """
        links = extract_sidebar_links(html)
        texts = {l.text for l in links}
        assert "No href" not in texts
        assert "With href" in texts


class TestFormatSidebarMarkdown:
    def test_format_basic(self):
        links = [
            SidebarLink(href="https://example.com/", text="Home", level=0),
            SidebarLink(href="https://example.com/lab1/", text="Lab 1", level=1),
        ]
        md = format_sidebar_markdown(links)
        assert "## Sidebar Links" in md
        assert "- [Home](https://example.com/)" in md
        assert "  - [Lab 1](https://example.com/lab1/)" in md

    def test_format_empty(self):
        assert format_sidebar_markdown([]) == ""
