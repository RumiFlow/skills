---
name: commit-session-changes
description: Stage and commit only Git changes attributable to the current Codex task. Use when the user asks to commit this session's work without including pre-existing or unrelated working-tree changes; create the commit message from the staged diff. Do not use when the user wants every current change committed regardless of origin.
---

# Commit Session Changes

Create one local Git commit containing exactly the changes made for the current
task, even when the working tree also contains unrelated user work.

## Authorization and scope

- Treat an explicit invocation, or a direct request matching this skill, as
  authorization to stage the current task's changes and create one local
  commit. It does not authorize pushing, amending, rebasing, stashing,
  discarding, or deleting other work.
- "Current task" means the active Codex conversation and its tool actions, not
  changes inferred from timestamps or everything presently shown by Git.
- Include additions, modifications, and deletions made by the current task,
  including focused tests, formatting changes, and generated files that the
  task intentionally produced.

## Establish provenance before staging

1. Confirm the working directory is inside a Git repository.
2. Inspect `git status --short`, the full staged diff, the full unstaged diff,
   and untracked files before changing the index.
3. Build a session-change manifest from the conversation and tool history. For
   every intended file, record the exact attributable hunks or that the entire
   new file was created by this task. Do not treat the current Git diff alone
   as evidence that a change belongs to the task.
4. Classify any already-staged hunk the same way. If the index contains a hunk
   that is not attributable to the current task, stop without changing the
   index or committing. Report the staged paths that prevent safe isolation.
5. If ownership of any intended hunk is ambiguous, stop before staging and
   identify the ambiguity. Never guess that nearby edits belong to the task.

An untracked file that existed before the task has no Git baseline. Stage it
only when the task history proves the entire file belongs to this task;
otherwise treat it as ambiguous.

## Stage only the manifest

- For a tracked file containing both task and non-task edits, stage only the
  attributable hunks. Use a minimal patch applied to the index or interactive
  patch staging with hunk splitting/editing when needed.
- Stage a whole path only when the manifest proves that the entire path's diff
  belongs to the task, such as a file created wholly by the task.
- Include both sides of a task-authored replacement and any task-authored
  deletion needed for the resulting code to be correct.
- Never use broad staging commands such as `git add .`, `git add -A`, or
  `git add -u`. Do not path-stage a tracked file with mixed ownership.
- Pass `--` before path arguments. Do not modify the working-tree content while
  staging.

After staging, inspect all of the following:

```bash
git diff --cached --check
git diff --cached --name-status
git diff --cached --stat
git diff --cached
git status --short
```

If `git diff --cached --check` reports an error, stop without committing.
Compare every staged hunk with the session-change manifest. Confirm unrelated
working-tree changes remain unstaged. If the cached diff contains an unintended
hunk, remove only that hunk from the index and re-check; never discard it from
the working tree. If exact correction is unsafe, stop without committing.

If the verified cached diff is empty, stop without creating an empty commit.

## Create the message and commit

1. Read the verified staged diff and, when useful, the staged versions of its
   files. Treat the staged snapshot as the authoritative source for what the
   commit contains.
2. Read other repository files when they help explain the staged change. Useful
   context can include neighboring implementations, callers, tests,
   documentation, configuration, and recent commit history. This inspection is
   read-only: do not stage a context file unless it is already part of the
   session-change manifest, and do not describe an unstaged change as committed.
3. Write a concise imperative subject that accurately describes the staged
   outcome, informed by the surrounding context and the repository's
   terminology and recent commit style. Keep the subject at most 72 characters.
   Add a short body only when it explains an important reason or groups distinct
   staged changes.
4. Commit exactly the verified index with that message.

Do not use `--amend`, `--no-verify`, or a force option. If a hook or Git command
fails, preserve the work and report the failure rather than bypassing it.

## Verify and report

After a successful commit:

- Report the commit SHA and subject.
- Inspect the committed diff and final `git status --short`.
- Confirm the commit contains only the manifest and call out that unrelated
  unstaged changes remain, when applicable.
- Do not push the commit.
