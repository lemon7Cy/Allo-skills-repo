# Dify Workflow Review Checklist

Use this checklist after implementing or modifying a Dify workflow DSL.

## Importability

- YAML parses without errors.
- top-level structure includes `app`, `kind`, `version`, and `workflow`.
- `workflow.graph.nodes` and `workflow.graph.edges` exist and are lists.
- every node has `id`, `type`, `data.type`, `position`, and dimensions expected by the target DSL.
- every edge references existing source and target node IDs.
- every edge `data.sourceType` and `data.targetType` match connected nodes.

## Version Compatibility

- target Dify version/commit is stated.
- node fields are compatible with that version.
- upstream `main` fields are not used for older deployments without confirmation.
- exported DSL from target platform is preferred for uncertain nodes.

## Variable Flow

- every `value_selector` points to an existing node and output/input key.
- LLM outputs are referenced as `text` unless contract says otherwise.
- Start variables have valid input types and names.
- End outputs reference reachable upstream values.
- Template variables are declared and use valid selectors.
- Code node variables match `main()` parameter names exactly.
- Code node returned dict keys match declared outputs exactly.

## Control Flow

- every branch can be reached.
- every branch has a sensible continuation or terminal output.
- loops/iterations have valid inputs and termination behavior.
- error branches do not create dead-end data flow unless intentional.

## External Integrations

- HTTP/tool/plugin nodes have request schema, auth strategy, and response shape.
- private plugin fields come from exported DSL/schema, not guesswork.
- failure behavior is explicit: terminate, continue, fallback, or default value.
- secrets are not hardcoded in YAML.

## LLM and Prompt Quality

- prompts state task, format, and constraints clearly.
- downstream code parsing does not depend on vague prose when structured output is possible.
- model provider/name are available in the target Dify deployment.
- temperature and token settings fit the task.

## Final Delivery Evidence

- static validation command or manual checklist result is recorded.
- live import/run result is recorded when available.
- unresolved assumptions are listed.
- final workflow file path is included.
- import instructions are included.
