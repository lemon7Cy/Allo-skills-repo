# Allo Skills 配置指南

本文档列出所有需要额外配置才能使用的 skill。

## 配置总览

| Skill | 必须配置 | 可选配置 | 状态 |
|-------|----------|----------|------|
| `mingxue-kb-query` | `MINGXUE_API_TOKEN` | — | ⚠️ 需配置 |
| `dongfang-enterprise-kb-query` | `DONGFANG_API_TOKEN` | — | ⚠️ 需配置 |
| `pdf-to-markdown` | `PDF_PARSE_TOKEN` | — | ⚠️ 需配置 |
| `huiping-ppt-generator` | — | `OPENAI_API_KEY` 等 | 🔵 可选 |
| 其他 20 个 skills | — | — | ✅ 开箱即用 |

## 凭据管理方式

Allo Desktop 通过 `settings.json` 管理 skill 凭据，**不依赖环境变量**：

```json
{
  "credentials": {
    "skills": {
      "mingxue-kb-query": {
        "MINGXUE_API_TOKEN": "..."
      },
      "dongfang-enterprise-kb-query": {
        "DONGFANG_API_TOKEN": "..."
      },
      "pdf-to-markdown": {
        "PDF_PARSE_TOKEN": "..."
      }
    }
  }
}
```

每个 skill 的 `SKILL.md` frontmatter 和 `marketplace.json` 都声明了 `required_env`/`optional_env`/`credentials`，Allo Desktop 会自动检查状态：
- 无声明的 key → `not_configurable`
- 有 required key 未配置 → `missing_required_credentials`
- required 已配、optional 未配 → `missing_optional_credentials`
- 全部就绪 → `ready`

## 需要配置的 Skills

### 1. mingxue-kb-query（明学知识库查询）

| Key | 说明 | 必须 |
|-----|------|------|
| `MINGXUE_API_TOKEN` | 明学 RAGFlow 知识库认证 token | ✅ |

API 地址已内置：`http://221.0.79.251:18091`

---

### 2. dongfang-enterprise-kb-query（东方电子企业知识库查询）

| Key | 说明 | 必须 |
|-----|------|------|
| `DONGFANG_API_TOKEN` | 东方电子 RAGFlow 知识库认证 token | ✅ |

API 地址已内置：`http://221.0.79.251:18093`

---

### 3. pdf-to-markdown（PDF 转 Markdown）

| Key | 说明 | 必须 |
|-----|------|------|
| `PDF_PARSE_TOKEN` | PDF Parse API 认证 token | ✅ |

API 地址已内置：`http://221.0.79.251:18090`

---

### 4. huiping-ppt-generator（PPT 生成器，可选）

| Key | 说明 | 必须 |
|-----|------|------|
| `GPT_IMAGE_API_KEY` | GPT Image 2 API Key（图片生成） | 可选 |

API 地址已内置：`http://221.0.79.251:8088/v1`（gpt-image-2）

不配置也能使用，图片部分会用占位图。

---

## 安全提醒

- 不要将 token、key 提交到 git 仓库
- 不要在 SKILL.md 或代码中硬编码 token
- Allo Desktop 自动管理凭据存储
