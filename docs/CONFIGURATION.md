# Allo Skills 配置指南

本文档列出所有需要额外配置才能使用的 skill。

## 配置总览

| Skill | 必须配置 | 可选配置 | 状态 |
|-------|----------|----------|------|
| `mingxue-kb-query` | SSH 连接 | — | ⚠️ 需配置 |
| `dongfang-enterprise-kb-query` | SSH 连接、Web UI | — | ⚠️ 需配置 |
| `pdf-to-markdown` | API URL、Token | — | ⚠️ 需配置 |
| `huiping-ppt-generator` | — | AI 图片生成 API | 🔵 可选 |
| `huiping-incremental-evaluator` | — | — | ✅ 开箱即用 |
| `huiping-report-review` | — | — | ✅ 开箱即用 |
| `huiping-data-analysis-coach` | — | — | ✅ 开箱即用 |
| `huiping-literature-guide` | — | — | ✅ 开箱即用 |
| `huiping-topic-advisor` | — | — | ✅ 开箱即用 |
| `huiping-html-deck` | — | — | ✅ 开箱即用 |
| 其他 15 个通用 skills | — | — | ✅ 开箱即用 |

## 详细配置

### 1. mingxue-kb-query（明学知识库查询）

通过 SSH 查询明学 RAGFlow 知识库。

```bash
export MINGXUE_SSH_HOST="<ssh-user>@<server-ip>"
export MINGXUE_SSH_PORT="<ssh-port>"
```

| 变量 | 说明 | 示例 |
|------|------|------|
| `MINGXUE_SSH_HOST` | SSH 用户@服务器地址 | `user@10.0.0.1` |
| `MINGXUE_SSH_PORT` | SSH 端口 | `10022` |

---

### 2. dongfang-enterprise-kb-query（东方电子企业知识库查询）

通过 SSH 查询东方电子 RAGFlow 知识库。

```bash
export DONGFANG_SSH_HOST="<ssh-user>@<server-ip>"
export DONGFANG_SSH_PORT="<ssh-port>"
export DONGFANG_WEB_UI="http://<server-ip>:<port>"
```

| 变量 | 说明 | 示例 |
|------|------|------|
| `DONGFANG_SSH_HOST` | SSH 用户@服务器地址 | `user@10.0.0.1` |
| `DONGFANG_SSH_PORT` | SSH 端口 | `10022` |
| `DONGFANG_WEB_UI` | Web Agentic Search UI 地址 | `http://10.0.0.1:18093` |

---

### 3. pdf-to-markdown（PDF 转 Markdown）

通过 PDF Parse API 将 PDF 转换为 Markdown。

```bash
export PDF_PARSE_BASE_URL="http://<server>:<port>"
export PDF_PARSE_TOKEN="<your-token>"
```

| 变量 | 说明 | 示例 |
|------|------|------|
| `PDF_PARSE_BASE_URL` | PDF Parse API 地址 | `http://10.0.0.1:18090` |
| `PDF_PARSE_TOKEN` | API 认证 token | （向管理员获取） |

---

### 4. huiping-ppt-generator（PPT 生成器，可选）

默认可使用，如需 AI 图片生成能力需配置：

```bash
# 复制环境变量模板
cp plugins/huiping-ppt-generator/skills/huiping-ppt-generator/.env.example \
   plugins/huiping-ppt-generator/skills/huiping-ppt-generator/.env
```

| 变量 | 说明 | 必须 |
|------|------|------|
| `IMAGE_BACKEND` | 图片生成后端 | 否（默认 `openai`） |
| `OPENAI_API_KEY` | OpenAI API Key（gpt-image-2） | 推荐 |
| `OPENAI_BASE_URL` | OpenAI API 地址 | 否（默认官方） |
| `GEMINI_API_KEY` | Gemini API Key（备选） | 可选 |
| `PEXELS_API_KEY` | Pexels 图片搜索（免费申请） | 可选 |
| `PIXABAY_API_KEY` | Pixabay 图片搜索（免费申请） | 可选 |

---

## 配置方式

### 方式一：Shell profile（推荐）

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
# Allo Skills 配置
export MINGXUE_SSH_HOST="..."
export MINGXUE_SSH_PORT="..."
export DONGFANG_SSH_HOST="..."
export DONGFANG_SSH_PORT="..."
export DONGFANG_WEB_UI="..."
export PDF_PARSE_BASE_URL="..."
export PDF_PARSE_TOKEN="..."
```

然后 `source ~/.zshrc` 生效。

### 方式二：项目级 .env

在项目根目录创建 `.env` 文件（已在 `.gitignore` 中）。

---

## 安全提醒

- 不要将 token、key、SSH 凭据提交到 git 仓库
- 不要在 SKILL.md 或代码中硬编码敏感信息
- 使用环境变量管理所有凭据
