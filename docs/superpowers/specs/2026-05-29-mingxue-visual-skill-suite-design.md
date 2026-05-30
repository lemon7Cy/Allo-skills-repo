# Mingxue Visual Skill Suite Design

## Purpose

Mingxue Visual Skill Suite turns the existing Mingxue course knowledge base into a visual, multi-skill teaching evaluation system for course reports. The first showcase focuses on incremental evaluation: comparing a student's initial draft and final draft to show real growth under AI-assisted learning.

The suite is designed for Allo's skill marketplace. Each skill has a clear teaching role, produces structured outputs, and can be combined in an Allo agent or front-end workflow. The user-facing demo should feel like a visual evaluation cockpit, not a chat-only assistant.

## Source Context

The PPT positions Mingxue as a response to course-report assessment challenges in the generative AI era. Its core claims are:

- Course reports are common and strongly affected by student AI usage.
- Teachers need to evaluate the student's real understanding, programming ability, writing ability, and growth.
- The proposed solution covers topic exploration, report writing, revision, evaluation, and reflection.
- The technical architecture uses a knowledge base layer, an intelligent orchestration layer, and an application layer.
- The knowledge base combines a material library, corpus library, and rubric library.
- The workflow uses multiple expert agents: domain knowledge, data analysis, literature guide, document quality control, innovation review, and integrated evaluation.
- The most distinctive teaching innovation is process-oriented incremental evaluation between initial and final drafts.

## Design Direction

The suite will use multiple Allo skills rather than one monolithic skill. This preserves marketplace modularity while still supporting a complete demonstration flow.

The showcase priority is visualization. Each skill should return both human-readable feedback and structured JSON for cards, charts, heatmaps, radar charts, waterfall charts, expert panels, and exportable reports.

## Skill Suite

### Existing Skill

#### `mingxue-kb-query`

Role: course knowledge and literature retrieval base.

Responsibilities:

- Answer course knowledge questions with citations.
- Retrieve relevant materials from the existing knowledge base.
- Provide source snippets, metadata, and confidence when called by other skills.

This skill stays focused on retrieval and citation. It does not own the teaching workflow.

### New Skills

#### `huiping-incremental-evaluator`

Role: primary showcase entry for initial-final draft evaluation.

Responsibilities:

- Check submitted materials for completeness.
- Compare initial and final drafts by section, argument, data analysis, literature usage, conclusion quality, and format.
- Produce six-dimension initial/final/delta scores.
- Fuse expert outputs from other skills.
- Produce growth evidence chains and teacher-ready evaluation reports.
- Emit visual JSON for the main demo cockpit.

This is the lead skill for the first version.

#### `huiping-report-review`

Role: single-report health check.

Responsibilities:

- Review structure, logic, format, terminology, chart explanation, references, and writing quality.
- Return chapter-level completeness and problem distribution.
- Provide revision suggestions suitable for students.
- Support independent use for initial draft coaching.

#### `huiping-data-analysis-coach`

Role: data analysis guidance and evaluation.

Responsibilities:

- Assess whether the report explains datasets, methods, experiments, charts, code, and conclusions sufficiently.
- Recommend analysis routes and visualization choices.
- Identify missing code or weak evidence.
- Contribute to the data-analysis-depth score in the incremental evaluator.

#### `huiping-literature-guide`

Role: literature and knowledge guidance.

Responsibilities:

- Call `mingxue-kb-query` for course materials and literature evidence.
- Build reading paths, concept summaries, and citation suggestions.
- Evaluate whether references support report arguments.
- Contribute to the literature-citation and domain-knowledge evidence in the incremental evaluator.

#### `huiping-topic-advisor`

Role: topic exploration and innovation assessment.

Responsibilities:

- Match student interests, course objectives, available datasets, and knowledge points.
- Recommend candidate topics.
- Score topic innovation, feasibility, relevance, and data availability.
- Contribute to the innovation score in the incremental evaluator.

## Primary Showcase Flow

The first demonstration should follow an incremental evaluation storyline:

1. User uploads or selects the student's initial draft, final draft, course requirements, and optional code/data/reference attachments.
2. `huiping-incremental-evaluator` runs material completeness checks.
3. It calls supporting skills in parallel:
   - `huiping-report-review` for the initial draft.
   - `huiping-report-review` for the final draft.
   - `huiping-data-analysis-coach` for data analysis depth.
   - `huiping-literature-guide` for knowledge and citation quality.
   - `huiping-topic-advisor` for topic innovation.
4. `huiping-incremental-evaluator` fuses results into visual outputs.
5. The Allo front end renders the results as an evaluation cockpit.
6. The user exports a teacher comment, student reflection tasks, and a structured evaluation report.

## Visual Modules

### 1. `material_check`

Purpose: show what materials are available and how missing materials affect evaluation confidence.

Visual forms:

- Material checklist cards.
- Completeness progress bar.
- Missing-item risk tags.

Required JSON:

```json
{
  "material_check": {
    "completeness_score": 86,
    "items": [
      {"name": "初稿", "status": "available", "confidence": 0.98},
      {"name": "终稿", "status": "available", "confidence": 0.99},
      {"name": "课程评分标准", "status": "available", "confidence": 0.9},
      {"name": "代码附件", "status": "missing", "impact": "数据分析深度评分置信度下降"}
    ],
    "risks": ["未提供代码附件，数据分析能力判断主要基于报告文本"]
  }
}
```

### 2. `draft_delta_map`

Purpose: show where the student changed the report.

Visual forms:

- Section delta bar chart.
- Revision heatmap.
- Key addition list.

Required JSON:

```json
{
  "draft_delta_map": {
    "sections": [
      {"name": "研究背景", "initial_words": 320, "final_words": 520, "delta_type": "expanded"},
      {"name": "数据分析", "initial_words": 460, "final_words": 980, "delta_type": "substantially_improved"},
      {"name": "结论", "initial_words": 180, "final_words": 430, "delta_type": "strengthened"}
    ],
    "key_additions": [
      {"section": "数据分析", "summary": "新增电池容量衰减趋势对比与误差分析"},
      {"section": "文献综述", "summary": "补充 3 篇与 SOC 估计相关文献"}
    ]
  }
}
```

### 3. `six_dimension_scores`

Purpose: turn report quality into a visible ability profile.

Dimensions:

- 创新性
- 数据分析深度
- 完整性
- 文献引用
- 结论合理性
- 格式规范性

Visual forms:

- Initial/final dual radar chart.
- Dimension delta bar chart.
- Dimension explanation cards.

Required JSON:

```json
{
  "six_dimension_scores": {
    "dimensions": [
      {"name": "创新性", "initial": 68, "final": 80, "delta": 12, "evidence": "选题从泛泛讨论转向具体数据集场景"},
      {"name": "数据分析深度", "initial": 55, "final": 82, "delta": 27, "evidence": "新增实验对比、误差分析和图表解释"},
      {"name": "完整性", "initial": 70, "final": 88, "delta": 18, "evidence": "补齐方法、实验、结论与参考文献"}
    ],
    "overall": {"initial": 66, "final": 84, "delta": 18}
  }
}
```

### 4. `expert_panel`

Purpose: show multi-expert collaboration and score fusion.

Visual forms:

- Expert cards.
- Contribution bars.
- Consensus and disagreement notes.
- Risk tags.

Required JSON:

```json
{
  "expert_panel": {
    "experts": [
      {"name": "领域知识专家", "score": 86, "confidence": 0.92, "view": "核心概念使用准确，课程相关性较强"},
      {"name": "数据分析专家", "score": 81, "confidence": 0.78, "view": "分析路线明显增强，但缺少代码附件支撑"},
      {"name": "文档质控专家", "score": 88, "confidence": 0.9, "view": "结构完整，图表说明仍可加强"},
      {"name": "创新性评审专家", "score": 79, "confidence": 0.84, "view": "选题有一定场景化改进，但方法创新有限"}
    ],
    "consensus": "终稿相比初稿有显著提升，主要体现在数据分析深度和报告完整性",
    "disagreements": ["数据分析专家因缺少代码附件给出较低置信度"]
  }
}
```

### 5. `growth_evidence_chain`

Purpose: answer where the student truly improved.

Visual forms:

- Ability delta waterfall chart.
- Evidence timeline.
- AI-assistance risk notes.

Required JSON:

```json
{
  "growth_evidence_chain": {
    "growth_points": [
      {
        "ability": "数据分析能力",
        "delta": 27,
        "evidence_before": "初稿仅描述数据来源，缺少实验设计",
        "evidence_after": "终稿加入容量衰减曲线、误差对比和结果解释",
        "authenticity_signal": "medium_high"
      },
      {
        "ability": "文献理解能力",
        "delta": 16,
        "evidence_before": "引用较少且缺少观点关联",
        "evidence_after": "新增文献对比并用于解释方法选择",
        "authenticity_signal": "medium"
      }
    ],
    "ai_assistance_risks": [
      "语言流畅度提升明显，但需结合课堂答辩确认学生理解深度"
    ]
  }
}
```

### 6. `evaluation_report`

Purpose: produce teacher-ready output.

Visual forms and exports:

- Teacher comment editor.
- Student reflection cards.
- Grade band and next-action list.
- PDF, Word, or Markdown export.

Required JSON:

```json
{
  "evaluation_report": {
    "teacher_comment": "该报告终稿相比初稿在数据分析深度、结构完整性和结论合理性方面提升明显...",
    "student_reflection_questions": [
      "你在终稿中新增的数据分析结果如何支撑报告结论？",
      "哪些修改来自你自己的理解深化，哪些来自 AI 辅助建议？"
    ],
    "recommended_grade_band": "良好-优秀",
    "next_feedback_actions": ["要求学生补充代码说明", "答辩中追问误差分析依据"]
  }
}
```

## Front-End Contract

All new skills should support a `visualization_payload` output block. The block contains stable keys for the visual modules above. The front end should not infer scores or parse free text. It should only render the provided JSON.

Recommended screen layout:

- Header: course name, report topic, student identifier, evaluation status.
- Left rail: material check, delta comparison, six-dimension score, expert panel, growth chain, export.
- Main panel: active chart or visualization.
- Right panel: evidence, citations, expert views, and risks.
- Footer: export evaluation report and generate student reflection task.

## Evaluation Principles

The system must avoid presenting AI-generated scores as absolute truth. Every score should include evidence and confidence where possible.

Key principles:

- Evaluate growth, not only final polish.
- Distinguish writing fluency improvement from demonstrated understanding.
- Flag missing artifacts such as code or datasets.
- Cite knowledge-base evidence for domain claims.
- Encourage teacher confirmation through questions or oral defense when authenticity is uncertain.

## Marketplace Entries

Add these skills to `marketplace.json` after implementation:

```json
[
  {
    "name": "huiping-incremental-evaluator",
    "source": "./plugins/huiping-incremental-evaluator",
    "description": "课程报告初稿与终稿增量评价，输出六维评分、专家评价、成长证据链和可视化 JSON。",
    "version": "1.0.0"
  },
  {
    "name": "huiping-report-review",
    "source": "./plugins/huiping-report-review",
    "description": "审查课程报告结构、逻辑、格式、图表、引用和语言质量，输出报告体检结果。",
    "version": "1.0.0"
  },
  {
    "name": "huiping-data-analysis-coach",
    "source": "./plugins/huiping-data-analysis-coach",
    "description": "辅导和评价课程报告中的数据分析设计、图表解释、代码说明和实验结论。",
    "version": "1.0.0"
  },
  {
    "name": "huiping-literature-guide",
    "source": "./plugins/huiping-literature-guide",
    "description": "基于明学知识库进行文献导读、课程知识梳理、引用质量审查和阅读路径推荐。",
    "version": "1.0.0"
  },
  {
    "name": "huiping-topic-advisor",
    "source": "./plugins/huiping-topic-advisor",
    "description": "面向课程报告进行选题挖掘、创新性评估、可行性分析和数据资源匹配。",
    "version": "1.0.0"
  }
]
```

## First Implementation Slice

The first implementation should create all five new skill files with consistent contracts, but make `huiping-incremental-evaluator` the main polished showcase. The supporting skills can start as structured expert workflows that return normalized JSON and can be deepened later.

Initial scope:

- Create five plugin directories and `SKILL.md` files.
- Register them in `marketplace.json`.
- Define common visual JSON output blocks.
- Keep `mingxue-kb-query` as the retrieval dependency.
- Validate marketplace consistency and run existing tests.

Out of scope for the first slice:

- Building the actual Allo front-end dashboard.
- Implementing document parsing beyond what the runtime or user provides.
- Training scoring models.
- Producing class-level analytics dashboards.

## Open Follow-Up

After this suite is implemented, the next product design task should define the front-end visual dashboard and demo data pack for the incremental evaluation storyline.
