---
name: huiping-incremental-evaluator
description: Use when evaluating course report initial and final drafts, comparing student growth, scoring report quality, producing expert feedback, or generating visualization JSON for Mingxue incremental evaluation.
---

# Huiping Incremental Evaluator

## Overview

Evaluate course reports by comparing the initial draft and final draft. Prioritize visible student growth, evidence-backed scoring, and structured visualization output for Allo dashboards.

## When to Use

- User asks to compare 初稿 and 终稿.
- User asks for 课程报告评价, 增量评价, 六维评分, 能力提升, 教师评语, or 学生反思.
- User needs JSON for radar charts, expert panels, growth chains, or evaluation report export.

Do not use for simple knowledge-base Q&A; use `mingxue-kb-query` instead.

## Required Inputs

Ask for missing core inputs before scoring:

| Input | Required | Purpose |
|---|---:|---|
| Course name and report requirements | Yes | Anchor scoring to the course |
| Initial draft | Yes | Baseline evidence |
| Final draft | Yes | Final evidence |
| Scoring rubric | Recommended | Weight dimensions |
| Code/data/reference attachments | Optional | Raise confidence for data and literature scores |

## Evaluation Flow

1. Run `material_check` to record available materials and missing-artifact risks.
2. Review initial and final drafts separately for structure, logic, evidence, data analysis, citations, and format.
3. Compare section-level changes and extract key additions.
4. Score six dimensions: 创新性, 数据分析深度, 完整性, 文献引用, 结论合理性, 格式规范性.
5. Build an expert panel with domain, data, literature, document-quality, innovation, and integrated-evaluation views.
6. Identify growth evidence and AI-assistance risks.
7. Output teacher comments and student reflection questions.

## Visualization Output Contract

Always include a `visualization_payload` block with these keys:

```json
{
  "visualization_payload": {
    "material_check": {
      "completeness_score": 0,
      "items": [],
      "risks": []
    },
    "draft_delta_map": {
      "sections": [],
      "key_additions": []
    },
    "six_dimension_scores": {
      "dimensions": [],
      "overall": {"initial": 0, "final": 0, "delta": 0}
    },
    "expert_panel": {
      "experts": [],
      "consensus": "",
      "disagreements": []
    },
    "growth_evidence_chain": {
      "growth_points": [],
      "ai_assistance_risks": []
    },
    "evaluation_report": {
      "teacher_comment": "",
      "student_reflection_questions": [],
      "recommended_grade_band": "",
      "next_feedback_actions": []
    }
  }
}
```

Use scores from 0 to 100. Use `confidence` from 0 to 1. For `authenticity_signal`, use `low`, `medium`, `medium_high`, or `high`.

For a complete showcase-ready example, use `references/demo-visualization-payload.json`. It contains a battery-course initial/final draft scenario with all six visual modules populated for front-end mockups and demo validation.

## Radar Chart Rendering

When the user needs a ready-to-embed radar chart, render the six-dimension scores with the bundled zero-dependency SVG renderer:

```bash
python3 references/scripts/render_radar_svg.py references/demo-visualization-payload.json radar.svg
```

Use the same command with any generated evaluation JSON that follows the `visualization_payload.six_dimension_scores` contract. The output SVG can be embedded in an Allo page, PPT, Markdown report, or exported evaluation artifact.

## Single-File Allo Install Compatibility

Allo may install only this `SKILL.md` from `marketplace.json`. If `references/` files are not available after marketplace installation, recreate the radar renderer from this inline copy:

```bash
cat > render_radar_svg.py <<'PY'
#!/usr/bin/env python3
import html
import json
import math
import sys
from pathlib import Path

WIDTH = 900
HEIGHT = 720
CX = WIDTH / 2
CY = 365
RADIUS = 230
MAX_SCORE = 100


def load_dimensions(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    scores = payload["visualization_payload"]["six_dimension_scores"]
    dimensions = scores["dimensions"]
    if len(dimensions) < 3:
        raise ValueError("six_dimension_scores.dimensions must contain at least 3 items")
    return payload, dimensions, scores["overall"]


def point_for(index, total, score):
    angle = -math.pi / 2 + (2 * math.pi * index / total)
    radius = RADIUS * max(0, min(score, MAX_SCORE)) / MAX_SCORE
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def axis_point(index, total, radius=RADIUS):
    angle = -math.pi / 2 + (2 * math.pi * index / total)
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def points_attr(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render_svg(payload, dimensions, overall):
    total = len(dimensions)
    title = payload.get("demo_case", {}).get("report_topic", "Huiping Incremental Evaluation")
    course = payload.get("demo_case", {}).get("course_name", "Course Report")
    grid = []
    for step in range(20, 101, 20):
        ring = [point_for(i, total, step) for i in range(total)]
        grid.append(f'<polygon points="{points_attr(ring)}" fill="none" stroke="#d8dee9" stroke-width="1" />')
    axes = []
    labels = []
    for i, dimension in enumerate(dimensions):
        x, y = axis_point(i, total)
        axes.append(f'<line x1="{CX:.1f}" y1="{CY:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#c5ceda" stroke-width="1" />')
        label_x, label_y = axis_point(i, total, RADIUS + 52)
        anchor = "middle"
        if label_x < CX - 30:
            anchor = "end"
        elif label_x > CX + 30:
            anchor = "start"
        labels.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" class="axis-label">{html.escape(dimension["name"])}</text>')
    initial_points = [point_for(i, total, d["initial"]) for i, d in enumerate(dimensions)]
    final_points = [point_for(i, total, d["final"]) for i, d in enumerate(dimensions)]
    score_rows = []
    for i, dimension in enumerate(dimensions):
        x = 95 + (i % 3) * 245
        y = 610 + (i // 3) * 32
        text = f'{dimension["name"]}: {dimension["initial"]} -> {dimension["final"]} (+{dimension["delta"]})'
        score_rows.append(f'<text x="{x}" y="{y}" class="score-row">{html.escape(text)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Huiping six dimension radar chart">
  <style>.title{{font:700 26px sans-serif;fill:#152235}}.subtitle,.legend{{font:16px sans-serif;fill:#5e6b7a}}.axis-label{{font:700 15px sans-serif;fill:#26384d}}.score-row{{font:14px sans-serif;fill:#405268}}.overall{{font:700 17px sans-serif;fill:#152235}}</style>
  <rect width="100%" height="100%" rx="28" fill="#f7f9fc" />
  <rect x="32" y="32" width="836" height="656" rx="24" fill="#ffffff" stroke="#e3e8ef" />
  <text x="70" y="82" class="title">六维能力增量雷达图</text>
  <text x="70" y="112" class="subtitle">{html.escape(course)} | {html.escape(title)}</text>
  <text x="70" y="148" class="overall">总分：初稿 {overall["initial"]} / 终稿 {overall["final"]} / 提升 +{overall["delta"]}</text>
  <g>{''.join(grid)}</g><g>{''.join(axes)}</g>
  <polygon points="{points_attr(initial_points)}" fill="#8aa4ff" fill-opacity="0.20" stroke="#5d74d8" stroke-width="3" />
  <polygon points="{points_attr(final_points)}" fill="#18b989" fill-opacity="0.24" stroke="#0f9f75" stroke-width="3" />
  <polyline points="{points_attr(initial_points + [initial_points[0]])}" fill="none" stroke="#5d74d8" stroke-width="3" />
  <polyline points="{points_attr(final_points + [final_points[0]])}" fill="none" stroke="#0f9f75" stroke-width="3" />
  <g>{''.join(labels)}</g>
  <circle cx="640" cy="145" r="7" fill="#5d74d8" /><text x="656" y="150" class="legend">初稿</text>
  <circle cx="715" cy="145" r="7" fill="#0f9f75" /><text x="731" y="150" class="legend">终稿</text>
  <g>{''.join(score_rows)}</g>
</svg>'''


def main(argv):
    if len(argv) != 3:
        print("Usage: render_radar_svg.py input-payload.json output.svg", file=sys.stderr)
        return 2
    payload, dimensions, overall = load_dimensions(Path(argv[1]))
    Path(argv[2]).write_text(render_svg(payload, dimensions, overall), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
PY
python3 render_radar_svg.py evaluation.json radar.svg
```

The `evaluation.json` file must contain the same `visualization_payload.six_dimension_scores` shape defined above. If the full `references/` directory is installed, prefer the maintained script at `references/scripts/render_radar_svg.py`; otherwise use this inline fallback.

## Human-Readable Output

Before the JSON, provide:

1. Overall conclusion.
2. Top three growth points.
3. Top three risks or teacher follow-up questions.
4. Six-dimension score summary.

## Scoring Guidance

| Dimension | Look For |
|---|---|
| 创新性 | Topic specificity, scenario relevance, independent problem framing |
| 数据分析深度 | Dataset explanation, method fit, experiment design, chart interpretation, error analysis |
| 完整性 | Background, method, experiment, result, conclusion, references |
| 文献引用 | Relevant sources, citation-to-argument connection, course-material grounding |
| 结论合理性 | Claims supported by data and analysis, no overreach |
| 格式规范性 | Structure, figures, tables, terminology, reference format |

## Common Mistakes

- Do not score polished language as real understanding without evidence.
- Do not hide missing code/data artifacts; lower confidence and flag follow-up.
- Do not invent citations; call `mingxue-kb-query` or mark evidence as unavailable.
- Do not return prose only; visualization JSON is required for showcase use.
