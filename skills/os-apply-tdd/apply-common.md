# Apply: common steps

Contract shared by `os-apply` and `os-apply-tdd`. Each skill defines its
own evidence for a task.

## Read once

Read `openspec/changes/<name>/proposal.md`, `design.md` (including
`## Seams` if the change is `tdd`), the delta specs and `tasks.md` — once,
at the start. If `openspec/changes/<name>/HANDOFF.md` exists, read it too
and resume from the step it names instead of starting over.

If context gets compacted or cleared mid-change, don't re-read those
artifacts: resume from `tasks.md` (the first unchecked task),
`HANDOFF.md` if present, and that task's brief.

## Lightweight review

After implementing a task and before marking it — no subagents:

- Does the diff actually cover the task's `covers:` scenarios?
- Does the diff touch anything *outside* that scope? If so, flag it before
  marking the task — don't silently expand scope.
- Is the evidence your skill requires cited?
- If that evidence is failing or missing: leave the task unmarked, and
  either fix the implementation or report the failure with the real output
  — never mark `- [x]` over a red test.

Only once the evidence exists, mark the task `- [x]` in `tasks.md`.

## Close

When no tasks remain, run only the tests for files touched this session —
never the full suite while applying; that's `/os-verify`'s job. Tell the
user the change is ready for verification and end with
`Next: /os-verify <name>`.
