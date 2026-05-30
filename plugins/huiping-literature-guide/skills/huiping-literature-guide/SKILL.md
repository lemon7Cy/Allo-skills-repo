---
name: huiping-literature-guide
description: Use when guiding course-report literature reading, building concept maps, checking citation quality, recommending reading paths, or connecting report arguments to Mingxue knowledge-base evidence.
---

# Huiping Literature Guide

## Overview

Guide literature reading and citation use for course reports. Use `mingxue-kb-query` as the evidence source when course knowledge, papers, or citations are needed.

## When to Use

- User asks for 文献导读, 阅读路径, 参考文献, 引用建议, 知识脉络, or concept explanation for a report.
- A report needs citation-quality or knowledge-grounding review.
- `huiping-incremental-evaluator` needs expert input for literature and domain evidence.

## Retrieval Rules

- Use `mingxue-kb-query` for Mingxue course knowledge and literature evidence.
- Use answer mode for concept grounding and research mode for paper/reference discovery.
- Cite only returned evidence. Do not invent document names, authors, pages, or claims.

## Visualization Output Contract

Always include:

```json
{
  "visualization_payload": {
    "literature_map": {
      "core_concepts": [
        {"name": "", "role": "", "related_terms": []}
      ],
      "reading_path": [
        {"order": 1, "topic": "", "reason": ""}
      ],
      "citation_review": {
        "score": 0,
        "strengths": [],
        "gaps": []
      },
      "evidence_sources": [
        {"document": "", "section_type": "", "similarity": 0, "use": ""}
      ]
    }
  }
}
```

## Response Format

1. Literature guidance summary.
2. Concept and reading path.
3. Citation-quality findings.
4. Evidence sources from the knowledge base.
5. `visualization_payload` JSON.

## Common Mistakes

- Do not return generic reading advice without tying it to the report topic.
- Do not cite source titles that were not retrieved.
- Do not overvalue citation count; judge whether citations support claims.
