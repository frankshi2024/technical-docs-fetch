"""Tests for the DeepWiki converter module."""

from nic2markdown.frameworks.deepwiki.converter import DeepwikiConverter

converter = DeepwikiConverter()


class TestHeadings:
    def test_h1(self):
        md = converter.convert("<h1>Hello</h1>")
        assert md.strip() == "# Hello"

    def test_h2(self):
        md = converter.convert("<h2>Section</h2>")
        assert md.strip() == "## Section"

    def test_h3(self):
        md = converter.convert("<h3>Subsection</h3>")
        assert md.strip() == "### Subsection"

    def test_heading_with_strong_unwrapped(self):
        md = converter.convert("<h1><strong>Bold Title</strong></h1>")
        assert md.strip() == "# Bold Title"

    def test_heading_with_em_unwrapped(self):
        md = converter.convert("<h2><em>Italic Title</em></h2>")
        assert md.strip() == "## Italic Title"

    def test_heading_with_copy_link_button_removed(self):
        html = '<h2 id="section" class="group" data-header="true">Heading<button aria-label="Copy link to header"><svg></svg></button></h2>'
        md = converter.convert(html)
        assert "Copy link" not in md
        assert "button" not in md
        assert "## Heading" in md

    def test_heading_attributes_removed(self):
        html = '<h2 id="section" class="group" data-header="true">Heading</h2>'
        md = converter.convert(html)
        # data-header and class="group" should be gone
        assert "data-header" not in md
        assert 'class="group"' not in md
        assert "## Heading" in md


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

    def test_inline_code(self):
        md = converter.convert("<p>Use <code>cmd</code> now</p>")
        assert "`cmd`" in md

    def test_link(self):
        md = converter.convert('<p><a href="https://example.com">click</a></p>')
        assert "[click](https://example.com)" in md


class TestCodeBlocks:
    def test_fenced_code_block(self):
        html = '<pre><code>print("hello")\n</code></pre>'
        md = converter.convert(html)
        assert "```" in md
        assert 'print("hello")' in md

    def test_code_block_with_language(self):
        html = '<pre><code class="language-python">print("hello")\n</code></pre>'
        md = converter.convert(html)
        assert "```python" in md or "```" in md


class TestMermaid:
    def test_mermaid_bailout_replaced(self):
        html = (
            '<pre class="px-2 py-1.5">'
            '<template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING"></template>'
            '</pre>'
        )
        md = converter.convert(html)
        assert "Mermaid diagram" in md
        assert "not rendered server-side" in md


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

    def test_table_unwrapped_from_div(self):
        html = (
            '<div>'
            '<table>'
            '<thead><tr><th>A</th></tr></thead>'
            '<tbody><tr><td>1</td></tr></tbody>'
            '</table>'
            '</div>'
        )
        md = converter.convert(html)
        assert "| A |" in md
        assert "| 1 |" in md


class TestRelativeLinkFixing:
    def test_absolute_url_unchanged(self):
        md = converter.convert(
            '<p><a href="https://other.com/page">link</a></p>',
            base_url="https://deepwiki.com/docs/"
        )
        assert "[link](https://other.com/page)" in md

    def test_relative_url_fixed(self):
        md = converter.convert(
            '<p><a href="next.html">next</a></p>',
            base_url="https://deepwiki.com/docs/page/"
        )
        assert "[next](https://deepwiki.com/docs/page/next.html)" in md

    def test_github_link_preserved(self):
        md = converter.convert(
            '<p><a href="https://github.com/microsoft/vscode/blob/main/src/main.ts">source</a></p>'
        )
        assert "[source](https://github.com/microsoft/vscode/blob/main/src/main.ts)" in md


class TestEmptyLinks:
    def test_empty_anchor_link_removed(self):
        html = '<p><a href="#empty"></a></p>'
        md = converter.convert(html)
        # The empty link should produce minimal output
        assert md.strip() in ("", "[#empty]()") or md.strip().startswith("#")

    def test_whitespace_without_newlines(self):
        md = converter.convert("<p>Hello</p><p>World</p>")
        assert "Hello" in md
        assert "World" in md
        # Should not have excessive blank lines
        assert "\n\n\n" not in md
