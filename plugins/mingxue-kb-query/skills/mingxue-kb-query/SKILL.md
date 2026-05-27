---
name: mingxue-kb-query
description: Use when the user asks to search, query, cite, or answer from the Mingxue knowledge base, especially battery/SOC/SOH/RUL/Kalman/EKF/UKF/BMS/energy-storage questions requiring sources.
---

# Mingxue KB Query

## Overview

Use the remote `mingxue-query-remote` wrapper to query the `mingxue-full-v1` RAGFlow knowledge base. Default to answer-oriented retrieval: use evidence chunks for answers, and treat references as separate signals unless the user asks for literature discovery.

## When to Use

- User mentions `明雪知识库`, `Mingxue`, `知识库`, or asks for cited retrieval results.
- Domain questions about batteries, energy storage, SOC, SOH, RUL, Kalman, EKF, UKF, BMS, ECM, or battery datasets.
- User asks to “查一下”, “检索”, “带出处”, “根据知识库回答”.

Do not use for general coding tasks or questions unrelated to this KB.

## Query Command

Use the remote wrapper command. Do not inline remote server internal paths in the local command.

```bash
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/mingxue-query-remote "QUESTION" --top-k 5 --mode answer --json'
```

Replace `QUESTION` with the user's question. Use `--top-k 3` for quick checks, `--top-k 8` for broader evidence.

Use `--mode research` only when the user asks for papers, references, literature trails, citation clues, or research overviews:

```bash
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/mingxue-query-remote "QUESTION" --top-k 5 --mode research --json'
```

Important:

- Do not inline remote server internal paths in the command.
- The remote wrapper already loads query configuration.
- The remote wrapper already sets the local query API base.
- The remote wrapper already calls the deployed `mingxue-query` binary.
- Do not write temporary scripts or use path-obfuscation workarounds.
- Do not print environment variables or tokens.

## Built-In Retrieval Rules

The proxy already handles configuration:

| Query language | Retrieval behavior |
|---|---|
| Chinese | Cross-language = English |
| English | Cross-language off |
| Any | Reranker off |
| Answer mode | Overfetch candidates, filter `references`/`biography` from primary chunks |
| Research mode | Keep citation/reference signals for literature discovery |

Do not manually add reranker unless the user explicitly asks to test it.

## Retrieval Mode Rules

- Default to `--mode answer` for factual, explanatory, comparison, and technical questions.
- Answer using `chunks` only; these are the primary evidence channel.
- Treat `reference_signals` as citation/literature clues, not direct answer evidence.
- Mention `diagnostics.filtered_references` only when useful to explain that citation sections were separated from answer evidence.
- Switch to `--mode research` when the user asks “有哪些论文”, “参考文献”, “研究脉络”, “literature”, “papers”, “citations”, or similar.

## Query Planning Rules

Do not use the user's final answer prompt as the retrieval query. Convert it into evidence queries.

Bad retrieval query:

```text
面向初学者解释储能锂离子电池循环实验数据分析中的 SOC SOH 容量衰减 库仑效率 能量效率 内阻 RUL OCV 安时积分 卡尔曼滤波
```

Better evidence queries:

```bash
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/mingxue-query-remote "锂离子电池循环实验数据分析 SOC SOH 容量衰减 库仑效率 能量效率" --top-k 4 --mode answer --json'
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/mingxue-query-remote "锂离子电池老化 内阻 容量衰减 SOH RUL 循环寿命" --top-k 4 --mode answer --json'
ssh -p 10022 -o ConnectTimeout=10 songjin@221.0.79.251 '~/bin/mingxue-query-remote "SOC估计 OCV 安时积分 卡尔曼滤波 锂离子电池" --top-k 4 --mode answer --json'
```

If the user asks about 5+ terms, split into 2-4 focused answer-mode queries. Suggested clusters:

| Cluster | Terms |
|---|---|
| State indicators | SOC, SOH, OCV |
| Experiment metrics | capacity fade, coulombic efficiency, energy efficiency |
| Aging and lifetime | internal resistance, RUL, cycle life |
| Estimation methods | ampere-hour integration, Kalman, EKF, UKF |

Merge evidence after retrieval:

- Deduplicate highly similar chunks and repeated documents.
- Prefer `abstract`, `method`, `result`, and `table` chunks over generic `body` chunks.
- Use `top-k 3-5` per focused query instead of one large keyword dump.
- If evidence is still thin, run one additional focused query; do not pad the answer from general knowledge.
- Run a separate `--mode research` query only for literature/reference needs.

## Answer Format

Return:

1. Short answer or conclusion.
2. Evidence-based explanation from returned `chunks`.
3. Source list with `rank`, `document`, `section_type`, and `similarity`.
4. Optional reference-signal note only if useful for research follow-up.

Example source line:

```text
出处：rank #1, section=method, State_of_Charge_Estimation_of_Battery_Energy_Storage_Systems_Based_on_Adaptive_U.md, sim=0.671
```

If retrieved chunks are weak, say so and avoid overclaiming.

## Common Mistakes

- Do not invent citations; only cite returned chunks.
- Do not answer from `reference_signals` unless the user explicitly asks for literature/reference discovery.
- Do not stuff many loosely related terms into one retrieval query; split into focused evidence queries.
- Do not confuse answer planning with retrieval planning: final answers can synthesize broadly, retrieval should be narrow.
- Do not expose or print `MINGXUE_QUERY_TOKEN`.
- Do not include remote server internal absolute paths in commands shown to tools or users.
- Do not claim page numbers; the current Markdown/RAGFlow pipeline returns document names and chunks, not stable PDF pages.
- Do not use RAGFlow admin credentials directly in the final answer.
