---
name: os-amend-spec
description: Use when an existing change needs to change direction mid-flight — a new requirement, a design decision reversed, or scope adjusted — while preserving the tasks already done.
disable-model-invocation: true
argument-hint: "[change] [what changes]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - proposal-templates.md
    - next-step.md
---

# os-amend-spec

Updates a change's artifacts to reflect a change of direction, without
throwing away completed work.

Before step 1, read `select-change.md`, `proposal-templates.md` and
`next-step.md`.

## 1. Select the change

Apply `select-change.md`.

## 2. Understand the amendment

First read the current `openspec/changes/<name>/proposal.md`, `design.md`,
delta specs and `tasks.md`, so you amend the real current state. Then ask
the user (plain questions or AskUserQuestion) what's changing: a new
requirement, a reversed decision, a scope cut.

## 3. Update every affected artifact

- `proposal.md` / `design.md`: update the sections the amendment touches.
  Record the new decision in `design.md` in the same format as the existing
  ones, with alternatives if relevant. If the change is `tdd`
  (`implementation-mode.md`), keep `## Seams` in the format of "Seams (tdd
  only)" in `proposal-templates.md`.
- Delta specs: add, modify or remove requirements/scenarios to match.
- `tasks.md`:
  - **MUST NOT** unmark any task already `- [x]` that the amendment doesn't
    affect.
  - Tasks affected by the amendment: reopen them (`- [ ]`) and update their
    `— covers:` suffix.
  - New requirements: add tasks in the format of "Task → scenario link" in
    `proposal-templates.md`.

Don't touch `VERIFY.md`: editing code or artifacts already changes the
content fingerprint, so the next `/os-verify` re-verifies.

## 4. Close

Run `openspec validate --change <name>` and fix what it flags. If new or
reopened tasks exist, end with `Next: /os-apply <name>` or
`Next: /os-apply-tdd <name>` per the change's mode; if nothing needs
implementing, end with `Next: /os-review-spec <name>`.
