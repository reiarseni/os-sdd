# B6 — `os-review`: findings, proposals and verdict

Covers: a scenario with no covering task is a blocking finding; a `tdd`
change with no `## Seams` is blocking; partially-selected proposed fixes
still get applied selectively; the user can ask for an unrelated change
mid-review; refuses to run once all tasks are done; mid-implementation
adjustments reopen only affected tasks; a rejected blocking finding lands in
Open Questions and forces `BLOCK`.

`OS_SDD` below is the absolute path of this repository. Headless `claude -p`
runs end the turn as soon as the model asks its findings (no
`AskUserQuestion` tool in `-p` mode — see `b1-session-options.md`), so a
single-turn run can verify the findings themselves and their format, but not
the state after the user picks fixes; that needs a scripted `-c -p` reply.

## Setup — scenario with no covering task

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/changes/add-color-tags/specs/notes openspec/specs
cat > openspec/changes/add-color-tags/proposal.md <<'MD'
## Why

Users want to organize notes visually.

## What Changes

- Add a color field to notes.

## Implementation

Implementation: standard
MD
cat > openspec/changes/add-color-tags/design.md <<'MD'
## Decisions

Store color as a string enum on the note record.

## Open Questions

- none
MD
cat > openspec/changes/add-color-tags/specs/notes/spec.md <<'MD'
## ADDED Requirements

### Requirement: Note color
A note SHALL have an optional color.

#### Scenario: Set a note's color
- **WHEN** a color is assigned to a note
- **THEN** it's stored and returned on read

#### Scenario: Filter notes by color
- **WHEN** the notes list is filtered by a color
- **THEN** only notes with that color are returned
MD
cat > openspec/changes/add-color-tags/tasks.md <<'MD'
## 1. Storage

- [ ] 1.1 Add the color column — covers: notes/Set a note's color
MD
git add -A && git commit -q -m init
```

## Prompt

```bash
claude -p "/os-review add-color-tags" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Edit" "Bash" "AskUserQuestion" > b6-uncovered.jsonl
```

## Pass criterion

Look for a **Bloqueante**/Blocking finding naming `Filter notes by color` as
uncovered, in before/after form, plus a second blocking finding for task
1.1's missing verification.

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL, core finding confirmed**. Ran
the uncovered-scenario setup for real (`b6-uncovered.jsonl`). The model:
correctly identified 0/1 tasks done and proceeded (not a "todo hecho"
refusal); explicitly reasoned about and skipped the web-research question
("es un cambio pequeño e interno... no se beneficiaría"); reported
`AskUserQuestion` unavailable and fell back to text; and raised exactly the
two expected blocking findings — the uncovered `Filter notes by color`
scenario, and task 1.1 missing a stated verification — each with a
before/after edit, plus two risk findings about `design.md` not deciding
how filtering works. This confirms "scenario without a task" and "task
without declared verification" as blocking findings, before/after format,
and reasoned (not blanket) web-research skipping.

Also ran a second, cheap setup (a change with a single task already `[x]`)
against `/os-review done-change`: the model refused outright — "Per the
skill's scope check, `/os-review` refuses to run once every task is done" —
wrote no `REVIEW.md`, and pointed at `/os-verify done-change` instead.
Confirms the all-tasks-done refusal.

`REVIEW.md` was **not written** in the uncovered-scenario run because the
turn ended waiting
for the user's selection (headless `-p` has no way to answer
`AskUserQuestion`) — the "always write REVIEW.md" step, the `Verdict`
computation, `fingerprint.py --artifacts` being called, the `tdd`/no-seams
case, partial-selection application, the "change anything else?" loop, the
all-tasks-done refusal, mid-implementation task-reopening, and a rejected
blocking finding landing in Open Questions were **not exercised** — each
needs a scripted multi-turn `-c -p` conversation, deferred for time. This is
reported as a real gap, not folded into a claimed pass.
