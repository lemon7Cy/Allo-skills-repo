---
name: huiping-ppt-generator
description: AI 驱动的课程报告 PPT 生成器，将文档/数据转换为原生可编辑的 .pptx 文件。支持多角色协作、SVG 内容生成、动画和 speaker notes。当用户需要生成正式的、可在 PowerPoint 中编辑的课程报告 PPT 时使用。基于 ppt-master 改造。
tools: []
version: "1.0.0"
author: allo-official
required_env: []
optional_env:
  - OPENAI_API_KEY
  - GEMINI_API_KEY
  - PEXELS_API_KEY
  - PIXABAY_API_KEY
credentials:
  - key: OPENAI_API_KEY
    label: OpenAI API Key
    description: 用于 AI 图片生成（gpt-image-2）。不配置则使用占位图。
    required: false
    secret: true
  - key: GEMINI_API_KEY
    label: Gemini API Key
    description: 用于 Gemini 图片生成（备选后端）。
    required: false
    secret: true
  - key: PEXELS_API_KEY
    label: Pexels API Key
    description: 用于 Pexels 图片搜索（免费申请：https://www.pexels.com/api/）。
    required: false
    secret: true
  - key: PIXABAY_API_KEY
    label: Pixabay API Key
    description: 用于 Pixabay 图片搜索（免费申请：https://pixabay.com/api/docs/）。
    required: false
    secret: true
---

# 慧评 PPT 生成器

> 来源: 基于 [ppt-master](https://github.com/hugohe3/ppt-master)（MIT）改造，适配课程报告场景。原作者: Hugo He。

## 首次安装（必须）

本 skill 依赖上游 Python 脚本和模板资源。首次使用前运行：

```bash
bash <SKILL_ROOT>/setup.sh
```

该脚本会 sparse clone 上游仓库，拉取 scripts、references、templates 并安装 Python 依赖。

如需 AI 图片生成，还需配置环境变量：
```bash
cp <SKILL_ROOT>/.env.example <SKILL_ROOT>/.env
# 编辑 .env 设置 OPENAI_API_KEY

## 这个 Skill 做什么

将课程报告文档（PDF/DOCX/Markdown）转换为**原生可编辑的 .pptx**：

- ✅ **原生 DrawingML shapes** — 每个元素可在 PowerPoint 里直接编辑
- ✅ **入场动画和转场** — PowerPoint 原生动画
- ✅ **Speaker Notes** — 支持生成音频旁白
- ✅ **自定义模板** — 可套用 .pptx 模板
- ✅ **多格式源文件** — PDF/DOCX/XLSX/URL/Markdown

## 何时使用

**合适**：
- 需要在 PowerPoint 里编辑提交的正式课程报告
- 需要套用学校/院系 PPT 模板
- 需要 speaker notes 和音频旁白
- 需要从长文档自动生成演示稿

**不合适**：
- 快速网页演示（用 `huiping-html-deck`）
- 纯数据可视化（用 `huiping-incremental-evaluator`）
- 知识查询（用 `mingxue-kb-query`）

## 核心流水线

```
源文档 → 创建项目 → [模板] → Strategist → [图片生成] → Executor 逐页生成 → 质量检查 → 后处理 → 导出 PPTX
```

## 工作流

### Step 1 · 源文档处理

用户提供的材料，转换为 Markdown：

| 用户提供 | 命令 |
|----------|------|
| PDF 文件 | `python3 scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX 文件 | `python3 scripts/source_to_md/doc_to_md.py <file>` |
| XLSX 文件 | `python3 scripts/source_to_md/excel_to_md.py <file>` |
| 网页链接 | `python3 scripts/source_to_md/web_to_md.py <URL>` |
| Markdown | 直接读取 |

### Step 2 · 创建项目

```bash
python3 scripts/project_manager.py init <项目名> --format ppt169
python3 scripts/project_manager.py import-sources <项目路径> <源文件...> --move
```

格式选项：`ppt169`（默认 16:9）、`ppt43`（4:3）

### Step 3 · 模板选项

**默认自由设计**，不主动询问模板。

只有用户明确给出模板目录路径时才触发模板流程：
- `kind: brand` — 复制品牌标识（颜色/字体/Logo）
- `kind: layout` — 复制页面结构
- `kind: deck` — 复制完整模板

### Step 4 · Strategist 阶段（必须）

读取角色定义：`Read references/strategist.md`

**八项确认**（⛔ 阻塞点，必须等待用户确认）：

1. 画布格式
2. 页数范围
3. 目标受众
4. 风格目标
5. 配色方案
6. 图标使用方式
7. 排版计划（含公式渲染策略）
8. 图片使用方式

课程报告场景的常见确认：
- **受众**：答辩评委 / 课题组 / 课程老师
- **风格**：学术风格、数据驱动、清晰专业
- **配色**：与课程报告评价体系一致

**输出**：
- `<项目路径>/design_spec.md` — 设计规范
- `<项目路径>/spec_lock.md` — 执行锁定

### Step 5 · 图片获取（条件触发）

如果设计规范中有 `Acquire Via: ai` 或 `Acquire Via: web` 的行：

| 类型 | 加载参考 | 运行 |
|------|----------|------|
| AI 生成 | `references/image-generator.md` | `python3 scripts/image_gen.py --manifest <项目路径>/images/image_prompts.json` |
| 网络搜索 | `references/image-searcher.md` | `python3 scripts/image_search.py ...` |

### Step 6 · Executor 阶段

读取角色定义：
```
Read references/executor-base.md
Read references/shared-standards.md
Read references/executor-general.md  # 或 executor-consultant.md
```

**关键规则**：
- SVG 必须手写，不允许脚本批量生成
- 逐页顺序生成，不允许分组批量
- 每页生成前重新读取 `spec_lock.md`
- 生成完成后运行质量检查：
  ```bash
  python3 scripts/svg_quality_checker.py <项目路径>
  ```

### Step 7 · 后处理与导出

**三步流水线**（顺序执行，每步成功后才执行下一步）：

```bash
# 7.1 拆分 speaker notes
python3 scripts/total_md_split.py <项目路径>

# 7.2 SVG 后处理（图标嵌入、图片裁剪、文本扁平化）
python3 scripts/finalize_svg.py <项目路径>

# 7.3 导出 PPTX
python3 scripts/svg_to_pptx.py <项目路径>
```

**输出**：
- `exports/<项目名>_<时间戳>.pptx` — 原生可编辑 PPTX

**可选参数**：
- `-t <效果>` — 页面转场（fade/push/wipe/split/none）
- `-a <效果>` — 入场动画（auto/fade/none/mixed）
- `--merge-paragraphs` — 合并段落为可编辑文本框

## 课程报告专用工作流

```
课程报告 PDF/DOCX
       ↓
huiping-ppt-generator (Strategist + Executor)
       ↓
原生 .pptx（含动画、speaker notes）
       ↓
PowerPoint 打开编辑 → 提交/答辩
```

### 与评价体系配合

1. 先用 `huiping-incremental-evaluator` 生成六维评分
2. 用 `huiping-data-analysis-coach` 优化数据分析部分
3. 用 `huiping-literature-guide` 完善文献引用
4. 最后用本 skill 生成正式 PPT

## 安装依赖

本 skill 需要 Python 3.10+ 环境：

```bash
pip install -r requirements.txt
```

如果需要 AI 图片生成，配置 `.env`：
```bash
cp .env.example .env
# 编辑 .env 设置 OPENAI_API_KEY 等
```

## 资源文件

```
huiping-ppt-generator/
├── SKILL.md                  ← 你正在读
├── requirements.txt          ← Python 依赖
├── .env.example              ← 环境变量模板
├── scripts/
│   ├── source_to_md/         ← 源文档转换脚本
│   ├── project_manager.py    ← 项目管理
│   ├── image_gen.py          ← AI 图片生成
│   ├── image_search.py       ← 网络图片搜索
│   ├── svg_quality_checker.py← SVG 质量检查
│   ├── finalize_svg.py       ← SVG 后处理
│   ├── svg_to_pptx.py        ← PPTX 导出
│   └── total_md_split.py     ← Notes 拆分
├── templates/
│   ├── layouts/              ← 页面布局模板
│   ├── brands/               ← 品牌预设
│   ├── charts/               ← 图表模板
│   └── icons/                ← 图标库
└── references/
    ├── strategist.md         ← Strategist 角色定义
    ├── executor-base.md      ← Executor 基础规范
    ├── shared-standards.md   ← 共享技术约束
    └── ...                   ← 其他参考文档
```

## 核心设计原则

1. **原生可编辑** — 输出的每个元素都能在 PowerPoint 里直接修改
2. **手写 SVG** — 每页 SVG 由 AI 逐页手写，保证跨页视觉一致
3. **Spec Lock** — 颜色/字体/图标从 spec_lock.md 读取，不允许凭记忆
4. **质量门控** — svg_quality_checker.py 检查通过后才能导出
5. **课程导向** — 面向学术汇报场景优化设计规范和工作流
