"""Tests for the DeepWiki validator module."""

from nic2markdown.frameworks.deepwiki.validator import detect, get_version


DEEPWIKI_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>VS Code Architecture</title>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"TechArticle","headline":"VS Code Architecture Overview","publisher":{"@type":"Organization","name":"DeepWiki"}}
    </script>
</head>
<body>
    <div>
        <div>
            <h1 id="test-heading" class="group" data-header="true">Test Heading</h1>
            <p>Some content.</p>
        </div>
    </div>
</body>
</html>"""

DEEPWIKI_HTML_ALT = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"TechArticle","headline":"Alt Page","description":"Test","publisher":{"name":"DeepWiki","@type":"Organization"}}
    </script>
</head>
<body>
    <div>
        <h2 id="section" class="group" data-header="true">Section</h2>
        <p>Content.</p>
    </div>
</body>
</html>"""

DEEPWIKI_NO_LD_JSON_BUT_HEADERS = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div>
        <h1 id="heading" class="group" data-header="true">Heading</h1>
        <p>Content.</p>
    </div>
</body>
</html>"""

NON_DEEPWIKI_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="generator" content="Hugo 0.120.0">
    <title>Test</title>
</head>
<body><p>Hello</p></body>
</html>"""


class TestDetect:
    def test_deepwiki_with_ld_json(self):
        assert detect(DEEPWIKI_HTML) is True

    def test_deepwiki_alt_ld_json(self):
        assert detect(DEEPWIKI_HTML_ALT) is True

    def test_deepwiki_with_headers_only(self):
        assert detect(DEEPWIKI_NO_LD_JSON_BUT_HEADERS) is True

    def test_non_deepwiki(self):
        assert detect(NON_DEEPWIKI_HTML) is False

    def test_empty_html(self):
        assert detect("<html></html>") is False


class TestGetVersion:
    def test_returns_deepwiki_identifier(self):
        version = get_version(DEEPWIKI_HTML)
        assert version == "DeepWiki"

    def test_returns_none_for_unknown(self):
        version = get_version(NON_DEEPWIKI_HTML)
        assert version is None

    def test_returns_deepwiki_for_headers_only(self):
        version = get_version(DEEPWIKI_NO_LD_JSON_BUT_HEADERS)
        assert version == "DeepWiki"
