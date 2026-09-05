---
name: implementation-review-graph
description: Run a non-trivial software plan through dependency-aware implementation, parallel critical review, evidence-based triage, ordered repair, and final regression. Invoke explicitly for full implementation-review-repair work; do not use for small localized edits.
---

# Implementation Review Graph

Use this workflow:

```text
plan → implementation graph → integration gate → parallel review
     → triage and root-cause clustering → parallel solution analysis
     → ordered fix graph → sequential repair → regression → final review
```

The governing principle is: **parallelize independent analysis; serialize code changes by default.**

## Core rules

1. Read every applicable `AGENTS.md` and repository instruction before working.
2. Preserve unrelated user changes. Do not reset, discard, broadly reformat, commit, push, merge, rebase, or open a pull request unless authorized.
3. Keep the main thread as the sole writer unless isolated worktrees, stable interfaces, and disjoint write sets make parallel implementation clearly safe.
4. Use subagents for independent analysis: review, investigation, solution comparison, and high-risk closure checks. They must not intentionally edit source code or workflow state.
5. Treat review comments as hypotheses until evidence supports them. Do not report preferences as defects.
6. Triage and deduplicate findings before designing fixes. Repair root causes rather than symptoms.
7. Revalidate every finding and recommendation against the current code immediately before changing it.
8. Require objective evidence at every gate: tests, builds, static checks, reproductions, or complete code-path analysis.
9. Keep one canonical run record and update it after each material transition.
10. Do not declare completion while a required finding remains unresolved or an acceptance criterion lacks evidence.

## Canonical run record

Create `.agent-runs/<run-id>/RUN.md` from [the run template](assets/RUN.md.template). Resume a specified existing run; otherwise create a unique directory and never overwrite an earlier run.

`RUN.md` is the single source of truth for the objective, baseline, acceptance criteria, implementation graph, review findings, root-cause decisions, fix graph, validation, final review, and completion status. Do not duplicate the same state in JSON or additional reports unless repository instructions require another format.

Use these values consistently:

- Run status: `active`, `blocked`, `complete`.
- Gate result: `pending`, `passed`, `blocked`.
- Implementation/fix node status: `pending`, `active`, `passed`, `blocked`, `superseded`.
- Acceptance-criterion status: `pending`, `passed`, `blocked`.
- Finding status: `investigate`, `open`, `fixed`, `rejected`, `duplicate`, `superseded`, `deferred`.

Dependency columns in the implementation and fix tables are the authoritative graph. Add a derived Mermaid diagram only when it materially improves readability. Keep evidence concise and link to files or logs instead of pasting large outputs.

## Defaults

Use these defaults unless the invocation overrides them:

- Goal: `Implement the plan completely and carry it through final verification.`
- Blocking threshold: none. There is no severity cutoff by default; every accepted, in-scope finding is required work. Severity determines order and review depth, not whether a finding may be ignored.
- Review dimensions: requirements, correctness, tests/edge cases, and architecture/compatibility.
- Writer policy: one active writer.
- Final review: one fresh reviewer; use more reviewers for security-sensitive, migration-heavy, concurrent, or otherwise high-risk changes.
- Final-review repair cycles: at most two before reassessing evidence, root cause, and scope. Do not defer a required finding merely to stop a loop.

An invocation may explicitly set `Blocking threshold: P0`, `P1`, `P2`, or `P3`. In that mode, findings at or above the threshold are required before completion, while lower-severity findings may be deferred with an owner, risk, and rationale. `none` does not mean that nothing blocks completion; it means that no severity cutoff applies, so all accepted, in-scope findings require resolution.

Severity reflects impact, not implementation effort:

| Severity | Meaning | Default handling |
|---|---|---|
| `P0` | Catastrophic: active data loss, critical compromise, destructive migration, or total outage | Repair first; skeptical solution review and independent closure required |
| `P1` | Serious correctness, security, integrity, or compatibility defect | Repair urgently; skeptical solution review and independent closure required |
| `P2` | Material but bounded defect affecting meaningful behavior, reliability, tests, or an acceptance criterion | Required repair in the default no-threshold mode |
| `P3` | Low-risk maintainability, clarity, cosmetic, or optional defect | Repair after higher-severity work in the default no-threshold mode; reject preferences that are not defects |

Any accepted finding needs a deterministic reproduction or failing test, direct file-and-code-path evidence, relevant tool output, or a demonstrated acceptance-criterion violation.

## Phase 1 — Baseline and plan gate

Before editing production code:

1. Inspect the plan, repository structure, applicable instructions, current Git status, and available validation commands.
2. Record the baseline commit and all pre-existing working-tree changes.
3. Define measurable acceptance criteria, constraints, and non-goals. Resolve ordinary ambiguity conservatively and record assumptions.
4. Audit the plan for missing requirements, incorrect dependencies, architecture or API conflicts, migrations, rollback, error paths, concurrency, security, performance, UX, and testability when relevant.
5. Revise the plan only when the requirements or repository evidence require it. Record material deviations. If the plan is explicitly approved, limit revisions to repository compatibility and testability.
6. Build the implementation graph in the run record.

Each implementation node needs an ID (`I-1`, `I-2`, ...), objective, dependencies, expected outputs or write set, validation method, done condition, and status.

Pass the plan gate only when every acceptance criterion is measurable and every implementation node is executable and testable.

## Phase 2 — Execute the implementation graph

Execute only nodes whose dependencies have passed or were superseded with rationale.

After each node:

1. Inspect the diff for scope drift and unrelated changes.
2. Run the smallest relevant validation.
3. Record the exact command or check and result.
4. Mark the node `passed` only when its done condition has evidence.
5. If validation fails, keep the node `active` while repairing it; mark it `blocked` only when progress requires an external decision, permission, dependency, or environment change.

Before review, pass the integration gate: build or compile the affected project, run relevant tests and static checks, inspect the aggregate implementation diff, and distinguish introduced failures from demonstrated pre-existing or environmental failures. If the requested implementation already exists, record it as the implementation output and begin at this gate.

## Phase 3 — Parallel independent review

Select only dimensions relevant to the change. Spawn one analysis-only subagent per independent dimension and run them in parallel. Use [the subagent prompts](references/subagent-prompts.md).

Every concern must include a stable title, affected acceptance criteria, severity, confidence, exact evidence, observed and expected behavior, impact, root-cause hypothesis, and a reproduction or decisive validation method. Do not request patches during discovery.

## Phase 4 — Triage and root-cause clustering

Normalize findings as `F-001`, `F-002`, and so on:

- `investigate`: evidence is insufficient.
- `open`: accepted and unresolved.
- `fixed`: sufficient targeted validation passed; record closure evidence.
- `rejected`: unsupported, incorrect, intentional, or outside scope; rationale required.
- `duplicate`: covered by another finding; canonical finding required.
- `superseded`: later code or a broader finding made it obsolete; rationale required.
- `deferred`: valid but postponed; owner and risk required. Under the default no-threshold policy, a deferred accepted finding prevents completion. With an explicit threshold, only findings below that threshold may be deferred without preventing completion.

Resolve every `investigate` finding before ordering repairs: promote it to `open` or assign a final disposition with rationale. Merge duplicate symptoms and group accepted findings into root-cause clusters `RC-01`, `RC-02`, and so on. A cluster is normally the unit of solution analysis and repair. When no finding remains `open`, skip solution analysis and repair and proceed to regression.

## Phase 5 — Analyze solutions in parallel

For each open root-cause cluster:

- Let the main thread select an obvious, low-risk fix and record why delegation adds no value.
- Otherwise spawn one analysis-only solution subagent per independent cluster and wait for all results before ordering fixes.
- For `P0`, `P1`, or high-blast-radius changes, use a separate skeptical reviewer.

A recommendation must state the confirmed root cause, viable options for non-trivial issues, tradeoffs, selected approach, affected files and contracts, dependencies, validation plan, likely regressions, and rollout or rollback implications when relevant. The main thread owns the final decision.

## Phase 6 — Construct and execute the fix graph

Create fix nodes `FIX-01`, `FIX-02`, and so on. Add dependencies when fixes share contracts or write sets, alter schemas or data formats, require migrations or reproductions, or when a broad fix may supersede a narrower one.

Order ready fixes by:

1. Security, data loss, corruption, build blockers, and severe correctness.
2. Foundational root causes and shared contracts.
3. Schema, migration, and API changes.
4. Dependent behavior fixes.
5. Tests, observability, maintainability, and documentation.

Keep one fix `active` by default. For each fix:

1. Revalidate that the underlying finding still exists.
2. Create or identify a failing reproduction when practical and confirm it fails for the expected reason.
3. Reassess the recommendation against all intervening changes; narrow or improve it when possible.
4. Implement the smallest root-cause fix without unrelated refactoring.
5. Run the reproduction, targeted tests, and directly affected regression checks.
6. Inspect the diff and update the run record.
7. For `P0`, `P1`, or otherwise high-risk fixes, obtain an independent analysis-only closure review. Straightforward `P2` or `P3` fixes may rely on objective validation plus the final review.
8. Mark the fix and its findings `passed`/`fixed` only after sufficient evidence. Return the fix to `active` when closure or regression fails.

Recompute the remaining fix frontier after each closure because earlier fixes may supersede or reorder later work.

## Phase 7 — Regression and final review

After all fixes required by the active completion policy close:

1. Run every feasible build, test, lint, type-check, migration, generated-file, and packaging check relevant to the repository.
2. Inspect the aggregate diff and dependency changes.
3. Confirm unrelated user changes remain untouched.
4. Map every acceptance criterion to concrete evidence.
5. Spawn a fresh analysis-only final reviewer who did not author the implementation or repairs. Use multiple reviewers when risk warrants it.
6. Route new evidence-backed findings through triage, solution analysis, ordering, and repair rather than patching them ad hoc.
7. After two complete repair cycles, reassess any remaining finding's evidence, root cause, scope, and status. Under the default no-threshold policy, continue resolving accepted in-scope findings or mark the run `blocked` when an external constraint prevents progress. Only an explicit blocking threshold allows below-threshold findings to be deferred without preventing completion.

Classify unavailable validation precisely. Record the attempted command and observed failure; do not label an implementation defect as environmental without evidence.

## Completion gate

Set the run status to `complete` only when:

- Every acceptance criterion is `passed` with evidence.
- Every implementation and required fix node is `passed` or `superseded` with rationale.
- No finding remains `investigate` or `open`.
- With the default no-threshold policy, no accepted finding remains `deferred`. With an explicit threshold, no finding at or above that threshold remains unresolved or deferred.
- Every repaired root-cause cluster has targeted validation; `P0`, `P1`, and otherwise high-risk clusters also have independent closure evidence.
- Every feasible regression check was attempted; no introduced failure remains; demonstrated pre-existing or environmental failures are recorded.
- The final independent review finds no unresolved defect required by the active completion policy.
- Every finding has a final disposition, and rejected, duplicate, superseded, or deferred findings have explicit rationales.
- Residual risks, assumptions, and unavailable validations are recorded.

If work is blocked, set the run status to `blocked` and report the exact blocker, evidence, completed nodes, and safest next decision.

## Final response

Report what was implemented, material plan deviations, review coverage and finding disposition, root-cause fixes and order, exact validation outcomes, acceptance-criteria evidence, residual risks or blockers, and the run-record path.

## Subagent fallback

When subagents are unavailable, perform the same reviews as separate analysis-only passes in the main thread. Keep discovery, solution selection, implementation, and closure logically independent; do not skip triage or root-cause clustering.
