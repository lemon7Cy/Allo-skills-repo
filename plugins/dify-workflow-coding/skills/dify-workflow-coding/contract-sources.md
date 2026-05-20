# Dify Workflow Contract Sources

Use this reference before implementing non-basic Dify workflow nodes.

## Source Priority

1. Exported DSL from the exact target Dify deployment.
2. Dify source code pinned to the target version or commit.
3. Local repo examples and Pydantic node types.
4. User-provided plugin/tool/API contract.
5. Memory or guesswork: not allowed for final DSL fields.

## Public Dify Source Map

The upstream repository is `https://github.com/langgenius/dify`.

Useful paths:

- `web/app/components/workflow/types.ts`: core workflow graph, node, edge, variable, and block enums.
- `web/app/components/workflow/nodes/*/types.ts`: per-node data types.
- `web/app/components/workflow/nodes/*`: default values, validators, output variable helpers, and UI constraints.
- `api/`: backend import, execution, and validation behavior when needed.

Native node directories seen in current upstream include:

- `agent`
- `answer`
- `assigner`
- `code`
- `data-source`
- `document-extractor`
- `end`
- `http`
- `human-input`
- `if-else`
- `iteration`
- `knowledge-retrieval`
- `llm`
- `loop`
- `parameter-extractor`
- `question-classifier`
- `start`
- `template-transform`
- `tool`
- `trigger-plugin`
- `trigger-schedule`
- `trigger-webhook`
- `variable-assigner`

## Version Rules

- Always identify target Dify version or commit before using upstream contracts.
- If the target deployment is older than upstream `main`, do not copy new node fields blindly.
- If version is unknown, prefer exported DSL from the user's platform.
- If neither version nor exported DSL is available, mark non-basic node contracts as uncertain.

## Private Plugins and Custom Tools

Public Dify source can describe the plugin framework, but it cannot know a user's private plugin fields.

Require at least one:

- exported DSL fragment containing the private node;
- plugin manifest/schema;
- tool parameter schema;
- API contract with endpoint, auth, request, response, and errors.

If none is available, do not generate private node fields. Use one of these fallbacks:

- `http-request` node for API-backed integrations;
- `code` node for deterministic transformation or temporary mock behavior;
- `tool` node only when tool schema is available;
- documented placeholder with clear replacement instructions.

## Local Repository Caveat

This repository contains many Python `node_types`, but automatic generation currently only routes through a small subset. A local type file is a contract hint, not proof that `WorkflowGenerator` can create that node.
