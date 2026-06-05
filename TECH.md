# 技术文档

## 架构

```
URL 输入 → fetcher（HTTP 下载）→ gateway（框架检测/路由）→ framework converter → GFM Markdown
                                        ├── validator（框架识别）
                                        ├── extractor（正文提取）
                                        ├── converter（HTML→MD）
                                        └── sidebar（侧边栏链接）
```

### 管道流程

1. **`fetcher.py`** — 通过 httpx 下载 HTML，跟踪重定向，返回 `(html_text, final_url)`
2. **`gateway.py`** — 依次调用各 converter 的 `detect()` 方法，找到匹配的框架，分发请求
3. **framework converter** — 每个框架实现 `BaseConverter` 的 4 个接口（见下文）
4. **`writer.py`** — 以时间戳命名输出到 `output/` 目录

### 模块索引

| 模块 | 职责 |
|------|------|
| `cli.py` | argparse CLI 入口，串联整个管道 |
| `fetcher.py` | HTTP 请求 + 重定向跟踪 |
| `gateway.py` | 框架检测 + 路由分发 |
| `writer.py` | 输出 Markdown 到文件 |
| `frameworks/base.py` | `BaseConverter` 抽象基类 + `SidebarLink` dataclass |
| `frameworks/mkdocs_material/` | MkDocs Material 框架实现 |
| `frameworks/readthedocs/` | Read the Docs (Sphinx) 框架实现 |
| `frameworks/deepwiki/` | DeepWiki 框架实现 |

---

## 新增框架指南

只需 3 步：

### 1. 在 `frameworks/` 下新建子包

```
frameworks/
└── my_framework/
    ├── __init__.py       # 空文件
    ├── validator.py      # detect(html) -> bool, get_version(html) -> str|None
    ├── extractor.py      # 从完整 HTML 中提取正文内容
    ├── converter.py      # HTML → GFM Markdown，实现 BaseConverter
    └── sidebar.py        # 提取侧边栏导航链接
```

### 2. 实现 `BaseConverter` 的 4 个方法

```python
from ..base import BaseConverter, SidebarLink

class MyFrameworkConverter(BaseConverter):

    @staticmethod
    def detect(html: str) -> bool:
        """检测 HTML 是否由本框架生成。"""
        ...

    def extract_article(self, html: str, base_url: str) -> str:
        """查找并返回正文内容的 inner HTML。"""
        ...

    def convert(self, article_html: str, base_url: str = "") -> str:
        """将正文 HTML 转换为 GFM Markdown。"""
        ...

    def extract_sidebar_links(self, html: str, base_url: str) -> list[SidebarLink]:
        """提取侧边栏导航链接及层级信息。"""
        ...
```

### 3. 在 `gateway.py` 注册

```python
from .frameworks.my_framework.converter import MyFrameworkConverter

_CONVERTERS: list[type[BaseConverter]] = [
    MkdocsMaterialConverter,
    ReadthedocsConverter,
    DeepwikiConverter,
    MyFrameworkConverter,  # ← 添加这行
]
```

同时在 `_CONVERTER_NAME_MAP` 和 `get_framework_name()` 中添加对应的版本提取逻辑。

---

## 各框架转换详情

### MkDocs Material

- **检测**: `<meta name="generator" content="mkdocs-...">`
- **正文**: `<article class="md-content__inner md-typeset">`
- **特殊处理**: Admonitions (11 种类型 → GFM alerts)、Arithmatex (MathJax)、Tabbed sets、Task lists、Footnotes
- **侧边栏**: `<nav class="md-nav--primary">`，从 `data-md-level` 获取层级

### Read the Docs (Sphinx)

- **检测**: `<meta name="readthedocs-addons-api-version">` 或 `<meta name="readthedocs-project-slug">`
- **正文**: `<div role="main">`
- **特殊处理**: Admonitions（与 MkDocs 类似）、`highlight-*` 代码块（语言提取）、`<span class="pre">` 内联代码、`<div class="table-wrapper">` 表格包裹
- **侧边栏**: `<li class="toctree-lN">`，从 class 名获取层级

### DeepWiki

- **检测**: `<script type="application/ld+json">` 中 `"publisher":{"name":"DeepWiki"}`
- **正文**: `h1[data-header="true"]` + 向上找到最接近的包含所有内容标题的容器 `<div>`
- **特殊处理**: 标题中的 copy-link 按钮和 SVG 图标去除、`<template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING">` Mermaid 图表替换为注释、`<div>` 包裹的表格解包
- **侧边栏**: 右侧 TOC 的 `a[href^="#"]` 锚点链接，根据目标标题层级推断嵌套深度

---

## 测试

```bash
uv run pytest -v    # 147 个测试
```

测试结构：

```
tests/
├── test_gateway.py              # 框架检测和路由
└── frameworks/
    ├── mkdocs_material/         # validator, extractor, converter, sidebar
    ├── readthedocs/             # validator, extractor, converter, sidebar
    └── deepwiki/                # validator, extractor, converter, sidebar
```

每个框架的测试覆盖：
- `test_validator.py` — 检测正例和反例
- `test_extractor.py` — 正文提取、噪音去除、相对链接修复、错误处理
- `test_converter.py` — 标题、段落、代码块、提示框、表格、链接
- `test_sidebar.py` — 链接提取、层级、格式化
