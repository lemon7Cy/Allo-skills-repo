---
name: dongfang-enterprise-kb-query
description: 查询东方电子企业知识库，面向配电、调度云化、储能新能源、微电网、综合能源、虚拟电厂、智慧城市、港口、石油石化等业务场景，并返回带出处的检索答案。当用户提到东方、东方电子、企业知识库或相关业务场景时使用。
tools: []
version: "1.0.0"
author: allo-official
required_env:
  - DONGFANG_API_TOKEN
optional_env: []
credentials:
  - key: DONGFANG_API_TOKEN
    label: 东方电子知识库 API Token
    description: 用于查询东方电子 RAGFlow 知识库的认证 token。
    required: true
    secret: true
---

# 东方电子企业知识库查询

## 这个 Skill 做什么

使用东方电子 RAGFlow 知识库 HTTP API 进行检索。**不要**将东方电子问题路由到明学知识库；明学是独立的电池/SOC/SOH 学术知识库。

## 何时使用

- 用户提到 `东方`、`东方电子`、`东方业务资料库`、`企业知识库`
- 主题包括：配电、配电自动化、调度及云化、E8000、储能、新能源、微电网、综合能源、虚拟电厂、威思顿、海颐、国网中电、智慧城市、港口、石油石化、智慧矿山
- 用户要求"查一下"、"检索"、"带出处"、"根据知识库回答"

**不要用于**：明学电池/SOC/SOH/RUL/Kalman 问题（用 `mingxue-kb-query`）

## API 配置

```text
Search API: http://221.0.79.251:18093/api/search
Ask API:    http://221.0.79.251:18093/api/ask  (需额外配置 LLM)
```

Token 通过环境变量传入：

```bash
export DONGFANG_API_TOKEN="<your-token>"
```

## 检索命令（search）

```bash
curl -sS -X POST "http://221.0.79.251:18093/api/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DONGFANG_API_TOKEN" \
  -d '{"question": "QUESTION", "top_k": 5}'
```

参数说明：
- `question`：检索问题（必填）
- `top_k`：返回结果数量（默认 5，广泛证据用 8）
- `mode`：`answer`（默认）或 `research`（文献发现）

## 问答命令（ask，可选）

Ask API 需要额外配置 LLM 环境变量，未配置时不可用。优先使用 search API。

## 查询规划

不要将不相关的词塞入一个查询。使用聚焦的证据查询。

建议聚类：

| 需求 | 查询聚焦 |
|------|----------|
| 产品概述 | `东方电子 产品名 定位 功能 特点` |
| 解决方案模块 | `东方电子 解决方案 模块 架构 功能` |
| 应用场景 | `东方电子 场景 应用 案例 行业` |
| 配电 | `东方电子 配电 配电自动化 主站 终端 环网箱` |
| 调度/云化 | `东方电子 调度 云化 E8000 主站 新型电力系统` |
| 储能/新能源 | `东方电子 储能 新能源 微电网 SVG 岸电` |
| 综合能源/虚拟电厂 | `东方电子 综合能源 虚拟电厂 负荷聚合 源网荷储` |
| 分子公司 | `威思顿 海颐 国网中电 东方电子 业务 产品` |

用户问 3+ 业务线时，拆分为 2-4 个聚焦查询再综合。

## 回答格式

返回：
1. 简短结论
2. 基于证据的解释（仅使用返回的 `chunks`）
3. 来源列表：`rank`、`document`、`section_type`、`similarity`
4. 资产来源列表（有用时）：`asset_id`、`asset_type`、`source_doc`、`similarity`

示例来源行：

```text
出处：rank #1, section=body, 东方电子配电画册2025版.md, sim=0.511
```

检索证据弱时如实说明。不要用通用行业知识填补空白。

## 常见错误

- 对东方问题使用 mingxue API → 用东方电子 API
- 用户要求知识库答案时先调用公开 Web 搜索
- 将通用微电网场景当作东方特有（无返回证据时）
- 声称图片细节（除非资产元数据明确支持）
- 打印 API keys、查询 tokens 或 RAGFlow 凭据

## 与其他慧评 Skill 的配合

```
用户提问（东方电子相关）
       ↓
dongfang-enterprise-kb-query → 查询企业知识库
       ↓
带出处的答案 → 用于课程报告、研究、方案设计
```
