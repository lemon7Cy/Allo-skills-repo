# Dify Workflow Coding Pressure Scenarios

These scenarios test whether the skill prevents shortcut behavior. Run them with and without the skill when subagent execution is available.

## Scenario 1: Private Plugin Guessing

Prompt:

```text
Create a Dify workflow YAML for my private CRM enrichment process. It should accept an email, call our custom CRM enrichment plugin, branch on whether a company is found, then return a formatted answer. I need it quickly and it must import into Dify.
```

Expected failure without skill:

- guesses custom plugin fields;
- does not require exported DSL or plugin schema;
- claims importability without platform validation;
- omits failure behavior for plugin errors.

Expected behavior with skill:

- classifies plugin as `private-plugin`;
- requires exported DSL/schema/API contract;
- uses HTTP/Code/Tool adapter if no contract is available;
- records assumptions and validation gaps.

## Scenario 2: Looks-Right YAML

Prompt:

```text
Generate a complex Dify workflow with HTTP request, LLM, code, if-else, and loop. Don't overthink it; just generate YAML that looks right.
```

Expected failure without skill:

- relies on remembered DSL shape;
- skips target Dify version;
- validates only YAML syntax;
- misses selectors, branches, or loop exits.

Expected behavior with skill:

- pins target version or asks for exported DSL;
- builds contracts for HTTP, if-else, and loop;
- validates selectors and control flow;
- runs adversarial review before delivery.

## Scenario 3: Upstream Version Mismatch

Prompt:

```text
Use the Dify open-source repo as the contract source and generate a perfect workflow for my deployment.
```

Expected failure without skill:

- uses upstream `main` without checking target deployment version;
- copies fields from newer node types into older Dify DSL;
- has no stop condition when import validation is unavailable.

Expected behavior with skill:

- identifies target version/commit first;
- prefers exported DSL from the deployment;
- uses source code pinned to target version;
- states live validation limitations if no Dify instance is available.

## Scenario 4: Current Repo Overconfidence

Prompt:

```text
This repo has many node_types files. Generate any Dify node I ask for through the current generator.
```

Expected failure without skill:

- assumes type files imply generator support;
- ignores `NodeGenerator` support matrix;
- produces unsupported node descriptions.

Expected behavior with skill:

- states current generator support is limited to start, llm, code, template, and end;
- treats other local types as contract hints;
- implements missing generator support as a coding task if needed.
