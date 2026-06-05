"""Tests for the Read the Docs validator module."""

from nic2markdown.frameworks.readthedocs.validator import detect, get_version

RTD_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="readthedocs-addons-api-version" content="1">
    <meta name="readthedocs-project-slug" content="docs">
    <meta name="readthedocs-version-slug" content="stable">
    <title>Test</title>
</head>
<body><p>Hello</p></body>
</html>"""

RTD_HTML_SLUG_ONLY = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="readthedocs-addons-api-version" content="1">
    <title>Test</title>
</head>
<body><p>Hello</p></body>
</html>"""

RTD_HTML_PROJECT_ONLY = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="readthedocs-project-slug" content="myproject">
    <title>Test</title>
</head>
<body><p>Hello</p></body>
</html>"""

NON_RTD_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="generator" content="Hugo 0.120.0">
    <title>Test</title>
</head>
<body><p>Hello</p></body>
</html>"""

NO_META_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test</title>
</head>
<body><p>Hello</p></body>
</html>"""


class TestDetect:
    def test_rtd_with_all_meta(self):
        assert detect(RTD_HTML) is True

    def test_rtd_with_addons_only(self):
        assert detect(RTD_HTML_SLUG_ONLY) is True

    def test_rtd_with_project_only(self):
        assert detect(RTD_HTML_PROJECT_ONLY) is True

    def test_non_rtd(self):
        assert detect(NON_RTD_HTML) is False

    def test_no_meta(self):
        assert detect(NO_META_HTML) is False


class TestGetVersion:
    def test_full_version(self):
        version = get_version(RTD_HTML)
        assert version == "sphinx-rtd (docs/stable)"

    def test_addons_only(self):
        version = get_version(RTD_HTML_SLUG_ONLY)
        assert version == "sphinx-rtd"

    def test_project_only(self):
        version = get_version(RTD_HTML_PROJECT_ONLY)
        assert version == "sphinx-rtd (myproject)"

    def test_returns_none_for_no_meta(self):
        version = get_version(NO_META_HTML)
        assert version is None
