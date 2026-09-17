---
name: os-apply-tdd
description: Use when a tdd-mode change's artifacts are approved and its tasks need implementing as red→green vertical slices in the declared seams. For standard-mode changes use os-apply instead.
disable-model-invocation: true
argument-hint: "[change]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - apply-common.md
    - proposal-templates.md
    - next-step.md
  shared-scripts:
    - task_brief.py
---

# os-apply-tdd

Implements a `tdd`-mode change's tasks as vertical slices — one scenario at
a time, red for the right reason, then the minimum code to go green — in the
seams `design.md` declares.

Before step 1, read `select-change.md`, `implementation-mode.md`,
`apply-common.md`, `tests.md` and `next-step.md`.

## 1. Select the change and check mode

Apply `select-change.md`, then `implementation-mode.md`; this skill is for
`tdd` changes.

## 2. Read once

See "Read once" in `apply-common.md`.

## 3. Per task

For each unchecked task, in order:

1. Get its brief, running from the project root:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/task_brief.py" <change> <id>`, where
   `<id>` is the task's id exactly as written in `tasks.md` (e.g. `2.1`). The
   brief has the task's scenarios and the seam each one is tested through.
2. For each scenario, follow `tests.md`: "One scenario, one slice", or
   "Manual scenarios" if its seam is `manual:`. If the brief says the seam is
   not declared, see "Undeclared seams" in `tests.md`.
3. **Evidence**: the red→green transcript (or the manual verification's
   result) for every scenario of the task.
4. See "Lightweight review" in `apply-common.md`, then mark the task.

## 4. Close

See "Close" in `apply-common.md`.
