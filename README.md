# course-to-obsidian

把公开课程的教材、讲义、习题和作业整理成适合 Obsidian 阅读的 Markdown 学习书的 Codex skill。

支持官方资料与课程版本核对、可靠中文译本接入、中英对照、学习路径、作业导航、便携书稿，以及可选的 Obsidian 代码阅读优化。以来源与许可允许的范围收录资料，明确区分正文、原创导读与在线题目入口。

## 安装

需要已安装 Codex，并能访问此仓库。私有仓库需要先使用自己的 GitHub 账号完成 Git 身份认证。

```bash
git clone https://github.com/iceBear662/course-to-obsidian.git "${CODEX_HOME:-$HOME/.codex}/skills/course-to-obsidian"
```

如果目标目录已经存在，先检查已有内容，避免覆盖本地修改。安装后重新打开 Codex 会话，使其发现 skill。

## 使用

在 Codex 中指定 skill、课程和输出位置，例如：

> 使用 $course-to-obsidian，把 CS61A 资料完整的最近一期整理成 Obsidian 学习书。需要教材完整中文版与英文对照、官方作业导航、学习进度页，并优化代码阅读效果。输出到我指定的笔记库。

也可以只生成书稿，不修改 Obsidian 配置。学期、语言、输出目录、是否安装显示插件均按当前需求决定，不绑定示例中的某一学期或本机路径。

## 仓库内容

| 路径 | 用途 |
| --- | --- |
| `SKILL.md` | 主要工作流程与交付要求 |
| `agents/openai.yaml` | Codex 展示信息与默认提示 |
| `references/sources-and-translation.md` | 来源、译本、许可与转换方法 |
| `references/obsidian-code.md` | 代码阅读插件选型与配置边界 |
| `references/book-audit.md` | 检查工具与可选清单格式 |
| `assets/course-code-reading.css` | 限定到书页的 Obsidian 代码样式 |
| `scripts/audit_book.py` | Markdown 链接、围栏与可选覆盖清单检查 |
| `scripts/requirements.txt` | 检查工具的 Python 依赖 |

本仓库提供整理方法与工具，不附带课程教材、译本文本、作业答案或第三方插件源码。

## 可选：检查书稿

在仓库目录中创建隔离的 Python 环境并安装解析依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/audit_book.py /absolute/path/to/course-book
```

需要检查章节、语言版本和代码保真时，按 [清单格式说明](references/book-audit.md) 提供 manifest：

```bash
.venv/bin/python scripts/audit_book.py /absolute/path/to/course-book \
  --manifest /absolute/path/to/book-manifest.json \
  --report /absolute/path/to/audit.json
```

检查器不联网、不执行教材代码，也不判断译文准确度或验证插件视觉效果。默认只读，只有指定 `--report` 才写出报告。Obsidian 阅读本身不需要安装这些 Python 依赖。

## 来源与收录范围

每次生成学习书都应重新核对官方版本、译本修订与许可。公开可访问不代表允许全文转载；插件也需要按实际版本和用户授权选用。完整正文、有限摘录、原创说明和在线导航应在交付中明确标识。
