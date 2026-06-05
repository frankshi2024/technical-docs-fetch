"""Tests for the DeepWiki sidebar link extraction."""

from nic2markdown.frameworks.deepwiki.sidebar import (
    extract_sidebar_links,
    format_sidebar_markdown,
)
from nic2markdown.frameworks.base import SidebarLink


DEEPWIKI_WITH_TOC = """<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"TechArticle","publisher":{"name":"DeepWiki"}}
    </script>
</head>
<body>
    <div class="w-full flex-1">
        <div class="container flex">
            <!-- main content -->
            <div class="content-area">
                <h1 id="test-page" class="group" data-header="true">Test Page</h1>
                <p>Intro content.</p>
                <h2 id="section-one" class="group" data-header="true">Section One</h2>
                <p>Section one content.</p>
                <h2 id="section-two" class="group" data-header="true">Section Two</h2>
                <p>Section two content.</p>
                <h3 id="subsection" class="group" data-header="true">Subsection</h3>
                <p>Subsection content.</p>
            </div>
            <!-- right sidebar with TOC -->
            <div class="sidebar-right">
                <h3>On this page</h3>
                <a href="#section-one">Section One</a>
                <a href="#section-two">Section Two</a>
                <a href="#subsection">Subsection</a>
            </div>
        </div>
    </div>
</body>
</html>"""


class TestExtractSidebarLinks:
    def test_extracts_toc_links(self):
        links = extract_sidebar_links(DEEPWIKI_WITH_TOC)
        texts = {l.text for l in links}
        assert "Section One" in texts
        assert "Section Two" in texts
        assert "Subsection" in texts

    def test_h2_links_are_level_0(self):
        links = extract_sidebar_links(DEEPWIKI_WITH_TOC)
        for link in links:
            if link.text in ("Section One", "Section Two"):
                assert link.level == 0, f"{link.text} should be level 0, got {link.level}"

    def test_h3_links_are_level_1(self):
        links = extract_sidebar_links(DEEPWIKI_WITH_TOC)
        for link in links:
            if link.text == "Subsection":
                assert link.level == 1, f"Subsection should be level 1, got {link.level}"

    def test_links_have_correct_href(self):
        links = extract_sidebar_links(DEEPWIKI_WITH_TOC)
        href_map = {l.text: l.href for l in links}
        assert href_map.get("Section One") == "#section-one"
        assert href_map.get("Section Two") == "#section-two"

    def test_no_toc_returns_empty(self):
        html = "<html><body>No TOC here</body></html>"
        links = extract_sidebar_links(html)
        assert links == []

    def test_resolves_relative_urls_in_toc(self):
        links = extract_sidebar_links(
            DEEPWIKI_WITH_TOC,
            base_url="https://deepwiki.com/microsoft/vscode"
        )
        for link in links:
            if link.text == "Section One":
                # Anchor links stay as-is (they start with '#')
                assert link.href == "#section-one"


class TestFormatSidebarMarkdown:
    def test_format_basic(self):
        links = [
            SidebarLink(href="#section-one", text="Section One", level=0),
            SidebarLink(href="#subsection", text="Subsection", level=1),
        ]
        md = format_sidebar_markdown(links)
        assert "## Sidebar Links" in md
        assert "- [Section One](#section-one)" in md
        assert "  - [Subsection](#subsection)" in md

    def test_format_empty(self):
        assert format_sidebar_markdown([]) == ""
