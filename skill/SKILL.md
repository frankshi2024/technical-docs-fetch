---
name: nic2markdown
description: |
  Convert documentation pages (MkDocs Material, Read the Docs / Sphinx, 
  DeepWiki) to GitHub-compatible Markdown. Use this skill whenever the 
  user wants to save, read, or process a documentation page as clean 
  Markdown — especially for coding agents where browsing raw HTML pages 
  is token-heavy and error-prone.
---

# nic2markdown

Convert documentation pages into clean GitHub-Flavored Markdown —
ideal for human reading and agent consumption.

Supports **MkDocs Material**, **Read the Docs** (Sphinx), and **DeepWiki**.

## Usage

```bash
# Basic conversion — output saved to output/<stem>.<yyyymmddhhmmss>.md
nic2markdown <url>

# Also extract sidebar navigation links
nic2markdown <url> -s

# Custom output directory
nic2markdown <url> -o ./my-notes
```

## What it handles

- **Admonitions** (note, warning, tip, danger, ...) → GFM alerts (`> [!NOTE]`)
- **Code blocks** with syntax highlighting info preserved
- **Tables**, task lists, footnotes
- **MathJax** → `$` / `$$` delimiters
- **Relative links** → resolved to absolute URLs
- **Sidebar navigation** (optional, with `-s` flag)

## Health check

```bash
nic2markdown --help
```

## Supported frameworks

| Framework | Status |
|-----------|--------|
| MkDocs Material | ✅ Supported |
| Read the Docs (Sphinx) | ✅ Supported |
| DeepWiki | ✅ Supported |

## Installation

```bash
# One-liner (Linux / macOS / Git Bash / WSL)
curl -fsSL https://raw.githubusercontent.com/frankshi2024/technical-docs-fetch/main/install.sh | bash

# Windows PowerShell
iwr -useb https://raw.githubusercontent.com/frankshi2024/technical-docs-fetch/main/install.ps1 | iex
```

Requires **uv** (https://docs.astral.sh/uv/).
