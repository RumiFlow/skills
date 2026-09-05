# Subagent prompts

Load this file only when delegating review, investigation, solution analysis, skeptical review, closure, or final review. Replace placeholders and provide only the necessary objective, criteria, repository rules, diff, files, and validation evidence.

## Common analysis-only contract

Append this to every subagent prompt:

```text
Do not intentionally edit source files, apply patches, commit, or change workflow
state. You may run non-destructive inspections and validation commands permitted
by repository rules. Treat concerns as hypotheses until concrete evidence supports
them. Do not report preferences as defects. Return distilled results, not raw logs.
Say "no findings" when no evidence-backed problem exists.
```

## Implementation reviewer

```text
Review the implementation for this dimension: [DIMENSION].

Objective and acceptance criteria:
[OBJECTIVE AND CRITERIA]

Relevant plan, repository rules, diff, files, and tests:
[CONTEXT]

For each finding return:
- stable title and affected acceptance criteria
- severity P0-P3 and confidence high/medium/low
- exact evidence
- observed and expected behavior
- impact and root-cause hypothesis
- reproduction or smallest decisive validation

Do not propose or implement a patch during discovery.
```

Use these focus areas when relevant:

- Requirements: omitted, partial, or contradicted acceptance criteria.
- Correctness: state transitions, boundaries, errors, retries, cancellation, concurrency, lifecycle, ownership, and partial failure.
- Tests: missing material coverage, invalid mocks, assertions that cannot fail, flakiness, false confidence, and untested failure paths.
- Architecture/compatibility: public contracts, layering, dependencies, schemas, migrations, data formats, and backwards compatibility.
- Security/privacy: trust boundaries, authorization, secrets, input handling, injection, paths, logging, transport, dependencies, and privileges.
- Performance/resources: algorithmic scale, I/O, memory, contention, caching, batching, startup, and hot paths.
- UX/accessibility: observable behavior, recovery, feedback, keyboard/screen-reader use, focus, and platform conventions.

## Finding investigator

```text
Investigate [FINDING] against the current repository state. Assign one disposition:
investigate, open, rejected, duplicate, or superseded. Reproduce the concern when
safe and practical. Return exact evidence, corrected severity/confidence, likely
root cause, related findings, and the smallest decisive validation. Do not patch it.
```

## Root-cause solution analyst

```text
Analyze root-cause cluster [CLUSTER] against the current repository state. Confirm
or revise the root cause. For a non-trivial issue, compare at least two viable
solutions across correctness, scope, compatibility, migration needs, complexity,
testability, rollout, rollback, and regression risk.

Return:
1. confirmed root cause
2. options and tradeoffs
3. selected recommendation and rationale
4. affected files, interfaces, schemas, and dependencies
5. reproduction, targeted tests, and regression plan
6. likely failure modes and rollout/rollback implications

Do not provide a patch. State explicitly when intervening changes invalidate the
original recommendation.
```

## Skeptical recommendation reviewer

```text
Challenge [RECOMMENDATION] for [CLUSTER]. Assume it may be overbroad, incomplete,
or create a new failure mode. Check whether it addresses the root cause, preserves
contracts, handles migration/rollback, and has sufficient validation. Compare it
with the strongest alternative. Return approve, revise, or reject with evidence.
```

## Fix closure reviewer

```text
Independently review [FIX] for [FINDINGS]. Compare the original evidence, selected
recommendation, actual diff, and validation results.

Answer:
1. Does the original defect still reproduce?
2. Is the root cause resolved rather than masked?
3. Does validation exercise the original failure path and relevant regressions?
4. Did the fix violate an acceptance criterion or public contract?
5. Is the diff broader than necessary?
6. Should the fix be passed, returned to active, or marked blocked?
```

## Final reviewer

```text
Perform a fresh analysis-only review of the final implementation against the
objective, acceptance criteria, plan, repository rules, aggregate diff, and
verification evidence. Look for unresolved findings, interactions between fixes,
new regressions, compatibility failures, missing failure paths, and unnecessary
complexity introduced during repair. Do not repeat a closed finding unless its
closure evidence is invalid. Return findings in severity order (`P0` through
`P3`), identify which remain required by the active completion policy, then give
a criterion-by-criterion passed/blocked verdict.
```
