---
name: maas-observability
description: Use when the user requests MaaS platform observability data including overview stats, model usage, provider statistics, pool statistics, or system health checks.
tools: []
version: "1.0.0"
author: allo-official
required_env:
  - MAAS_ADMIN_API_KEY
optional_env: []
credentials:
  - key: MAAS_ADMIN_API_KEY
    label: MaaS Admin API Key
    description: MaaS 平台 Admin 后台的 admin_api_key，用于查询可观测性接口。
    required: true
    secret: true
---

# MaaS 可观测查询 Skill

## Overview

查询 MaaS 平台可观测性数据，包括平台总览、模型用量、Provider/Pool 统计和系统健康状态。

## Runtime Paths

The Agent context should provide the absolute path to this `SKILL.md`. Derive bundled files from that path instead of using fixed virtual mount paths:

```bash
SKILL_DIR="$(cd "$(dirname "$SKILL_MD_PATH")" && pwd)"
WORKSPACE_DIR="${WORKSPACE_DIR:-$PWD/workspace}"
OUTPUT_DIR="${OUTPUT_DIR:-$PWD/outputs}"
```

Create output directories if needed.

## API Reference

Base URL: `http://221.0.79.251:8080`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/observability/overview` | GET | 平台总览 |
| `/api/v1/observability/models` | GET | 模型用量 |
| `/api/v1/observability/providers` | GET | Provider 统计 |
| `/api/v1/observability/pools` | GET | Pool 统计 |
| `/api/v1/observability/health` | GET | 系统健康 |

公共参数（models / providers / pools）：

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `start_time` | 否 | 1h前 | RFC3339 格式 |
| `end_time` | 否 | 当前 | RFC3339 格式 |
| `provider_type` | 否 | 全部 | pools 接口可选过滤：anthropic/openai/gemini/kimi/glm |

## Workflow

### Step 1: 验证接口可用

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  http://221.0.79.251:8080/api/v1/observability/overview
```

返回 `200` 表示配置正确。

### Step 2: 按需查询

**平台总览**：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  http://221.0.79.251:8080/api/v1/observability/overview
```

**模型用量**：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  "http://221.0.79.251:8080/api/v1/observability/models?start_time=2026-06-07T00:00:00Z&end_time=2026-06-08T00:00:00Z"
```

**Provider 统计**：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  "http://221.0.79.251:8080/api/v1/observability/providers"
```

**Pool 统计**（可按 provider_type 过滤）：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  "http://221.0.79.251:8080/api/v1/observability/pools?provider_type=openai"
```

**系统健康**：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  http://221.0.79.251:8080/api/v1/observability/health
```

### Step 3: 解析与展示

使用 `jq` 提取关键字段，或用 python 解析 JSON 响应后格式化展示给用户。

## Response Fields

### overview

| 字段 | 说明 |
|------|------|
| `total_accounts` | 总账号数 |
| `normal_accounts` | 正常账号数 |
| `error_accounts` | 异常账号数 |
| `overload_accounts` | 过载账号数 |
| `today_requests` | 今日请求数 |
| `today_tokens` | 今日 Token 数 |
| `today_cost` | 今日费用 |
| `active_users` | 活跃用户数 |
| `qps` / `tps` | 当前/峰值/平均 QPS 和 TPS |
| `sla` | SLA 百分比 |
| `error_rate` | 错误率 |
| `health_score` | 健康分数 |
| `duration` | 延迟分位数（p50/p90/p95/p99） |
| `upstream_429_count` | 上游 429 次数 |
| `upstream_529_count` | 上游 529 次数 |

### models

| 字段 | 说明 |
|------|------|
| `model` | 模型名 |
| `requests` | 请求数 |
| `input_tokens` / `output_tokens` / `total_tokens` | Token 用量 |
| `cost` / `actual_cost` | 费用 |

### providers / pools

| 字段 | 说明 |
|------|------|
| `provider_type` | 提供商类型 |
| `provider_pool` | Pool 名称（pools 接口） |
| `requests` | 请求数 |
| `success_count` / `error_count` | 成功/失败数 |
| `total_tokens` | Token 用量 |
| `cost` | 费用 |
| `active_models` | 活跃模型数 |
| `active_accounts` | 活跃账号数 |

### health

| 字段 | 说明 |
|------|------|
| `qps` / `tps` | 当前/峰值/平均 |
| `upstream_error_rate` | 上游错误率 |
| `upstream_429_count` / `upstream_529_count` | 上游限流次数 |
| `duration` | 延迟分位数 |
| `ttft` | 首 Token 延迟分位数 |

## Common Queries

查所有模型近日用量：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  "http://221.0.79.251:8080/api/v1/observability/models?start_time=2026-06-07T00:00:00Z&end_time=2026-06-08T00:00:00Z"
```

找出请求量最高的 provider：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  "http://221.0.79.251:8080/api/v1/observability/providers" | jq '.data.providers | sort_by(-.requests) | .[0]'
```

定位某个 provider 下哪个 pool 错误率高：
```bash
curl -s -H "Authorization: Bearer $MAAS_ADMIN_API_KEY" \
  "http://221.0.79.251:8080/api/v1/observability/pools?provider_type=openai" | jq '.data.pools'
```

## Alert Rules

| 条件 | 含义 |
|------|------|
| `health_score < 80` | 健康分数低，需关注 |
| `error_rate > 0.05` | 错误率过高 |
| `overload_accounts > 0` | 有账号过载 |
| `upstream_429_count` 持续增长 | 上游限流 |

## Common Mistakes

- 忘记认证 header — 所有接口都需要 `Authorization: Bearer $MAAS_ADMIN_API_KEY`
- 时间格式错误 — 必须用 RFC3339 格式（如 `2026-06-07T00:00:00Z`）
- 使用了 image-generation 的 key — 这里需要的是 admin_api_key，不是 GPT_IMAGE_API_KEY
