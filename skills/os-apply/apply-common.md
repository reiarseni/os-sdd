# Apply: common steps

Contract for `os-apply`. Each mode file defines its own evidence for a
task.

## Review gate

Before reading the artifacts, check `openspec/changes/<name>/REVIEW.md`:

- Missing entirely, or `Verdict: BLOCK`: warn the user and recommend
  `/os-review <name>`. Continue only if the user explicitly confirms
  applying without a fresh `READY`.
- `Verdict: READY`: compare its `Fingerprint:` line against the change's
  current artifacts fingerprint (each skill's step 1 says how to compute
  it). A mismatch means the artifacts changed since the review — treat it
  the same as missing/`BLOCK` (warn, recommend `/os-review <name>`, confirm
  before continuing). A match means the review is fresh: proceed without
  asking.

## Read once

Read `openspec/changes/<name>/proposal.md`, `design.md` (including
`## Seams` if the change is `tdd`), the delta specs and `tasks.md` — once,
at the start. If `openspec/changes/<name>/HANDOFF.md` exists, read it too
and resume from the step it names instead of starting over.

If context gets compacted or cleared mid-change, don't re-read those
artifacts: resume from `tasks.md` (the first unchecked task),
`HANDOFF.md` if present, that task's brief, and `modes/<mode>.md` — the
red→green rules in `tdd` mode don't survive compaction otherwise.

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
