#!/usr/bin/env python3
"""Render Mingxue six-dimension scores as a standalone SVG radar chart."""

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
        raise ValueError(
            "six_dimension_scores.dimensions must contain at least 3 items"
        )
    return payload, dimensions, scores["overall"]


def point_for(index, total, score):
    angle = -math.pi / 2 + (2 * math.pi * index / total)
    radius = RADIUS * max(0, min(score, MAX_SCORE)) / MAX_SCORE
    x = CX + radius * math.cos(angle)
    y = CY + radius * math.sin(angle)
    return x, y


def axis_point(index, total, radius=RADIUS):
    angle = -math.pi / 2 + (2 * math.pi * index / total)
    x = CX + radius * math.cos(angle)
    y = CY + radius * math.sin(angle)
    return x, y


def points_attr(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render_svg(payload, dimensions, overall):
    total = len(dimensions)
    title = payload.get("demo_case", {}).get(
        "report_topic", "Huiping Incremental Evaluation"
    )
    course = payload.get("demo_case", {}).get("course_name", "Course Report")

    grid = []
    for step in range(20, 101, 20):
        ring = [point_for(i, total, step) for i in range(total)]
        grid.append(
            f'<polygon points="{points_attr(ring)}" fill="none" stroke="#d8dee9" stroke-width="1" />'
        )

    axes = []
    labels = []
    for i, dimension in enumerate(dimensions):
        x, y = axis_point(i, total)
        axes.append(
            f'<line x1="{CX:.1f}" y1="{CY:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#c5ceda" stroke-width="1" />'
        )

        label_x, label_y = axis_point(i, total, RADIUS + 52)
        anchor = "middle"
        if label_x < CX - 30:
            anchor = "end"
        elif label_x > CX + 30:
            anchor = "start"
        labels.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" class="axis-label">{html.escape(dimension["name"])}</text>'
        )

    initial_points = [
        point_for(i, total, d["initial"]) for i, d in enumerate(dimensions)
    ]
    final_points = [point_for(i, total, d["final"]) for i, d in enumerate(dimensions)]

    score_rows = []
    row_y = 610
    for i, dimension in enumerate(dimensions):
        x = 95 + (i % 3) * 245
        y = row_y + (i // 3) * 32
        text = f"{dimension['name']}: {dimension['initial']} -> {dimension['final']} (+{dimension['delta']})"
        score_rows.append(
            f'<text x="{x}" y="{y}" class="score-row">{html.escape(text)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Huiping six dimension radar chart">
  <style>
    .title {{ font: 700 26px "PingFang SC", "Microsoft YaHei", sans-serif; fill: #152235; }}
    .subtitle {{ font: 16px "PingFang SC", "Microsoft YaHei", sans-serif; fill: #5e6b7a; }}
    .axis-label {{ font: 700 15px "PingFang SC", "Microsoft YaHei", sans-serif; fill: #26384d; }}
    .legend {{ font: 15px "PingFang SC", "Microsoft YaHei", sans-serif; fill: #26384d; }}
    .score-row {{ font: 14px "PingFang SC", "Microsoft YaHei", sans-serif; fill: #405268; }}
    .overall {{ font: 700 17px "PingFang SC", "Microsoft YaHei", sans-serif; fill: #152235; }}
  </style>
  <rect width="100%" height="100%" rx="28" fill="#f7f9fc" />
  <rect x="32" y="32" width="836" height="656" rx="24" fill="#ffffff" stroke="#e3e8ef" />
  <text x="70" y="82" class="title">六维能力增量雷达图</text>
  <text x="70" y="112" class="subtitle">{html.escape(course)} | {html.escape(title)}</text>
  <text x="70" y="148" class="overall">总分：初稿 {overall["initial"]} / 终稿 {overall["final"]} / 提升 +{overall["delta"]}</text>

  <g>{"".join(grid)}</g>
  <g>{"".join(axes)}</g>
  <polygon points="{points_attr(initial_points)}" fill="#8aa4ff" fill-opacity="0.20" stroke="#5d74d8" stroke-width="3" />
  <polygon points="{points_attr(final_points)}" fill="#18b989" fill-opacity="0.24" stroke="#0f9f75" stroke-width="3" />
  <polyline points="{points_attr(initial_points + [initial_points[0]])}" fill="none" stroke="#5d74d8" stroke-width="3" />
  <polyline points="{points_attr(final_points + [final_points[0]])}" fill="none" stroke="#0f9f75" stroke-width="3" />
  <g>{"".join(labels)}</g>

  <circle cx="640" cy="145" r="7" fill="#5d74d8" />
  <text x="656" y="150" class="legend">初稿</text>
  <circle cx="715" cy="145" r="7" fill="#0f9f75" />
  <text x="731" y="150" class="legend">终稿</text>
  <g>{"".join(score_rows)}</g>
</svg>
'''


def main(argv):
    if len(argv) != 3:
        print(
            "Usage: render_radar_svg.py input-payload.json output.svg", file=sys.stderr
        )
        return 2

    input_path = Path(argv[1])
    output_path = Path(argv[2])
    payload, dimensions, overall = load_dimensions(input_path)
    output_path.write_text(render_svg(payload, dimensions, overall), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
