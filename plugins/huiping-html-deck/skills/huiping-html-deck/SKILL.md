---
name: huiping-html-deck
description: 生成课程报告演示用的横向翻页网页 PPT（单文件 HTML），支持电子杂志风和瑞士国际主义两种风格。当用户需要为课程报告、学术分享、答辩演示制作网页幻灯片时使用。基于 guizang-ppt-skill 改造，适配慧评课程报告场景。
tools: []
---

# 慧评 HTML 演示稿生成器

> 来源: 基于 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)（AGPL-3.0）改造，适配课程报告场景。原作者: 歸藏。

## 首次安装（必须）

本 skill 依赖上游模板资源。首次使用前运行：

```bash
bash <SKILL_ROOT>/setup.sh
```

该脚本会从上游仓库拉取模板 HTML、参考文档和校验脚本到本地。

## 这个 Skill 做什么

生成一份**单文件 HTML** 的横向翻页 PPT，专为课程报告演示设计：

- 🎓 **课程报告答辩** — 六维评分可视化、成长证据链展示
- 📊 **数据分析汇报** — SOC/SOH/RUL/BMS 实验结果展示
- 📖 **文献综述分享** — 知识图谱、引用网络可视化
- 🔬 **研究方法论** — 流程图、对比分析、系统架构

## 何时使用

**合适**：
- 课程报告答辩、中期汇报、结题展示
- 学术分享会、课题组内部汇报
- 需要快速生成、浏览器直接打开的演示稿
- 和 `huiping-incremental-evaluator` 配合展示评价结果

**不合适**：
- 需要在 PowerPoint 里编辑提交的正式文档（用 `huiping-ppt-generator`）
- 大段表格数据、密集数值（用常规 PPT）
- 需要多人协作编辑

## 两种视觉风格

### 风格 A · 电子杂志 × 电子墨水（默认）

- **WebGL 流体背景**（hero 页可见）
- **衬线标题 + 非衬线正文 + 等宽元数据**
- 适合：人文分享、课程叙事、研究故事
- 美学锚点：像 *Monocle* 杂志

### 风格 B · 瑞士国际主义

- **网格至上、单一高饱和锚点色、直角、发丝线**
- **极致字号对比、无衬线**
- 适合：数据汇报、技术分析、实验结果展示
- 美学锚点：像 Massimo Vignelli

**课程报告推荐**：实验数据多用风格 B，研究叙事多用风格 A。

## 工作流

### Step 1 · 需求澄清（动手前必做）

如果用户已经给了完整大纲，可以跳过。否则用以下问题逐个对齐：

| # | 问题 | 为什么要问 |
|---|------|-----------|
| 1 | 风格 A 还是 B？ | 决定用哪个 template + layouts |
| 2 | 受众和场景？（答辩 / 组会 / 分享会） | 决定语言风格和深度 |
| 3 | 时长？ | 15 分钟 ≈ 10 页，30 分钟 ≈ 20 页 |
| 4 | 有没有原始素材？（课程报告 PDF / 数据文件 / 旧 PPT） | 有素材就基于素材生成 |
| 5 | 有没有图表或截图？ | 决定图文版式和图片槽位 |
| 6 | 想要哪套主题色？ | 杂志风 5 套 / 瑞士风 4 套 |
| 7 | 硬约束？（必须包含哪些内容） | 避免返工 |

#### 风格选择参考

| 内容类型 | 推荐风格 |
|----------|----------|
| SOC/SOH/RUL 实验数据分析 | B · 瑞士风（数据驱动） |
| BMS 系统架构和流程 | B · 瑞士风（结构图强） |
| 文献综述、研究故事 | A · 杂志风（叙事感） |
| 课程报告六维评分展示 | B · 瑞士风（KPI Tower） |
| 研究方法论、对比分析 | B · 瑞士风（Duo Compare） |

#### 大纲协助（如果用户没有大纲）

用"课程报告弧"模板搭骨架：

```
研究背景(Hook)        → 1 页   : 问题是什么，为什么重要
文献综述(Context)     → 1-2 页 : 已有工作的关键发现
方法论(Method)        → 2-3 页 : 实验设计、系统架构
结果(Results)         → 2-4 页 : 关键数据、图表、对比
讨论(Discussion)      → 1-2 页 : 意义、局限、未来工作
结论(Takeaway)        → 1 页   : 核心贡献、下一步
```

### Step 2 · 拷贝模板

```bash
mkdir -p "项目/XXX/ppt/images"

# 风格 A · 电子杂志风
cp "<SKILL_ROOT>/assets/template.html" "项目/XXX/ppt/index.html"

# 或 风格 B · 瑞士国际主义风
cp "<SKILL_ROOT>/assets/template-swiss.html" "项目/XXX/ppt/index.html"
```

两个 template 都是**完整可运行**的文件——CSS、WebGL shader、翻页 JS、字体/图标 CDN 全已预设。

**必改占位符**：
- `<title>` 标签中的 `[必填] 替换为 PPT 标题`

### Step 3 · 选定主题色

只允许从预设里选，不允许自定义 hex：

| 风格 A · 杂志风 | 适合 |
|---|---|
| 🖋 墨水经典 | 通用默认 |
| 🌊 靛蓝瓷 | 科技 / 研究 / 数据 |
| 🌿 森林墨 | 自然 / 可持续 / 文化 |
| 🍂 牛皮纸 | 怀旧 / 人文 / 文学 |
| 🌙 沙丘 | 艺术 / 设计 / 创意 |

| 风格 B · 瑞士风 | 锚点色 |
|---|---|
| 🔵 克莱因蓝 IKB | 通用默认、AI、方法论 |
| 🟡 柠檬黄 | 年轻、消费品 |
| 🟢 柠檬绿 | 生态、健康 |
| 🟠 安全橙 | 工业、运动 |

### Step 4 · 填充内容

**关键规则**：
1. **先读模板的 `<style>` 块**确认类名存在
2. 不要从零写 slide，用 layouts 文件里的现成布局骨架
3. 风格 A 类名和风格 B 类名**互不通用**
4. 每页 section 必须带 `light` / `dark` / `hero light` / `hero dark`
5. 连续 3 页以上同主题 = 视觉疲劳，不允许

**风格 A 布局**（10 种）：开场封面、章节幕封、数据大字报、左文右图、图片网格、流水线、悬念收束、大引用页、并列对比、图文混排

**风格 B 布局**（22 种锁定版式）：S01 Index Cover → S22 Image Hero，每页必须写 `data-layout="Sxx"`

### Step 5 · 对照检查清单自检

生成后打开 `references/checklist.md` 逐项对照。P0 级别问题必须全部通过。

课程报告特别检查项：
- 六维评分数据是否完整展示
- 图表/数据可视化是否清晰可读
- 关键结论是否有数据支撑
- 文献引用格式是否统一

### Step 6 · 本地预览

```bash
open "项目/XXX/ppt/index.html"
```

浏览器直接打开，不需要服务器。

## 与其他慧评 Skill 的配合

```
huiping-incremental-evaluator → 生成六维评分 JSON
       ↓
huiping-html-deck → 将评分数据可视化为演示稿
       ↓
浏览器打开 → 答辩/汇报展示
```

## 资源文件

```
huiping-html-deck/
├── SKILL.md                    ← 你正在读
├── assets/
│   ├── template.html           ← 风格 A · 杂志风模板
│   ├── template-swiss.html     ← 风格 B · 瑞士风模板
│   └── screenshot-backgrounds/ ← 截图美化背景
├── scripts/
│   └── validate-swiss-deck.mjs ← 瑞士风版式校验器
└── references/
    ├── components.md           ← 组件手册
    ├── layouts.md              ← 风格 A 布局骨架
    ├── layouts-swiss.md        ← 风格 B 22 种版式
    ├── swiss-layout-lock.md    ← 瑞士风版式锁
    ├── themes.md               ← 风格 A 主题色
    ├── themes-swiss.md         ← 风格 B 主题色
    ├── image-prompts.md        ← 配图提示词
    ├── screenshot-framing.md   ← 截图适配
    └── checklist.md            ← 质量检查清单
```

## 核心设计原则

1. **克制优于炫技** — WebGL 背景只在 hero 页透出
2. **结构优于装饰** — 信息靠字号 + 字体对比 + 网格留白
3. **图片是第一公民** — 图片只裁底部，保证顶部和左右完整
4. **节奏靠 hero 页** — hero 和 non-hero 交替
5. **瑞士风守版式** — Style B 只用 S01-S22，不发明新结构
