# Skills

Reusable Codex skills for focused commits and structured implementation reviews.

## Available skills

- [Commit Session Changes](commit-session-changes/SKILL.md): stage and commit only
  changes made during the current task, preserving unrelated work. The commit
  message describes the staged changes and can draw on surrounding repository
  context.
- [Implementation Review Graph](implementation-review-graph/README.md): implement
  a plan, review it through independent analysis, triage findings, repair issues
  in dependency order, and verify the result. Includes reviewer prompts and a
  resumable run-record template.

## Install

Clone this repository:

```bash
git clone https://github.com/RumiFlow/skills.git
```

Copy each skill's complete directory into `.agents/skills/` in your project, or
into `~/.agents/skills/` for your user. Keep the `agents/`, `assets/`, and
`references/` subdirectories with their skill where present.

See the [Implementation Review Graph guide](implementation-review-graph/README.md)
for installation and workflow details.

## Use

```text
$commit-session-changes
```

```text
$implementation-review-graph Implement docs/plan.md.
```

Commit Session Changes creates a local commit. Implementation Review Graph uses
explicit invocation and records progress in `.agent-runs/<run-id>/RUN.md`.
