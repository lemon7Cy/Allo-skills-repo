---
name: dongfang-enterprise-kb-query
description: 查询东方电子企业知识库，面向配电、调度云化、储能新能源、微电网、综合能源、虚拟电厂、智慧城市、港口、石油石化等业务场景，并返回带出处的检索答案。当用户提到东方、东方电子、企业知识库或相关业务场景时使用。
tools: []
---

# 东方电子企业知识库查询

## 这个 Skill 做什么

使用独立的东方电子 RAGFlow 知识库回答企业/业务材料问题。**不要**将东方电子问题路由到明学知识库；明学是独立的电池/SOC/SOH 学术知识库。

## 何时使用

- 用户提到 `东方`、`东方电子`、`东方业务资料库`、`企业知识库`
- 主题包括：配电、配电自动化、调度及云化、E8000、储能、新能源、微电网、综合能源、虚拟电厂、威思顿、海颐、国网中电、智慧城市、港口、石油石化、智慧矿山
- 用户要求"查一下"、"检索"、"带出处"、"根据知识库回答"

**不要用于**：明学电池/SOC/SOH/RUL/Kalman 问题（用 `mingxue-kb-query`）

## 查询命令

使用远程东方查询包装器。不要对东方问题调用明学包装器。

```bash
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/dongfang-query-remote "QUESTION" --top-k 5 --mode answer --json'
```

获取更广泛证据：

```bash
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/dongfang-query-remote "QUESTION" --top-k 8 --mode answer --json'
```

文献/参考式探索（东方材料内）：

```bash
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/dongfang-query-remote "QUESTION" --top-k 5 --mode research --json'
```

包装器使用标准化远程查询服务：

```text
/mnt/hdd6t1/dongfang_query_proxy
```

远程主机上的服务管理命令：

```bash
/mnt/hdd6t1/dongfang_query_proxy/status.sh
/mnt/hdd6t1/dongfang_query_proxy/start.sh
/mnt/hdd6t1/dongfang_query_proxy/stop.sh
/mnt/hdd6t1/dongfang_query_proxy/restart.sh
/mnt/hdd6t1/dongfang_query_proxy/smoke.sh "东方电子有哪些配电自动化产品？"
```

查询失败时使用 `status.sh` 或 `smoke.sh` 检查。不要打印 `/mnt/hdd6t1/dongfang_query_proxy/query.env`（包含凭据/token）。

## Web / Agentic Search

东方电子公开 Agentic Search UI：

```text
http://221.0.79.251:18093
```

UI 支持证据搜索和 Agentic Search QA。Agentic Search 执行独立问题重写、首轮检索、证据评估、可选跟进检索、证据合并和最终引用答案。

## 数据集信息

- 主数据集：`dongfang-business-v1`
- 主数据集 ID：`4604b1105b7311f189f0cb2e8883de1f`
- 资产数据集：`dongfang-assets-shadow-v1`
- 资产数据集 ID：`693b40cc5b7311f189f0cb2e8883de1f`
- 查询代理：远程服务器 `127.0.0.1:18100`
- 查询服务根目录：`/mnt/hdd6t1/dongfang_query_proxy`
- 远程 CLI 包装器：`~/bin/dongfang-query-remote`
- 公共 Web 前端：远程服务器 `0.0.0.0:18093`
- 源运行根目录：`/mnt/hdd6t1/dongfang_kb/runs/20260529-dongfang-full`

不要暴露凭据或 token。不要打印 env 文件。只引用返回的 chunks/assets。

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
2. 基于证据的解释（仅使用返回的 `chunks` 和 `assets`）
3. 来源列表：`rank`、`document`、`section_type`、`similarity`
4. 资产来源列表（有用时）：`asset_id`、`asset_type`、`source_doc`、`similarity`

示例来源行：

```text
出处：rank #1, section=body, 东方电子配电画册2025版.md, sim=0.511
```

检索证据弱时如实说明。不要用通用行业知识填补空白。

## 常见错误

- 对东方问题使用 `mingxue-query-remote` → 用 `dongfang-query-remote`
- 用户要求知识库答案时先调用公开 Web 搜索
- 将通用微电网场景当作东方特有（无返回证据时）
- 声称图片细节（除非资产元数据或 VLM 摘要明确支持）
- 打印 API keys、查询 tokens、env 文件或 RAGFlow 凭据

## 与其他慧评 Skill 的配合

```
用户提问（东方电子相关）
       ↓
dongfang-enterprise-kb-query → 查询企业知识库
       ↓
带出处的答案 → 用于课程报告、研究、方案设计
```

## 资源文件

```
dongfang-enterprise-kb-query/
└── SKILL.md ← 你正在读
```

本 skill 是远程 SSH 查询，无本地脚本依赖。
