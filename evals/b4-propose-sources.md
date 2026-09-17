# B4 — `os-propose`/`os-propose-grill`: existing change/spec detection

Covers: an active change with the same name/overlap and no tasks done offers
to continue instead of recreating; one with some tasks done points at
`/os-review` instead of proposing; a spec that already covers the requested
behavior stops the proposal; a project with no `root` stops instead of
guessing; the project's `context`/`rules` are respected without being
copied into the artifacts verbatim; an exploration's facts/sources seed the
first round instead of being re-researched; a proposal from a map stretch
links back with `Map:`.

`OS_SDD` below is the absolute path of this repository.

## Setup — active change, no tasks done

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/changes/add-color-tags/specs/notes
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
MD
cat > openspec/changes/add-color-tags/specs/notes/spec.md <<'MD'
## ADDED Requirements

### Requirement: Note color
A note SHALL have an optional color.

#### Scenario: Set a note's color
- **WHEN** a color is assigned to a note
- **THEN** it's stored and returned on read
MD
cat > openspec/changes/add-color-tags/tasks.md <<'MD'
## 1. Storage

- [ ] 1.1 Add the color column — covers: notes/Set a note's color
MD
mkdir -p openspec/specs
git add -A && git commit -q -m init
```

## Prompt — active change, no tasks done

```bash
claude -p "/os-propose Let users tag notes with a color" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" "AskUserQuestion" > b4-notasks.jsonl
```

## Setup — active change, some tasks done (mid-implementation)

Same as above, but mark `1.1` as `[x]` before running.

## Prompt — active change, some tasks done

```bash
claude -p "/os-propose Let users tag notes with a color" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" "AskUserQuestion" > b4-sometasks.jsonl
```

## Setup — root null

```bash
EVAL2="$(mktemp -d)" && cd "$EVAL2"
"$OS_SDD/install.sh" "$EVAL2"
```
(no `git init`, no `openspec/` directory at all)

## Prompt — root null

```bash
claude -p "/os-propose Add a feature" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" > b4-noroot.jsonl
```

## Pass criterion

```bash
grep -c "openspec new change" b4-notasks.jsonl     # 0 — must ask before creating
grep -c "openspec new change" b4-sometasks.jsonl   # 0 — should redirect to /os-review, not propose
grep -c "/os-review" b4-sometasks.jsonl            # >0
grep -c "openspec init" b4-noroot.jsonl            # 0 — must stop, not init unasked
```

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL**. Ran the two change-detection
scenarios for real.

- **No tasks done** (`b4-notasks.jsonl`): the model found the overlapping
  `add-color-tags` change (0/1 tasks), summarized its current proposal, and
  asked to continue it or start fresh — matching "no tasks done → ask,
  don't recreate" exactly, with no `openspec new change` call.
- **Some tasks done** (`b4-sometasks.jsonl`, all tasks marked `[x]` so the
  change reads `isComplete: true`): the model detected the completed change,
  explicitly said "no debo proponer encima," ran no interview and wrote no
  artifacts, and closed with `Next: /os-review add-color-tags` — matching
  "some/all tasks done → redirect to `/os-review`, don't propose."

Not executed in this pass: root-null, an already-covered spec with no
change needed, project `context`/`rules` being respected without being
copied verbatim, an exploration's facts seeding round 1 without
re-researching, and a proposal from a map stretch writing `Map:` — each
needs its own setup/run on the order of the two above and was deferred for
time. Reporting the gap rather than inventing a result for them.
