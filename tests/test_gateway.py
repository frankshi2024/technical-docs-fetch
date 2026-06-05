"""Tests for the gateway module (framework detection and routing)."""

import pytest
from nic2markdown.gateway import (
    detect_framework,
    get_converter,
    get_framework_name,
    UnsupportedFrameworkError,
)
from nic2markdown.frameworks.deepwiki.converter import DeepwikiConverter
from nic2markdown.frameworks.mkdocs_material.converter import MkdocsMaterialConverter
from nic2markdown.frameworks.readthedocs.converter import ReadthedocsConverter


# ── HTML fixtures ────────────────────────────────────────────────────────

MKDOCS_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="generator" content="mkdocs-1.6.1, mkdocs-material-9.7.6">
    <title>Test</title>
</head>
<body><article class="md-content__inner md-typeset"><p>Content</p></article></body>
</html>"""

RTD_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="readthedocs-addons-api-version" content="1">
    <meta name="readthedocs-project-slug" content="docs">
    <meta name="readthedocs-version-slug" content="stable">
    <title>Test</title>
</head>
<body><div role="main"><section><p>Content</p></section></div></body>
</html>"""

DEEPWIKI_HTML = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<script type="application/ld+json">{"@type":"TechArticle","headline":"Test","publisher":{"@type":"Organization","name":"DeepWiki"}}</script>
<h1 data-header="true" id="test">Test</h1>
<p>Content</p>
</body>
</html>"""

HUGO_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="generator" content="Hugo 0.120.0">
    <title>Test</title>
</head>
<body><p>Content</p></body>
</html>"""


# ── Detect tests ─────────────────────────────────────────────────────────

class TestDetectFramework:
    """Each registered converter should be detectable."""

    def test_detects_mkdocs(self):
        converter = detect_framework(MKDOCS_HTML)
        assert isinstance(converter, MkdocsMaterialConverter)

    def test_detects_readthedocs(self):
        converter = detect_framework(RTD_HTML)
        assert isinstance(converter, ReadthedocsConverter)

    def test_detects_deepwiki(self):
        converter = detect_framework(DEEPWIKI_HTML)
        assert isinstance(converter, DeepwikiConverter)

    def test_returns_none_for_unknown(self):
        converter = detect_framework(HUGO_HTML)
        assert converter is None


# ── Get converter tests ──────────────────────────────────────────────────

class TestGetConverter:
    """get_converter returns the right converter or raises."""

    def test_returns_converter_for_mkdocs(self):
        converter = get_converter(MKDOCS_HTML)
        assert isinstance(converter, MkdocsMaterialConverter)

    def test_returns_converter_for_readthedocs(self):
        converter = get_converter(RTD_HTML)
        assert isinstance(converter, ReadthedocsConverter)

    def test_returns_converter_for_deepwiki(self):
        converter = get_converter(DEEPWIKI_HTML)
        assert isinstance(converter, DeepwikiConverter)

    def test_raises_for_unknown(self):
        with pytest.raises(UnsupportedFrameworkError, match="Unsupported framework"):
            get_converter(HUGO_HTML)


# ── Framework name tests ─────────────────────────────────────────────────

class TestGetFrameworkName:
    """get_framework_name returns a readable string per framework."""

    def test_mkdocs_name(self):
        name = get_framework_name(MKDOCS_HTML)
        assert "mkdocs" in name
        assert "9.7.6" in name

    def test_readthedocs_name(self):
        name = get_framework_name(RTD_HTML)
        assert "sphinx-rtd" in name
        assert "docs" in name

    def test_deepwiki_name(self):
        name = get_framework_name(DEEPWIKI_HTML)
        assert "deepwiki" in name.lower()

    def test_unknown_name(self):
        name = get_framework_name(HUGO_HTML)
        assert name == "unknown"
