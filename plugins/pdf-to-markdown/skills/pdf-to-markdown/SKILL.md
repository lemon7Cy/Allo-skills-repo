---
name: pdf-to-markdown
description: 将 PDF 文件转换为 Markdown，支持同步/异步模式、图片/表格保留、RAG 归档。当用户需要转换 PDF 为 Markdown、处理 MinerU 归档、保留图片表格、或为 RAG 准备解析后的 PDF 输出时使用。
tools: []
version: "1.0.0"
author: allo-official
required_env:
  - PDF_PARSE_TOKEN
optional_env: []
credentials:
  - key: PDF_PARSE_TOKEN
    label: PDF Parse API Token
    description: 用于调用 PDF Parse API 将 PDF 转换为 Markdown 的认证 token。
    required: true
    secret: true
---

# PDF 转 Markdown

## 这个 Skill 做什么

通过 PDF Parse API 将 PDF 转换为 Markdown，支持：
- 📄 **同步模式** — 小 PDF（≤20 页）即时返回 Markdown
- ⚡ **异步模式** — 大 PDF（≤100 页）后台处理
- 📦 **MinerU 归档** — 保留图片、表格、布局资产
- 🔍 **RAG 就绪** — 输出可直接用于知识库检索

## API 配置

```text
Base URL: http://221.0.79.251:18090
```

Token 通过环境变量传入：

```bash
export PDF_PARSE_TOKEN="<your-token>"
```

## 端点选择

| 场景 | 端点 | 说明 |
|------|------|------|
| 健康检查 | `GET /health` | 确认服务和限制 |
| PDF ≤20 页，快速预览 | `POST /pdf/markdown` | 同步返回 JSON `{markdown}` |
| PDF ≤100 页，默认/生产 | `POST /pdf/jobs` | 异步任务避免超时 |
| PDF >100 页 | 先拆分 | 服务拒绝超大任务 |
| 需要图片/表格/布局资产 | `GET /pdf/jobs/<id>/archive` | 保留 MinerU zip |

限制：同步 ≤20 页，异步 ≤100 页，上传 ≤200 MB。

## 同步模式（小 PDF）

```bash
curl -sS -X POST "http://221.0.79.251:18090/pdf/markdown" \
  -H "Authorization: Bearer $PDF_PARSE_TOKEN" \
  -F "file=@/path/to/input.pdf" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["markdown"])' \
  > output.md
```

验证：输出文件存在、非空、包含预期标题/表格。

## 异步模式（大 PDF）

**提交任务**：
```bash
curl -sS -X POST "http://221.0.79.251:18090/pdf/jobs" \
  -H "Authorization: Bearer $PDF_PARSE_TOKEN" \
  -F "file=@/path/to/input.pdf"
```

**轮询状态**：
```bash
curl -sS -H "Authorization: Bearer $PDF_PARSE_TOKEN" \
  "http://221.0.79.251:18090/pdf/jobs/<job_id>"
```

**下载 Markdown**：
```bash
curl -sS -H "Authorization: Bearer $PDF_PARSE_TOKEN" \
  "http://221.0.79.251:18090/pdf/jobs/<job_id>/markdown" \
  -o output.md
```

**下载归档（需要资产时）**：
```bash
curl -sS -H "Authorization: Bearer $PDF_PARSE_TOKEN" \
  "http://221.0.79.251:18090/pdf/jobs/<job_id>/archive" \
  -o mineru_output.zip
```

## 归档规则

用于 RAG、评价或资产提取时，保存：

```
source.pdf
mineru_output.zip
extracted/              # 保留原始 zip 目录结构
document.md             # 选定的 Markdown
metadata.json           # 源文件、job_id、页数、时间戳、路径
```

不要扁平化目录、重命名图片、重写相对链接或丢弃归档——除非用户只需要文本预览。

## 大 PDF 处理（>100 页）

1. 按目录/章节拆分；否则用稳定页码范围
2. 保持范围 ≤100 页；密集扫描/表格多的 PDF 用 10-30 页
3. 每部分作为异步任务提交
4. 保存每部分的 PDF、任务状态、Markdown、归档和清单行
5. 所有部分完成后才拼接 Markdown，保持页码顺序

## 常见错误

| 错误 | 正确做法 |
|------|----------|
| 猜端点名 | 只用 `/health`、`/pdf/markdown`、`/pdf/jobs`、`/pdf/jobs/<id>/markdown`、`/archive` |
| 大 PDF 用同步 | 先用异步或拆分 |
| RAG 只存 Markdown | 也要下载归档 |
| 丢失图片链接 | 保留 MinerU 目录结构 |
| 只看 HTTP 200 | 检查 JSON `status`、文件大小、内容预览 |
| 上传 >100 页 | 先拆分再提交 |

## 转换后验证

报告以下信息：

```
输入路径
使用的端点
页数
耗时或任务状态
Markdown 路径
归档路径（如有）
前几行 Markdown 预览
```

## 与其他慧评 Skill 的配合

```
课程报告 PDF
       ↓
pdf-to-markdown → 转换为 Markdown + MinerU 归档
       ↓
mingxue-kb-query → 基于 Markdown 内容查询知识库
huiping-incremental-evaluator → 基于内容生成六维评分
huiping-ppt-generator → 基于内容生成演示稿
```

## 资源文件

```
pdf-to-markdown/
└── SKILL.md ← 你正在读
```

本 skill 是纯 API 调用，无本地脚本依赖。
