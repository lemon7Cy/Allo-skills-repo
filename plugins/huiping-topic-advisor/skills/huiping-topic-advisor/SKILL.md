---
name: huiping-topic-advisor
description: Use when helping students choose course report topics, evaluate topic innovation, match interests with datasets, assess feasibility, or prepare visual topic recommendation cards.
---

# Huiping Topic Advisor

## Overview

Help students move from broad interests to feasible, course-aligned report topics. Evaluate topic innovation, feasibility, course relevance, and data availability.

## When to Use

- User asks for 选题, 题目推荐, 创新性评估, 可行性分析, 兴趣匹配, or 数据资源匹配.
- A teacher wants topic diversity or topic-quality review.
- `huiping-incremental-evaluator` needs innovation evidence for a report topic.

## Topic Evaluation Criteria

| Criterion | Checks |
|---|---|
| Course relevance | Matches course objectives and required concepts |
| Innovation | Specific scenario, comparison angle, method variation, or data perspective |
| Feasibility | Scope fits time, available data, and student ability |
| Data availability | Dataset exists or collection path is clear |
| Learning value | Topic can demonstrate understanding, analysis, and reflection |

## Visualization Output Contract

Always include:

```json
{
  "visualization_payload": {
    "topic_recommendations": {
      "topics": [
        {
          "title": "",
          "innovation_score": 0,
          "feasibility_score": 0,
          "course_relevance_score": 0,
          "data_availability_score": 0,
          "reason": "",
          "risks": []
        }
      ],
      "topic_matrix": [
        {"title": "", "x_feasibility": 0, "y_innovation": 0, "size_relevance": 0}
      ],
      "next_questions": []
    }
  }
}
```

## Response Format

1. Recommended topic shortlist.
2. Innovation and feasibility comparison.
3. Required data and knowledge preparation.
4. Risks and narrowing suggestions.
5. `visualization_payload` JSON.

## Common Mistakes

- Do not recommend topics that are too broad to evaluate.
- Do not optimize only for novelty; feasibility and course relevance matter.
- Do not assign a topic without explaining what data or evidence can support it.
