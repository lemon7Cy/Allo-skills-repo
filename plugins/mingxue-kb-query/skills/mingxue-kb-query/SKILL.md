---
name: mingxue-kb-query
description: 查询明雪知识库，面向电池、SOC、SOH、RUL、Kalman、EKF、UKF、BMS、储能问题，并返回带出处的检索答案。
tools: []
---

# 明雪知识库查询

## 概述

使用远程 `mingxue-query-remote` 包装器查询 `mingxue-full-v1` RAGFlow 知识库。默认使用答案导向检索：用证据块回答，将参考文献作为独立信号（除非用户要求文献发现）。

## 何时使用

- 用户提到 `明雪知识库`、`Mingxue`、`知识库`，或要求带引用的检索结果
- 领域问题：电池、储能、SOC、SOH、RUL、Kalman、EKF、UKF、BMS、ECM、电池数据集
- 用户要求"查一下"、"检索"、"带出处"、"根据知识库回答"

不要用于通用编码任务或与此知识库无关的问题。

## 环境变量配置（必须）

使用前必须设置以下环境变量：

```bash
export MINGXUE_SSH_HOST="<ssh-user>@<server-ip>"   # e.g. user@10.0.0.1
export MINGXUE_SSH_PORT="<ssh-port>"                # e.g. 10022
```

## 查询命令

使用远程包装器命令。不要在本地命令中内联远程服务器内部路径。

```bash
ssh -p $MINGXUE_SSH_PORT -o ConnectTimeout=10 $MINGXUE_SSH_HOST '~/bin/mingxue-query-remote "QUESTION" --top-k 5 --mode answer --json'
```

将 `QUESTION` 替换为用户的问题。快速检查用 `--top-k 3`，更广泛证据用 `--top-k 8`。

仅当用户要求论文、参考文献、文献线索或研究概述时使用 `--mode research`：

```bash
ssh -p $MINGXUE_SSH_PORT -o ConnectTimeout=10 $MINGXUE_SSH_HOST '~/bin/mingxue-query-remote "QUESTION" --top-k 5 --mode research --json'
```

重要：
- 不要在命令中内联远程服务器内部路径
- 远程包装器已加载查询配置
- 远程包装器已设置本地查询 API 基址
- 远程包装器已调用部署的 `mingxue-query` 二进制文件
- 不要编写临时脚本或使用路径混淆变通方案
- 不要打印环境变量或 token

## 内置检索规则

代理已处理配置：

| 查询语言 | 检索行为 |
|----------|----------|
| 中文 | 跨语言 = 英文 |
| 英文 | 跨语言关闭 |
| 任意 | 重排序器关闭 |
| 答案模式 | 过度获取候选，从主要块中过滤 `references`/`biography` |
| 研究模式 | 保留引用/参考信号用于文献发现 |

除非用户明确要求测试，否则不要手动添加重排序器。

## 检索模式规则

- 默认使用 `--mode answer` 用于事实、解释、比较和技术问题
- 仅使用 `chunks` 回答；这些是主要证据通道
- 将 `reference_signals` 视为引用/文献线索，而非直接答案证据
- 仅在有用时提及 `diagnostics.filtered_references` 以解释引用部分已从答案证据中分离
- 当用户问"有哪些论文"、"参考文献"、"研究脉络"、"literature"、"papers"、"citations"等时切换到 `--mode research`

## 查询规划规则

不要使用用户的最终答案提示作为检索查询。将其转换为证据查询。

不好的检索查询：

```text
面向初学者解释储能锂离子电池循环实验数据分析中的 SOC SOH 容量衰减 库仑效率 能量效率 内阻 RUL OCV 安时积分 卡尔曼滤波
```

更好的证据查询：

```bash
ssh -p $MINGXUE_SSH_PORT -o ConnectTimeout=10 $MINGXUE_SSH_HOST '~/bin/mingxue-query-remote "锂离子电池循环实验数据分析 SOC SOH 容量衰减 库仑效率 能量效率" --top-k 4 --mode answer --json'
ssh -p $MINGXUE_SSH_PORT -o ConnectTimeout=10 $MINGXUE_SSH_HOST '~/bin/mingxue-query-remote "锂离子电池老化 内阻 容量衰减 SOH RUL 循环寿命" --top-k 4 --mode answer --json'
ssh -p $MINGXUE_SSH_PORT -o ConnectTimeout=10 $MINGXUE_SSH_HOST '~/bin/mingxue-query-remote "SOC估计 OCV 安时积分 卡尔曼滤波 锂离子电池" --top-k 4 --mode answer --json'
```

如果用户问 5+ 个术语，拆分为 2-4 个聚焦的答案模式查询。建议聚类：

| 聚类 | 术语 |
|------|------|
| 状态指标 | SOC、SOH、OCV |
| 实验指标 | 容量衰减、库仑效率、能量效率 |
| 老化与寿命 | 内阻、RUL、循环寿命 |
| 估计方法 | 安时积分、Kalman、EKF、UKF |

检索后合并证据：
- 去重高度相似的块和重复文档
- 优先 `abstract`、`method`、`result`、`table` 块而非通用 `body` 块
- 每个聚焦查询使用 `top-k 3-5` 而非一个大关键词堆砌
- 如果证据仍不足，运行一次额外的聚焦查询；不要从通用知识中填充答案
- 仅对文献/参考需求运行单独的 `--mode research` 查询

## 回答格式

返回：
1. 简短答案或结论
2. 基于证据的解释（来自返回的 `chunks`）
3. 来源列表：`rank`、`document`、`section_type`、`similarity`
4. 可选的参考信号说明（仅在对研究跟进有用时）

示例来源行：

```text
出处：rank #1, section=method, State_of_Charge_Estimation_of_Battery_Energy_Storage_Systems_Based_on_Adaptive_U.md, sim=0.671
```

如果检索到的块较弱，如实说明并避免过度声称。

## 常见错误

- 不要编造引用；只引用返回的块
- 不要从 `reference_signals` 回答（除非用户明确要求文献/参考发现）
- 不要在单个检索查询中堆砌许多松散相关的术语；拆分为聚焦的证据查询
- 不要混淆答案规划和检索规划：最终答案可以广泛综合，检索应该聚焦
- 不要暴露或打印 `MINGXUE_QUERY_TOKEN`
- 不要在命令中包含远程服务器内部绝对路径
- 不要声称页码；当前 Markdown/RAGFlow 管道返回文档名和块，而非稳定的 PDF 页码
- 不要在最终答案中直接使用 RAGFlow 管理凭据
