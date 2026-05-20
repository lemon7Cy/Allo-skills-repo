---
name: dify-workflow-coding
description: Use when creating, fixing, reviewing, or optimizing Dify workflow DSL/YAML, especially when workflows include non-basic nodes, custom tools, plugins, private integrations, or must import and run on a target Dify version.
---

# Dify Workflow Coding

## Overview

Treat Dify workflow generation as a coding task, not a one-shot YAML generation task. Build from contracts, validate data flow, run adversarial review, and repair until the workflow is importable and runnable for the target Dify version.

## Hard Rules

- Do not invent private plugin, tool, or custom-node fields.
- Do not rely on memory for unfamiliar Dify node schemas.
- Do not use Dify upstream `main` unless the target deployment is compatible with it.
- Do not claim importability or runtime success without validation evidence.
- If a contract is missing, use a safe adapter node (`http-request`, `code`, or `tool`) or ask for an exported DSL/schema.

## Workflow

1. Define the target: Dify version/commit, workflow mode, expected inputs, final outputs, and sample run data.
2. Classify every node as `known-local`, `native-upstream`, `private-plugin`, or `unknown`.
3. Build a contract pack for every non-trivial node before writing YAML.
4. Implement the workflow DSL with clear node IDs, titles, edges, and variable selectors.
5. Run static validation before review.
6. Run adversarial review using `review-checklist.md`.
7. Fix blockers and repeat validation/review until no blocker remains.
8. Deliver final workflow path, validation evidence, assumptions, and any platform-validation gaps.

## Node Contract Classes

| Class | Contract source | Action |
| --- | --- | --- |
| `known-local` | This repo has type and generator support | Generate normally, then validate |
| `native-upstream` | Dify source or exported DSL | Implement from contract, add fixture if useful |
| `private-plugin` | User exported DSL, plugin schema, or API contract | Implement only from supplied contract |
| `unknown` | No reliable contract | Do not invent fields; use adapter or ask for contract |

Current local generator support is narrow: `start`, `llm`, `code`, `template`, and `end`. Other local `node_types` files are useful references, not proof that automatic generation is implemented.

## Contract Sources

Use `contract-sources.md` before implementing any node that is not already proven by local generated examples.

Best public Dify sources include:

- `web/app/components/workflow/types.ts`
- `web/app/components/workflow/nodes/*/types.ts`
- node default values and validators under `web/app/components/workflow/nodes/*`
- exported DSL from the target Dify deployment

For private plugins or tools, require one of:

- exported DSL fragment from the user's Dify instance;
- plugin/tool schema;
- API contract with input, auth, output, and error shape.

## Required Static Validation

Run `python3 validate_workflow.py <workflow.yml>` from this skill directory. Before final review, verify:

- YAML parses.
- top-level `app`, `kind`, `version`, `workflow`, `workflow.graph.nodes`, and `workflow.graph.edges` exist.
- node IDs are unique.
- every edge source and target exists.
- every `value_selector` references an existing node and valid variable path.
- LLM node outputs are referenced as `text` unless the target contract proves otherwise.
- Code node `main()` parameters match declared input variables.
- Code node returned dict keys match declared outputs.
- template variables are declared and come from existing selectors.
- branches, loops, and iterations have reachable exits.
- tool, HTTP, and plugin nodes have an explicit error strategy or documented failure behavior.

## Review Gate

Run an adversarial review after implementation. The review must try to break importability, runtime data flow, version compatibility, custom-node contracts, and error paths. Use `review-checklist.md`.

If the review finds blockers, fix them and rerun validation. Do not downgrade blockers to assumptions unless they are outside available contracts and explicitly disclosed.

## Stop Conditions

You may deliver only when all are true:

- no known blocker remains;
- static validation has been run and summarized;
- every non-local node cites a contract source or is implemented through a safe adapter;
- any unavailable live Dify import/run validation is explicitly called out;
- final answer includes the workflow file path and how to import it.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Guessing a private plugin node structure | Require exported DSL/schema or use an adapter |
| Using upstream `main` for an older Dify deployment | pin target version/commit first |
| Adding a node because `node_types` exists | check generator support and DSL examples |
| Only checking YAML syntax | validate graph edges and variable selectors |
| Claiming it runs without import/run evidence | state validation actually performed |
| Parsing LLM text with brittle code | constrain prompt output or add robust parsing/fallbacks |

## Pressure Tests

Use `pressure-scenarios.md` to test whether this skill prevents shortcut behavior under time pressure, private-plugin ambiguity, and version mismatch.
