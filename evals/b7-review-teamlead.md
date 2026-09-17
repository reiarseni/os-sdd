# B7 — `os-review`: `TEAMLEAD.md` round trip

Covers: a team-lead summary gets generated with plain-language decisions and
`openspec show --diff` implications; team-lead feedback pasted into
`## Team-lead feedback` gets turned into proposals and moved to
`## Processed feedback (<date>)`.

`OS_SDD` below is the absolute path of this repository.

## Setup — feedback already present

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/changes/add-color-tags/specs/notes openspec/specs
# ... same proposal.md/design.md/specs/tasks.md as b6-review-adjustments.md,
# all scenarios covered this time ...
cat > openspec/changes/add-color-tags/TEAMLEAD.md <<'MD'
# Team-lead summary: add-color-tags

## Team-lead feedback

- We should support custom hex colors too, not just presets — product asked
  for this in the last planning meeting.
MD
git add -A && git commit -q -m init
```

## Prompt

```bash
claude -p "/os-review add-color-tags" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Edit" "Bash" "AskUserQuestion" > b7.jsonl
```

## Pass criterion

The feedback about custom hex colors becomes a finding (not silently
ignored), and, once resolved, `TEAMLEAD.md` gets a
`## Processed feedback (<date>)` section while `## Team-lead feedback`
either empties or is replaced.

## Last run

2026-09-17, Claude Code 2.1.274 — **NOT EXECUTED**. `os-review`'s step 3
("if `TEAMLEAD.md` exists and has an unprocessed `## Team-lead feedback`
section, read it too") and step 7 ("Team-lead round trip") were written to
satisfy this scenario, and step 8's "always write `REVIEW.md`" plus step
7's `TEAMLEAD.md` regeneration are structurally consistent per
`tests/lint_skills.py` (no broken section references, no duplicated rules
between `SKILL.md` and `TEAMLEAD-TEMPLATE.md`). A live run needs the same
multi-turn `-c -p` scripting `b6-review-adjustments.md` flagged as
unexecuted for its post-selection steps, plus a real `git` history for
`openspec show --diff` to have something to report — deferred for time.
Reporting this as unexecuted rather than inventing a transcript.
