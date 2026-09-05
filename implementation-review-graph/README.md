# Implementation Review Graph

A Codex skill for repeatedly executing this workflow:

```text
implement a plan → critically review it → triage findings → compare fixes
in parallel → order fixes by dependency → repair sequentially → verify
```

The main thread is the default sole writer. Subagents perform independent analysis, and one canonical Markdown run record keeps the workflow resumable without synchronized state files.

## Install for your user

From the directory containing the extracted `implementation-review-graph` folder:

```bash
target="$HOME/.agents/skills/implementation-review-graph"
mkdir -p "$(dirname "$target")"
rm -rf "$target"
cp -R implementation-review-graph "$target"
```

This intentionally replaces the complete skill directory rather than merging files. Back up custom changes outside any `.agents/skills` directory first; Codex can surface two skills with the same name when duplicate copies remain in scanned locations.

## Install in one repository

```bash
target="/path/to/repository/.agents/skills/implementation-review-graph"
mkdir -p "$(dirname "$target")"
rm -rf "$target"
cp -R implementation-review-graph "$target"
```

Codex normally detects skill changes automatically. Restart it when the skill does not appear.

## Invoke

Implicit invocation is disabled because the workflow can be expensive and changes code. Invoke it explicitly:

```text
$implementation-review-graph

Plan:
docs/plans/offline-synchronization.md

Review dimensions:
- requirements
- correctness and edge cases
- concurrency and lifecycle
- tests
- architecture and backwards compatibility

Constraints:
- Preserve existing public APIs.
- Do not add production dependencies.
- Preserve unrelated working-tree changes.
```

The omitted defaults are:

```text
Goal: Implement the plan completely and carry it through final verification.
Blocking threshold: none
```

`none` means there is no severity cutoff: every accepted, in-scope finding must be resolved. Severity is still used to prioritize work and determine review depth. To permit lower-severity findings to be deferred, explicitly set `Blocking threshold: P0`, `P1`, `P2`, or `P3`.

A compact invocation also works:

```text
$implementation-review-graph Implement docs/plan.md.
```

## Run record

Each new invocation creates:

```text
.agent-runs/<run-id>/RUN.md
```

That single file contains the objective, baseline, acceptance criteria, implementation graph, findings, root-cause decisions, fix graph, validation evidence, final review, and completion gate.

## Package layout

```text
implementation-review-graph/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── RUN.md.template
└── references/
    └── subagent-prompts.md
```
