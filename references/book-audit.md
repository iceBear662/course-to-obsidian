# 核对工具

`scripts/audit_book.py` 是只读检查器。使用已有合适的 Python 环境；如缺解析库，在隔离环境中安装 `scripts/requirements.txt`。环境位置由当前运行环境发现，不依赖某次任务的临时虚拟环境。

```bash
python scripts/audit_book.py /absolute/path/to/course-book
python scripts/audit_book.py /absolute/path/to/course-book --manifest /absolute/path/to/book-manifest.json --report /absolute/path/to/audit.json
```

从 skill 目录运行，或把脚本路径写为绝对路径。退出码 0 表示已支持的检查通过，1 表示检查失败，2 表示参数/环境错误。默认只向标准输出写 JSON；指定 `--report` 才创建报告文件。

检查内容：标准 Markdown 的相对链接和图片目标、未闭合围栏、未标语言的非空代码块（警告），以及可选清单中的本地资源、章节覆盖、文件摘要、代码正文摘要与小节编号。

不会抓取网址、检查在线播放、运行书里的代码、判断翻译准确度或验证 Obsidian 插件。Wiki 链接、页内锚点和视觉效果另作针对性检查。不要把该脚本通过称为整本教材已审校。

## 可选来源/覆盖清单

字段可以扩展。清单中的 `path` 相对书稿根目录；`offline` 条目必须有本地文件，`online` 与 `unavailable` 明确标记但不计作离线覆盖。每个条目使用唯一 `id`。

```json
{
  "course": "示例课程",
  "edition": "核对后的课程版本",
  "captured": "YYYY-MM-DD",
  "sources": [
    {"url": "https://example.edu/course/", "kind": "official", "license": "已核对的许可依据"}
  ],
  "items": [
    {"id": "textbook-1.1-en", "kind": "textbook", "section_id": "1.1", "language": "en", "availability": "offline", "path": "教材英文/1.1.md", "subsection_ids": ["1.1.1", "1.1.2"]},
    {"id": "textbook-1.1-zh", "kind": "textbook", "section_id": "1.1", "language": "zh", "availability": "offline", "path": "教材中文/1.1.md", "subsection_ids": ["1.1.1", "1.1.2"]},
    {"id": "lab-01", "kind": "lab", "language": "en", "availability": "online", "source_url": "https://example.edu/course/lab01/"}
  ],
  "coverage_groups": [
    {"kind": "textbook", "languages": ["en", "zh"], "section_ids": ["1.1"]}
  ]
}
```

若要验证排版没有改动程序，将**转换前**源文件的代码块摘要写入对应条目的 `code_sha256`，再检查转换后的文件。摘要只包含围栏正文，不包含语言标签；可以允许统一 `py` 为 `python`，但不会放过缩进和程序内容变化。

构建脚本可从 `scripts/audit_book.py` 导入 `code_digest(text)` 来计算摘要。函数使用 markdown-it 的围栏正文列表，以 `json.dumps(..., ensure_ascii=False, separators=(",", ":"))` 编码，再计算 UTF-8 SHA-256。不要用转换后的代码给自己重新生成“预期摘要”，否则失去保真检查意义。

文件级 `sha256` 可用于需要固定原始资源的条目；不要给允许用户写笔记的任务卡或进度页锁定文件摘要。`subsection_ids` 对照正文标题里的节号，证明结构覆盖，不证明逐段完整或译文质量。
