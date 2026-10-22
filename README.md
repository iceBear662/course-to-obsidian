# course-to-obsidian

把公开课程的教材、讲义、习题和作业整理成适合 Obsidian 阅读的 Markdown 学习书的通用 AI skill / 工作流程。

支持官方资料与课程版本核对、可靠中文译本接入、中英对照、学习路径、作业导航、便携书稿，以及可选的 Obsidian 代码阅读优化。以来源与许可允许的范围收录资料，明确区分正文、原创导读与在线题目入口。

## 在不同 AI 工具中使用

核心说明是普通 Markdown，不依赖某一家模型或专属 API。可以按当前工具的能力选择使用方式：

- **支持本地 skill 的工具**：下载或克隆完整仓库，按该工具的要求放入 skill 目录或导入。保留 `references/`、`scripts/` 和 `assets/` 的相对路径。
- **能读取项目文件的 AI 助手**：把仓库放进可访问的工作目录，让助手先读 `SKILL.md`，再按任务读取其中链接的参考文件，无需专门安装 skill。
- **普通 AI 对话**：把 `SKILL.md` 和任务所需的参考文件作为附件或文本提供，并发送下面的通用提示。需要检查书稿时一并提供 `references/book-audit.md`；需要优化代码阅读时提供 `references/obsidian-code.md`。

```bash
git clone https://github.com/iceBear662/course-to-obsidian.git
```

通用提示示例：

> 请按 course-to-obsidian/SKILL.md 的流程，把 CS61A 资料完整的最近一期整理成 Obsidian 学习书。需要教材完整中文版与英文对照、官方作业导航和学习进度页，并优化代码阅读效果。先读取相关参考文件，核对来源和许可，再整理书稿；输出到我指定的位置。

如果 AI 无法联网，请给它官方来源、译本和课程文件；如果无法写本地文件，就分章输出 Markdown，由你保存；如果无法运行 Python，检查脚本可以由你在本机手动执行。没有应用操作能力时，输出插件和样式的配置步骤，由你在 Obsidian 中应用。只把实际生成、保存或启用的结果标记为完成。

`agents/openai.yaml` 是可选的 Codex 展示配置，其他工具可以忽略；核心流程、样式和 Python 检查器都能独立使用。不同工具的自动发现、附件读取和脚本执行能力各异，导入方式以所用工具为准。

### 可选：安装到 Codex

```bash
git clone https://github.com/iceBear662/course-to-obsidian.git "${CODEX_HOME:-$HOME/.codex}/skills/course-to-obsidian"
```

如果目标目录已经存在，先检查已有内容，避免覆盖本地修改。安装后重新打开 Codex 会话，使其发现 skill。在 Codex 中可用 `$course-to-obsidian` 调用；其他工具使用上面的通用提示即可。

也可以只生成书稿，不修改 Obsidian 配置。学期、语言、输出目录、是否安装显示插件均按当前需求决定，不绑定示例中的某一学期或本机路径。

## 仓库内容

| 路径 | 用途 |
| --- | --- |
| `SKILL.md` | 主要工作流程与交付要求 |
| `agents/openai.yaml` | 可选的 Codex 展示信息与默认提示，其他工具可忽略 |
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
