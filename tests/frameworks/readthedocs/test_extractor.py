"""Tests for the Read the Docs extractor module."""

import pytest
from nic2markdown.frameworks.readthedocs.extractor import ReadthedocsExtractor, ExtractionError

extractor = ReadthedocsExtractor()

RTD_FULL_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="readthedocs-addons-api-version" content="1">
    <link rel="stylesheet" href="../_static/theme.css">
</head>
<body>
    <nav class="wy-nav-side">
        <ul>
            <li class="toctree-l1"><a href="../page1/">Page 1</a></li>
        </ul>
    </nav>
    <div role="main" class="document">
        <div itemprop="articleBody">
            <section id="hello-world">
                <h1>Hello World<a class="headerlink" href="#hello-world">&para;</a></h1>
                <p>This is the <strong>main</strong> content.</p>
                <a href="next.html">Next page</a>
                <img src="../_images/photo.png" alt="Photo">
            </section>
        </div>
    </div>
</body>
</html>"""

RTD_PAGE_NO_MAIN = """<!DOCTYPE html>
<html>
<head>
    <meta name="readthedocs-addons-api-version" content="1">
</head>
<body>
    <div class="content">
        <p>No role=main div here</p>
    </div>
</body>
</html>"""


class TestExtractArticle:
    def test_extracts_article_content(self):
        result = extractor.extract(RTD_FULL_PAGE)
        assert "Hello World" in result
        assert "main" in result
        assert "content" in result

    def test_removes_headerlink(self):
        result = extractor.extract(RTD_FULL_PAGE)
        assert "headerlink" not in result
        assert "&para;" not in result

    def test_removes_toc_backref(self):
        html = (
            '<div role="main">'
            '<h3><a class="toc-backref" href="#id4">version</a></h3>'
            '</div>'
        )
        result = extractor.extract(html)
        assert "toc-backref" not in result

    def test_unwraps_span_pre(self):
        html = (
            '<div role="main">'
            '<p><code class="docutils literal notranslate">'
            '<span class="pre">.readthedocs.yaml</span>'
            '</code></p>'
            '</div>'
        )
        result = extractor.extract(html)
        assert '<span class="pre">' not in result
        assert '.readthedocs.yaml' in result

    def test_fixes_relative_links(self):
        result = extractor.extract(
            RTD_FULL_PAGE,
            base_url="https://example.com/docs/page/"
        )
        assert 'href="https://example.com/docs/page/next.html"' in result or \
               "href=\"https://example.com/docs/page/next.html\"" in result

    def test_fixes_relative_images(self):
        result = extractor.extract(
            RTD_FULL_PAGE,
            base_url="https://example.com/docs/page/"
        )
        assert 'src="https://example.com/docs/_images/photo.png"' in result or \
               "src=\"https://example.com/docs/_images/photo.png\"" in result

    def test_raises_when_no_main_div(self):
        with pytest.raises(ExtractionError, match="Could not find main"):
            extractor.extract(RTD_PAGE_NO_MAIN)

    def test_keeps_content_structure(self):
        result = extractor.extract(RTD_FULL_PAGE)
        assert "<h1" in result
        assert "<p>" in result
        assert "<strong>" in result
