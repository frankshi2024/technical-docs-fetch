# technical-docs-fetch

> 将文档网站页面转换为干净的 GitHub 兼容 Markdown — 给人看，也给 coding agent 看。

---

## 这是什么？

**technical-docs-fetch** 是一个 CLI 工具，输入一个文档网页的 URL，输出干净的 GFM Markdown 文件。

它解决的问题：当你（或你的 coding agent）需要阅读在线技术文档时，直接抓取 HTML 既费 token 又容易出错。这个工具把网页还原成结构化的 Markdown，保留代码块、表格、提示框等语义结构。

## 支持的框架

| 框架 | 状态 |
|------|------|
| **MkDocs Material** | ✅ 完整支持 |
| **Read the Docs** (Sphinx) | ✅ 完整支持 |
| **DeepWiki** | ✅ 完整支持 |
| 更多框架 | 🚧 欢迎提 Issue |

## 快速开始

### 安装

**前置要求：[uv](https://docs.astral.sh/uv/)**

**GitHub（推荐）**

```bash
# Linux / macOS / Git Bash / WSL
curl -fsSL https://raw.githubusercontent.com/frankshi2024/technical-docs-fetch/main/install.sh | bash

# Windows PowerShell
iwr -useb https://raw.githubusercontent.com/frankshi2024/technical-docs-fetch/main/install.ps1 | iex
```

**Gitee 镜像（国内网络友好）**

```bash
# Linux / macOS / Git Bash / WSL
curl -fsSL https://gitee.com/frankshi2024/technical-docs-fetch/raw/main/install-gitee.sh | bash

# Windows PowerShell
iwr -useb https://gitee.com/frankshi2024/technical-docs-fetch/raw/main/install-gitee.ps1 | iex
```

### 使用

```bash
# 基本转换 → output/<stem>.<yyyymmddhhmmss>.md
technical-docs-fetch https://soc.ustc.edu.cn/COD/lab5/

# 同时提取侧边栏导航链接
technical-docs-fetch https://soc.ustc.edu.cn/COD/lab5/ -s

# 指定输出目录
technical-docs-fetch https://soc.ustc.edu.cn/Digital/2025/lab1/intro/ -o ./notes -s

# Read the Docs 页面
technical-docs-fetch https://docs.readthedocs.com/platform/stable/config-file/v2.html -s

# DeepWiki 页面
technical-docs-fetch https://deepwiki.com/microsoft/vscode -s

# 不支持的框架 → 报错退出
technical-docs-fetch https://example.com
# Error: Unsupported framework.
```

## 功能特性

| 原始结构 | 转换结果 |
|---------|---------|
| `<div class="admonition note">` (Sphinx / MkDocs) | `> [!NOTE]` (GFM Alert) |
| `<div class="admonition warning">` | `> [!WARNING]` |
| `<div class="admonition danger">` | `> [!CAUTION]` |
| `<div class="admonition tip/success">` | `> [!TIP]` |
| `<div class="admonition question">` | `> [!IMPORTANT]` |
| `<div class="highlight"><pre><code>` | ` ``` ` 围栏代码块 |
| 相对链接 | 补全为绝对 URL |
| 侧边栏导航 (`-s`) | 嵌套 Markdown 列表 |
| Task list | `- [ ]` / `- [x]` |
| MathJax | `$` / `$$` 公式 |
| Tabbed set (MkDocs) | 带标签的多代码块 |

---

## 开发

```bash
git clone https://github.com/frankshi2024/technical-docs-fetch.git
# 或国内镜像：git clone https://gitee.com/frankshi2024/technical-docs-fetch.git
cd technical-docs-fetch
uv sync
uv run pytest -v    # 147 个测试
```

详细架构和扩展指南见 **[TECH.md](TECH.md)**。

---

## 背景

本项目起源于：开发者在**使用 coding agent 理解、完成和 debug 课程实验作业**时，发现在 fetch 实验文档时，无论使用直接下载 HTML、借助 MCP 截图保存还是内置的其他工具，都存在形式冗余、消耗 token 较多乃至识别错误的问题。

调查发现，**中科大大部分计算机实验课程文档由 MkDocs Material 开发**。这也意味着，本就由 Markdown 生成的网页，最好的处理方法也是将其回归为 Markdown — 本项目应运而生。

后续扩展到支持 Read the Docs（Sphinx）和 DeepWiki，覆盖更多主流文档框架。

> ⚠️ 本工具不作为爬虫相关工具使用，仅提供有限数据清洗功能，不承担有关法律责任。

---

## 特别鸣谢

**DeepSeek-V4-Pro** 承担了本项目绝大部分代码编写工作。开发者和他度过了一段很好的 vibe coding 开发时光 🤖✨
