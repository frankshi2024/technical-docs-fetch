"""Tests for the DeepWiki extractor module."""

import pytest
from nic2markdown.frameworks.deepwiki.extractor import DeepwikiExtractor, ExtractionError

extractor = DeepwikiExtractor()


DEEPWIKI_FULL_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"TechArticle","headline":"Test Page","publisher":{"@type":"Organization","name":"DeepWiki"}}
    </script>
</head>
<body>
    <div class="w-full flex-1">
        <div class="container-wrapper">
            <div class="container flex">
                <!-- left sidebar -->
                <div class="sidebar-left">
                    <ul><li><a href="/other">Other wiki</a></li></ul>
                </div>
                <!-- main content area -->
                <div class="content-area">
                    <h1 id="test-page" class="group" data-header="true">
                        Test Page
                        <button aria-label="Copy link to header"><svg></svg></button>
                    </h1>
                    <p>This is the <strong>main</strong> content.</p>
                    <h2 id="section-one" class="group" data-header="true">
                        Section One
                        <button aria-label="Copy link to header"><svg></svg></button>
                    </h2>
                    <p>Section one content.</p>
                    <a href="next.html">Next page</a>
                    <img src="img/photo.png" alt="Photo">
                </div>
                <!-- right sidebar -->
                <div class="sidebar-right">
                    <h3>On this page</h3>
                    <a href="#section-one">Section One</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

DEEPWIKI_NO_H1 = """<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"TechArticle","publisher":{"name":"DeepWiki"}}
    </script>
</head>
<body>
    <div>
        <p>No h1 here, no data-header.</p>
    </div>
</body>
</html>"""


class TestExtractArticle:
    def test_extracts_content(self):
        result = extractor.extract(DEEPWIKI_FULL_PAGE)
        assert "Test Page" in result
        assert "main" in result
        assert "content" in result

    def test_removes_copy_link_buttons(self):
        result = extractor.extract(DEEPWIKI_FULL_PAGE)
        assert 'Copy link to header' not in result

    def test_removes_svg_icons_from_headings(self):
        result = extractor.extract(DEEPWIKI_FULL_PAGE)
        assert "<svg" not in result

    def test_fixes_relative_links(self):
        result = extractor.extract(
            DEEPWIKI_FULL_PAGE,
            base_url="https://deepwiki.com/microsoft/vscode/"
        )
        assert 'href="https://deepwiki.com/microsoft/vscode/next.html"' in result

    def test_fixes_relative_images(self):
        result = extractor.extract(
            DEEPWIKI_FULL_PAGE,
            base_url="https://deepwiki.com/microsoft/vscode/"
        )
        assert 'src="https://deepwiki.com/microsoft/vscode/img/photo.png"' in result

    def test_raises_when_no_h1_with_data_header(self):
        with pytest.raises(ExtractionError, match="Could not find DeepWiki content"):
            extractor.extract(DEEPWIKI_NO_H1)

    def test_keeps_content_structure(self):
        result = extractor.extract(DEEPWIKI_FULL_PAGE)
        assert "<h1" in result
        assert "<h2" in result
        assert "<p>" in result
        assert "<strong>" in result

    def test_excludes_sidebar_content(self):
        result = extractor.extract(DEEPWIKI_FULL_PAGE)
        assert "On this page" not in result
        assert "Other wiki" not in result
