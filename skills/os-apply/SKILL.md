---
name: os-apply
description: Use when a standard-mode change's artifacts are approved and its tasks need implementing, in line, one task at a time with a lightweight review after each. For tdd-mode changes use os-apply-tdd instead.
disable-model-invocation: true
argument-hint: "[change]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - apply-common.md
    - next-step.md
  shared-scripts:
    - task_brief.py
---

# os-apply

Implements a change's tasks in line, task by task, with a lightweight review
after each and no subagents.

Before step 1, read `select-change.md`, `implementation-mode.md`,
`apply-common.md` and `next-step.md`.

## 1. Select the change and check mode

Apply `select-change.md`, then `implementation-mode.md`; this skill is for
`standard` changes.

## 2. Read once

See "Read once" in `apply-common.md`.

## 3. Per task

For each unchecked task, in order:

1. Get its brief, running from the project root:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/task_brief.py" <change> <id>`, where
   `<id>` is the task's id exactly as written in `tasks.md` (e.g. `2.1`). The
   brief is the task text plus the full scenarios its `— covers:` points to;
   don't re-read the spec files.
2. Implement it.
3. **Evidence**: run the tests for the files you touched and cite the
   command, exit code and the tail of the output. If no tests apply (e.g.
   the task only touches markdown/config), write `no tests: <reason>` and
   cite one alternative check instead (lint, `openspec validate`, a grep,
   loading the file).
4. See "Lightweight review" in `apply-common.md`, then mark the task.

## 4. Close

See "Close" in `apply-common.md`.
