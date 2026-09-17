---
name: os-verify
description: Use when a change's tasks are all done and it needs verifying that the implementation actually satisfies its specs before archiving — cheap checks first, then a two-stage subagent review, then VERIFY.md with PASS or BLOCK.
disable-model-invocation: true
argument-hint: "[change]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - next-step.md
  shared-scripts:
    - fingerprint.py
---

# os-verify

Verifies the **implementation** against the change's specs — the gate
before archiving. Fixed order, cheapest checks first.

Before step 1, read `select-change.md`, `implementation-mode.md` and
`next-step.md`.

## 1. Select the change

Apply `select-change.md`, and determine the mode with
`implementation-mode.md`.

## 2. Fresh PASS already exists?

If `openspec/changes/<name>/VERIFY.md` says `Verdict: PASS` and
the output of `python3 "${CLAUDE_SKILL_DIR}/scripts/fingerprint.py"`, run
from the project root, matches its `Fingerprint:` line, **skip straight to
step 6** — don't re-run checks or subagents.

## 3. Cheap checks first

Run the full test suite, lint and typecheck (whichever exist in this repo).
If the previous `VERIFY.md` has a `Commands:` line, reuse those commands
verbatim; only redetect (check `package.json`, `pyproject.toml`,
`Makefile`, …) if the line is missing or a command fails with "command not
found".

If **any** of these fail: verdict is `BLOCK`. Write `VERIFY.md` (step 5)
citing the failing command and its real output, then go straight to step 7
— do not launch any subagent.

## 4. Two-stage subagent review

Only if step 3 passed. From the project root, compute the diff base and
the diff into a temp file:

```bash
DEFAULT="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)"
[ -z "$DEFAULT" ] && git rev-parse --verify -q main >/dev/null && DEFAULT=main
[ -z "$DEFAULT" ] && git rev-parse --verify -q master >/dev/null && DEFAULT=master
BASE=""
if [ -n "$DEFAULT" ] && [ "$(git symbolic-ref --short -q HEAD)" != "${DEFAULT#origin/}" ]; then
  BASE="$(git merge-base HEAD "$DEFAULT")"
fi
[ -z "$BASE" ] && BASE=HEAD
PKG="$(mktemp)"
echo "BASE=$BASE PKG=$PKG"
git diff "$BASE" > "$PKG"
git ls-files -o --exclude-standard | while read -r f; do git diff --no-index /dev/null "$f" >> "$PKG"; done
{ git diff --name-only "$BASE"; git ls-files -o --exclude-standard; } | sort -u
```

Run it as one command: shell variables don't survive between commands, so
use the printed `PKG=` path from here on. If it printed `BASE=HEAD` (you're
on the default branch, or none was found), tell the user the diff only
includes uncommitted changes and new files. The last lines are the touched
files.

Append to that file the delta specs' scenarios, every task's `— covers:`,
the seams table (if `tdd`) and the touched-files list. Both subagents'
prompts are in `REVIEW-LENSES.md`; give each the file's path.

1. **Fidelity subagent** (Agent tool): maps every scenario to its evidence.
   If it reports any blocking finding, skip the quality subagent.
2. **Quality subagent** (Agent tool with `model: "sonnet"`): repo
   conventions, simplicity and risk in the touched files.

Delete the package file once `VERIFY.md` is written.

The verdict must come from real, current output — never from a prior run or
an unverified subagent claim.

## 5. Write VERIFY.md

Compute `Fingerprint` with `python3 "${CLAUDE_SKILL_DIR}/scripts/fingerprint.py"`
from the project root. Use `VERIFY-TEMPLATE.md`: header (`Verdict`, date, `Fingerprint`,
`Commands`), cited command outputs, a scenario → evidence table, findings by
severity. Then continue with step 6 (after a `BLOCK` from step 3, step 7).

## 6. Offer to archive

Only with `Verdict: PASS` and a fingerprint that still matches: ask the user
if they want to archive, and follow `ARCHIVE.md` if they do. With `BLOCK`, don't
offer archiving — list what's missing and go to step 7.

## 7. Close

This is the only step that ends the skill. With `BLOCK`, end with
`Next: /os-apply <name>` or `Next: /os-apply-tdd <name>` per the change's
mode. After archiving, or if the user declined to archive a `PASS`, omit the
`Next:` line.
