---
name: os-apply
description: Use when a change's artifacts are approved and its tasks need implementing, in line, one task at a time with a lightweight review after each. Behavior is standard or tdd, decided by the change's own `Implementation:` line — never pass a mode explicitly.
disable-model-invocation: true
argument-hint: "[change]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - proposal-templates.md
    - next-step.md
  shared-scripts:
    - task_brief.py
    - fingerprint.py
---

# os-apply

Implements a change's tasks in line, task by task, with a lightweight review
after each and no subagents. Behavior — standard evidence, or tdd's
red→green vertical slices — depends on the mode `proposal.md` declares.

Before step 1, read `select-change.md`, `implementation-mode.md`,
`apply-common.md` and `next-step.md`.

## 1. Select the change and check mode

Apply `select-change.md`, then `implementation-mode.md`. Tell the user
`Mode: <mode> (from proposal.md)`, then read only `modes/<mode>.md` — never
both. If the user asks to apply the change in the other mode, explain that
the mode comes from `proposal.md` and only changes through `/os-review`;
don't force it.

## 2. Review gate and read once

See "Review gate" in `apply-common.md`, computing the current fingerprint
with `python3 "${CLAUDE_SKILL_DIR}/scripts/fingerprint.py" --artifacts <change>`. Then see "Read once" in `apply-common.md`.

## 3. Per task

For each unchecked task, in order:

1. Get its brief, running from the project root:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/task_brief.py" <change> <id>`, where
   `<id>` is the task's id exactly as written in `tasks.md` (e.g. `2.1`). The
   brief is the task text plus the full scenarios its `— covers:` points to;
   don't re-read the spec files.
2. See "Implement and evidence" in `modes/<mode>.md`.
3. See "Lightweight review" in `apply-common.md`, then mark the task.

## 4. Close

See "Close" in `apply-common.md`.
