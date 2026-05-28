# Agent 产品 Skills Marketplace 关联与使用指南

## 1. 概述

本文档描述 Agent CLI 和 Agent 客户端如何与线上 Skills Marketplace 仓库进行关联，实现 skill 的发现、安装、启用、更新和运行时加载。

### 仓库信息

| 项目 | 值 |
|---|---|
| 仓库地址 | `https://github.com/wbz0429/Allo-skills-repo.git` |
| 主索引文件 | `marketplace.json` |
| Skill 目录结构 | `plugins/<name>/skills/<name>/SKILL.md` |
| 校验脚本 | `scripts/validate_marketplace.py` |

---

## 2. 线上仓库结构

```
Allo-skills-repo/
├── marketplace.json                          # 全局 skill 索引
├── scripts/
│   └── validate_marketplace.py               # 一致性校验脚本
├── tests/
│   └── test_marketplace.py                   # 自动化测试
└── plugins/
    ├── mingxue-kb-query/
    │   └── skills/
    │       └── mingxue-kb-query/
    │           └── SKILL.md
    ├── dify-workflow-coding/
    │   └── skills/
    │       └── dify-workflow-coding/
    │           └── SKILL.md
    │           └── ... (references, tools)
    └── ... (其他 skill)
```

### marketplace.json Schema

```json
{
  "name": "allo-skills-repo",
  "description": "...",
  "plugins": [
    {
      "name": "mingxue-kb-query",
      "source": "./plugins/mingxue-kb-query",
      "description": "查询明雪知识库...",
      "version": "1.0.0"
    }
  ]
}
```

每个 plugin 字段含义：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | skill 唯一标识，也对应目录名 |
| `source` | string | 是 | 相对于 marketplace.json 的路径 |
| `description` | string | 否 | 触发条件描述，供 Agent 运行时匹配 |
| `version` | string | 否 | 当前版本号 |
| `displayName` | string | 否 | 展示名称（扩展预留） |
| `category` | string | 否 | 分类标签（扩展预留） |
| `tags` | string[] | 否 | 搜索标签（扩展预留） |
| `entry` | string | 否 | skill 入口文件相对路径（扩展预留） |
| `downloadUrl` | string | 否 | zip 下载地址（扩展预留） |
| `permissions` | object | 否 | 权限声明（扩展预留） |

---

## 3. Agent 产品集成架构

```
┌─────────────────────────────────────────────┐
│              Agent 产品                      │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Market   │  │ Skill    │  │ Agent     │  │
│  │ Source   │→ │ Library  │→ │ Skill Set │  │
│  │ Config   │  │ Install  │  │ Bind      │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       │              │              │        │
└───────┼──────────────┼──────────────┼────────┘
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌───────────┐
  │ GitHub   │  │ Local    │  │ Runtime   │
  │ Raw API  │  │ Cache    │  │ Load      │
  └──────────┘  └──────────┘  └───────────┘
```

三层配置：

```
Market 源配置       → 从哪里拉 skill 列表
    ↓
组织/用户 Library   → 安装了哪些 skills
    ↓
Agent Skill Set     → 某个 Agent 启用哪些 skills
```

---

## 4. 第一步：配置 Market Source

Agent 产品需要支持配置一个或多个 Skills Marketplace 源。

### 配置方式

**通过管理后台 UI 配置：**

```text
管理后台 → Skills Market → Market Sources → 添加
```

**通过配置文件：**

```json
{
  "skillMarkets": [
    {
      "id": "allo-official",
      "name": "Allo Official Skills",
      "url": "https://raw.githubusercontent.com/wbz0429/Allo-skills-repo/main/marketplace.json",
      "enabled": true,
      "trustLevel": "official"
    }
  ]
}
```

### 拉取 marketplace.json

产品启动或用户点击同步时，从配置的 URL 拉取 `marketplace.json`：

```typescript
async function syncMarket(marketUrl: string): Promise<MarketplacePlugin[]> {
  const response = await fetch(marketUrl);
  const data = await response.json();

  if (!data.plugins || !Array.isArray(data.plugins)) {
    throw new Error('Invalid marketplace.json: missing plugins array');
  }

  return data.plugins;
}
```

### 校验

拉取后需要校验：

```typescript
function validatePlugin(plugin: any): boolean {
  return (
    typeof plugin.name === 'string' &&
    plugin.name.length > 0 &&
    typeof plugin.source === 'string' &&
    plugin.source.length > 0
  );
}
```

---

## 5. 第二步：安装 Skill

### 安装流程

```text
用户在 Skills Market 页面浏览
    ↓
点击某个 skill 进入详情
    ↓
点击"安装"
    ↓
产品下载 SKILL.md（或 zip 包）
    ↓
校验文件完整性
    ↓
保存到本地 skill cache
    ↓
标记为已安装
```

### 从 GitHub Raw 下载单个 SKILL.md

```typescript
const BASE_URL = 'https://raw.githubusercontent.com/wbz0429/Allo-skills-repo/main';

async function installSkill(plugin: MarketplacePlugin): Promise<void> {
  const skillUrl = `${BASE_URL}/${plugin.source}/skills/${plugin.name}/SKILL.md`;

  const response = await fetch(skillUrl);
  if (!response.ok) {
    throw new Error(`Failed to download skill: ${response.status}`);
  }

  const content = await response.text();

  // 校验 SKILL.md 必须有 frontmatter
  if (!content.startsWith('---')) {
    throw new Error('Invalid SKILL.md: missing YAML frontmatter');
  }

  // 保存到本地
  await saveToLocalCache(plugin.name, content, plugin.version);
}
```

### 从 zip 包安装（后续扩展）

如果 marketplace.json 里有 `downloadUrl`：

```typescript
async function installSkillFromZip(plugin: MarketplacePlugin): Promise<void> {
  if (!plugin.downloadUrl) {
    throw new Error('No downloadUrl, use source-based install');
  }

  const zipBuffer = await downloadToBuffer(plugin.downloadUrl);
  await extractZip(zipBuffer, getSkillCacheDir(plugin.name));

  // 校验根目录有 SKILL.md
  const entryPath = path.join(getSkillCacheDir(plugin.name), 'SKILL.md');
  if (!fs.existsSync(entryPath)) {
    throw new Error('Invalid skill zip: SKILL.md not found at root');
  }
}
```

### 本地存储结构

```text
~/.agent/
├── config.json
└── skills/
    ├── mingxue-kb-query/
    │   └── SKILL.md
    ├── dify-workflow-coding/
    │   └── SKILL.md
    └── publish-dfcode/
        └── SKILL.md
```

---

## 6. 第三步：启用 Skill 到 Agent

### 配置方式

**给具体 Agent 绑定 skills：**

```json
{
  "agents": [
    {
      "id": "battery-research-agent",
      "name": "电池研究 Agent",
      "enabledSkills": [
        "mingxue-kb-query"
      ]
    },
    {
      "id": "dify-coding-agent",
      "name": "Dify Workflow Agent",
      "enabledSkills": [
        "dify-workflow-coding"
      ]
    },
    {
      "id": "dfcode-ops-agent",
      "name": "DFCode 运维 Agent",
      "enabledSkills": [
        "publish-dfcode",
        "query-dfcode-usage"
      ]
    }
  ]
}
```

**Agent 客户端 UI 操作：**

```text
Agent Builder → 选择 Agent → Skills 标签页
    ↓
勾选要启用的 skills
    ↓
保存配置
```

---

## 7. 第四步：运行时加载 Skill

Agent 收到用户消息后，按以下流程加载和匹配 skill：

```text
用户发送消息
    ↓
读取当前 Agent 的 enabledSkills
    ↓
遍历 enabledSkills，加载每个 SKILL.md 的 frontmatter
    ↓
用 description 字段做语义匹配
    ↓
匹配成功 → 将完整 SKILL.md 内容注入上下文
    ↓
Agent 按 SKILL.md 中的指令执行
```

### 伪代码

```typescript
interface SkillFrontmatter {
  name: string;
  description: string;
}

function parseFrontmatter(content: string): SkillFrontmatter {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) throw new Error('Missing frontmatter');

  const lines = match[1].split('\n');
  const result: any = {};
  for (const line of lines) {
    const [key, ...rest] = line.split(':');
    result[key.trim()] = rest.join(':').trim();
  }
  return result;
}

async function loadAndMatch(
  userMessage: string,
  enabledSkills: string[]
): Promise<string | null> {
  for (const skillName of enabledSkills) {
    const content = await readFromCache(skillName);
    const meta = parseFrontmatter(content);

    if (matchByDescription(userMessage, meta.description)) {
      return content; // 注入完整 SKILL.md 到 Agent 上下文
    }
  }
  return null;
}
```

### 匹配策略

第一版建议用关键词匹配：

```typescript
function matchByDescription(userMessage: string, description: string): boolean {
  const keywords = extractKeywords(description);
  const lowerMessage = userMessage.toLowerCase();
  return keywords.some(kw => lowerMessage.includes(kw.toLowerCase()));
}
```

后续可升级为 embedding 语义匹配。

---

## 8. CLI 集成

### 配置同步

CLI 登录后从 Agent 后端同步 skill 配置：

```bash
agent login
agent skill market sync allo-official
```

### CLI 命令

```bash
# 列出已配置的 market 源
agent skill market list

# 同步 market 索引
agent skill market sync allo-official

# 搜索 skill
agent skill search mingxue

# 查看 skill 详情
agent skill info mingxue-kb-query

# 安装 skill
agent skill install mingxue-kb-query

# 列出已安装的 skills
agent skill list --installed

# 启用 skill 到某个 Agent
agent skill enable mingxue-kb-query --agent battery-research-agent

# 禁用 skill
agent skill disable mingxue-kb-query --agent battery-research-agent

# 更新 skill
agent skill update mingxue-kb-query

# 更新所有 skills
agent skill update --all
```

### CLI 配置文件

```json
// ~/.agent/config.json
{
  "skillMarkets": [
    {
      "id": "allo-official",
      "name": "Allo Official Skills",
      "url": "https://raw.githubusercontent.com/wbz0429/Allo-skills-repo/main/marketplace.json",
      "enabled": true
    }
  ],
  "installedSkills": {
    "mingxue-kb-query": {
      "version": "1.0.0",
      "installedAt": "2026-05-28T10:00:00Z"
    }
  },
  "agents": {
    "battery-research-agent": {
      "enabledSkills": ["mingxue-kb-query"]
    }
  }
}
```

### CLI 运行时

```bash
agent chat --agent battery-research-agent
# Agent 自动加载 mingxue-kb-query skill
# 用户提问电池相关问题时自动触发
```

---

## 9. Skill 更新机制

### 版本检测

```typescript
async function checkUpdates(): Promise<UpdateInfo[]> {
  const remotePlugins = await syncMarket(marketUrl);
  const updates: UpdateInfo[] = [];

  for (const remote of remotePlugins) {
    const local = getLocalVersion(remote.name);
    if (local && remote.version && semver.gt(remote.version, local)) {
      updates.push({
        name: remote.name,
        currentVersion: local,
        latestVersion: remote.version,
      });
    }
  }

  return updates;
}
```

### 更新策略

| 策略 | 说明 |
|---|---|
| `manual` | 手动更新，推荐默认 |
| `patch` | 自动更新 patch 版本 |
| `latest` | 永远更新到最新版 |
| `pinned` | 固定版本，不自动更新 |

---

## 10. 权限管理

### 声明权限

skill 在 marketplace.json 中声明所需权限：

```json
{
  "name": "mingxue-kb-query",
  "permissions": {
    "shell": true,
    "network": true,
    "ssh": true,
    "filesystem": false,
    "browser": false,
    "secrets": []
  }
}
```

### 安装时确认

Agent 产品在安装高权限 skill 时应二次确认：

```text
┌─────────────────────────────────────────────┐
│  安装 Skill: mingxue-kb-query               │
│                                              │
│  该 Skill 需要以下权限:                       │
│  [x] 执行 shell 命令                         │
│  [x] 访问网络                                │
│  [x] SSH 远程服务器访问                       │
│                                              │
│  是否允许安装？                               │
│  [ 允许 ]  [ 取消 ]                           │
└─────────────────────────────────────────────┘
```

---

## 11. 仓库维护流程

### 新增 Skill

```bash
# 1. 创建目录
mkdir -p plugins/<skill-name>/skills/<skill-name>

# 2. 写 SKILL.md
vim plugins/<skill-name>/skills/<skill-name>/SKILL.md

# 3. 注册到 marketplace.json
# 在 plugins 数组中添加条目

# 4. 校验一致性
python3 scripts/validate_marketplace.py

# 5. 运行测试
python3 -m unittest tests.test_marketplace -v

# 6. 提交并推送
git add . && git commit -m "feat: add <skill-name> skill" && git push origin main
```

### 更新 Skill

```bash
# 1. 修改 SKILL.md
vim plugins/<skill-name>/skills/<skill-name>/SKILL.md

# 2. 更新 marketplace.json 中的 version 字段

# 3. 校验并测试
python3 scripts/validate_marketplace.py
python3 -m unittest tests.test_marketplace -v

# 4. 提交并推送
git add . && git commit -m "feat: update <skill-name> to <version>" && git push origin main
```

### 校验检查清单

每次变更后必须通过：

```bash
python3 scripts/validate_marketplace.py
```

该脚本校验：

- marketplace.json 语法正确
- 每个 plugin 有 name 和 source
- 每个 source 目录下存在对应的 SKILL.md
- plugins/ 下所有 SKILL.md 都已在 marketplace.json 中注册
- 无重复 name

---

## 12. 当前可用 Skills 列表

| Name | 分类 | 说明 |
|---|---|---|
| `mingxue-kb-query` | 知识库 | 查询明雪知识库，电池/SOC/SOH/RUL/BMS 带出处检索 |
| `dify-workflow-coding` | 开发 | 创建、修复、审查 Dify workflow DSL/YAML |
| `publish-dfcode` | 运维 | 发布 dfcode 到 npm |
| `query-dfcode-usage` | 运维 | 查询 dfcode-admin 生产用量 |
| `guizang-ppt-skill` | 办公 | 生成横向翻页网页 PPT |
| `article-to-html` | 办公 | Markdown 渲染为 paper-style HTML |
| `publish-research-site` | 研究 | 研究主题转化为网站并部署到 Vercel |
| `video-plan` | 创意 | 短视频/vlog 分场景脚本规划 |
| `mega-goal-prompt` | 开发 | 生成 long-horizon mega prompt |
| `doctor-strange` | 决策 | 因果沙盘和多宇宙推演模拟 |
| `lab-interpreter` | 医疗 | 解读医疗化验单和体检报告 |
| `emergency-triage` | 医疗 | 急诊分诊和症状排查 |
| `clean-data-xls` | 办公 | 清洗 Excel/表格数据 |
| `audit-xls` | 金融 | 审计电子表格公式和金融模型 |
| `deck-refresh` | 金融 | 刷新 PowerPoint deck 数据 |
| `ib-check-deck` | 金融 | 投行演示文稿质检 |
| `competitive-analysis` | 金融 | 竞争格局和竞品分析 |
| `3-statement-model` | 金融 | 三表财务模型 |
| `comps-analysis` | 金融 | 可比公司分析 |
| `dcf-model` | 金融 | DCF 估值模型 |
| `lbo-model` | 金融 | LBO 模型 |

---

## 13. 推荐落地顺序

| 阶段 | 内容 | 优先级 |
|---|---|---|
| P0 | Market Source 配置 + 拉取 marketplace.json | 高 |
| P0 | Skill 安装（从 GitHub Raw 下载 SKILL.md） | 高 |
| P0 | Agent 绑定 enabledSkills | 高 |
| P0 | 运行时加载和关键词匹配 | 高 |
| P1 | Skills Market UI 页面（浏览/搜索/安装） | 中 |
| P1 | CLI 命令支持 | 中 |
| P1 | Skill 版本检测和更新 | 中 |
| P2 | 权限声明和安装确认 | 低 |
| P2 | zip 包下载安装 | 低 |
| P2 | 组织级策略和同步 | 低 |
| P3 | 语义匹配替代关键词匹配 | 低 |
| P3 | 后端 API + 安装统计 + 推荐 | 低 |

---

## 14. Agent 侧配置文件汇总

### Market Source（管理后台 / 全局配置）

```json
{
  "skillMarkets": [
    {
      "id": "allo-official",
      "name": "Allo Official Skills",
      "url": "https://raw.githubusercontent.com/wbz0429/Allo-skills-repo/main/marketplace.json",
      "enabled": true
    }
  ]
}
```

### Installed Skills（用户/组织级）

```json
{
  "installedSkills": [
    {
      "name": "mingxue-kb-query",
      "version": "1.0.0",
      "marketId": "allo-official",
      "enabled": true,
      "scope": "organization"
    }
  ]
}
```

### Agent Skill Set（Agent 级）

```json
{
  "agents": [
    {
      "id": "battery-research-agent",
      "name": "电池研究 Agent",
      "enabledSkills": ["mingxue-kb-query"]
    }
  ]
}
```

### 运行时加载优先级

```text
Agent 显式配置
    > Project 配置
    > User 配置
    > Organization 默认配置
    > Marketplace 可用但未启用的 skills
```
