---
name: huiping-report-review
description: Use when reviewing a single course report draft for structure, logic, completeness, formatting, chart explanation, terminology, references, or student-facing revision suggestions.
---

# Huiping Report Review

## Overview

Review one course report draft as a document-quality expert. Output concise revision guidance and structured data for report health visualizations.

## When to Use

- User uploads or pastes one report draft for review.
- User asks for 报告体检, 结构检查, 文档质控, 格式检查, 修改建议, or 图表/引用规范检查.
- `huiping-incremental-evaluator` needs initial or final draft review inputs.

## Review Checklist

| Area | Checks |
|---|---|
| Structure | Title, abstract, background, method, experiment, result, conclusion, references |
| Logic | Problem statement, argument chain, evidence-to-claim alignment |
| Figures and tables | Captions, units, readability, interpretation in text |
| Terminology | Course concepts used accurately and consistently |
| References | Citation relevance, format, and connection to claims |
| Writing quality | Clarity, concision, academic tone, section transitions |

## Visualization Output Contract

Always include:

```json
{
  "visualization_payload": {
    "report_health": {
      "overall_score": 0,
      "sections": [
        {"name": "", "completeness": 0, "issues": 0, "status": ""}
      ],
      "issue_distribution": [
        {"category": "", "count": 0, "severity": ""}
      ],
      "revision_priorities": [
        {"priority": 1, "area": "", "suggestion": "", "expected_impact": ""}
      ]
    }
  }
}
```

Use `status` values `missing`, `weak`, `acceptable`, or `strong`. Use severity values `critical`, `warning`, or `info`.

## Response Format

1. Overall health conclusion.
2. High-impact revision priorities.
3. Section-level findings.
4. `visualization_payload` JSON.

## Common Mistakes

- Do not rewrite the whole report unless asked.
- Do not make unsupported domain claims; use `mingxue-kb-query` for course evidence.
- Do not only comment on language; prioritize structure, evidence, and reasoning.
