"""Tests for the Read the Docs converter module."""

from nic2markdown.frameworks.readthedocs.converter import ReadthedocsConverter

converter = ReadthedocsConverter()


class TestHeadings:
    def test_h1(self):
        md = converter.convert("<h1>Hello</h1>")
        assert md.strip() == "# Hello"

    def test_h2(self):
        md = converter.convert("<h2>Section</h2>")
        assert md.strip() == "## Section"

    def test_heading_with_strong_unwrapped(self):
        md = converter.convert("<h1><strong>Bold Title</strong></h1>")
        assert md.strip() == "# Bold Title"


class TestParagraphsAndInline:
    def test_paragraph(self):
        md = converter.convert("<p>Hello world</p>")
        assert md.strip() == "Hello world"

    def test_bold(self):
        md = converter.convert("<p><strong>bold</strong> text</p>")
        assert md.strip() == "**bold** text"

    def test_italic(self):
        md = converter.convert("<p><em>italic</em> text</p>")
        assert md.strip() == "*italic* text"

    def test_inline_code_basic(self):
        md = converter.convert("<p>Use <code>cmd</code> now</p>")
        assert "`cmd`" in md

    def test_inline_code_sphinx(self):
        """Sphinx pattern: <code class="docutils literal notranslate"><span class="pre">text</span></code>"""
        html = (
            '<p>File is <code class="docutils literal notranslate">'
            '<span class="pre">.readthedocs.yaml</span>'
            '</code></p>'
        )
        md = converter.convert(html)
        assert "`.readthedocs.yaml`" in md

    def test_inline_code_sphinx_multi_span(self):
        html = (
            '<code class="docutils literal notranslate">'
            '<span class="pre">404</span> '
            '<span class="pre">Not</span> '
            '<span class="pre">Found</span>'
            '</code>'
        )
        md = converter.convert(html)
        assert "`404 Not Found`" in md

    def test_link(self):
        md = converter.convert('<p><a href="https://example.com">click</a></p>')
        assert "[click](https://example.com)" in md


class TestCodeBlocks:
    def test_fenced_code_block(self):
        html = (
            '<div class="highlight highlight-yaml">'
            '<div class="highlight">'
            '<pre><span></span>version: 2\nname: test\n</pre>'
            '</div>'
            '</div>'
        )
        md = converter.convert(html)
        assert "```yaml" in md
        assert "version: 2" in md

    def test_code_block_with_linenos(self):
        html = (
            '<div class="highlight highlight-python">'
            '<div class="highlight">'
            '<pre><span></span><span class="linenos">1</span>print("hello")\n'
            '<span class="linenos">2</span>print("world")\n'
            '</pre>'
            '</div>'
            '</div>'
        )
        md = converter.convert(html)
        assert "```python" in md
        assert 'print("hello")' in md
        assert 'print("world")' in md
        assert "linenos" not in md

    def test_code_block_default_language(self):
        html = (
            '<div class="highlight highlight-default">'
            '<div class="highlight">'
            '<pre><span></span>some code\n</pre>'
            '</div>'
            '</div>'
        )
        md = converter.convert(html)
        assert "```" in md
        assert "some code" in md

    def test_code_block_simple_variant(self):
        """Variant: <div class="highlight-yaml notranslate"><div class="highlight">..."""
        html = (
            '<div class="highlight-yaml notranslate">'
            '<div class="highlight">'
            '<pre><span></span>version: 2\n</pre>'
            '</div>'
            '</div>'
        )
        md = converter.convert(html)
        assert "```yaml" in md
        assert "version: 2" in md


class TestAdmonitions:
    def test_note(self):
        html = (
            '<div class="admonition note">'
            '<p class="admonition-title">Note</p>'
            '<p>Some content.</p>'
            '</div>'
        )
        md = converter.convert(html)
        assert "> [!NOTE]" in md
        assert "**Note**" in md
        assert "Some content." in md

    def test_warning(self):
        html = (
            '<div class="admonition warning">'
            '<p class="admonition-title">Careful</p>'
            '<p>Watch out.</p>'
            '</div>'
        )
        md = converter.convert(html)
        assert "> [!WARNING]" in md
        assert "**Careful**" in md

    def test_danger(self):
        html = (
            '<div class="admonition danger">'
            '<p class="admonition-title">Danger</p>'
            '<p>Do not proceed.</p>'
            '</div>'
        )
        md = converter.convert(html)
        assert "> [!CAUTION]" in md

    def test_tip(self):
        html = (
            '<div class="admonition tip">'
            '<p class="admonition-title">Pro Tip</p>'
            '<p>Use this trick.</p>'
            '</div>'
        )
        md = converter.convert(html)
        assert "> [!TIP]" in md

    def test_seealso_as_note(self):
        html = (
            '<div class="admonition seealso">'
            '<p class="admonition-title">See also</p>'
            '<p>Related docs.</p>'
            '</div>'
        )
        md = converter.convert(html)
        # seealso is not in ADMONITION_MAP, defaults to NOTE
        assert "> [!NOTE]" in md


class TestHeaderlinkRemoval:
    def test_headerlink_removed(self):
        html = '<h1 id="test">Title<a class="headerlink" href="#test">&para;</a></h1>'
        md = converter.convert(html)
        assert "headerlink" not in md
        assert "&para;" not in md
        assert "# Title" in md


class TestTables:
    def test_simple_table(self):
        html = (
            '<table>'
            '<thead><tr><th>A</th><th>B</th></tr></thead>'
            '<tbody><tr><td>1</td><td>2</td></tr></tbody>'
            '</table>'
        )
        md = converter.convert(html)
        assert "| A | B |" in md
        assert "| 1 | 2 |" in md

    def test_table_wrapper_unwrapped(self):
        html = (
            '<div class="table-wrapper">'
            '<table>'
            '<thead><tr><th>Col</th></tr></thead>'
            '<tbody><tr><td>Val</td></tr></tbody>'
            '</table>'
            '</div>'
        )
        md = converter.convert(html)
        assert "| Col |" in md
        assert "| Val |" in md


class TestRelativeLinkFixing:
    def test_absolute_url_unchanged(self):
        md = converter.convert(
            '<p><a href="https://other.com/page">link</a></p>',
            base_url="https://example.com/docs/"
        )
        assert "[link](https://other.com/page)" in md

    def test_relative_url_fixed(self):
        md = converter.convert(
            '<p><a href="next.html">next</a></p>',
            base_url="https://example.com/docs/page/"
        )
        assert "[next](https://example.com/docs/page/next.html)" in md
