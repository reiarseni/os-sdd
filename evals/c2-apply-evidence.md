# C2 — `os-apply`: evidence per mode

Covers, across a `standard` and a `tdd` change: a test that fails for the
task's affected files; a task with no applicable tests (markdown/config
only); a diff that reaches outside the task's `covers:` scope; a test that
passes immediately instead of failing first; a `manual:` scenario; closing
once every task is done.

`OS_SDD` below is the absolute path of this repository.

## Setup — standard change, mixed tasks

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes/notes-standard/specs/notes
cat > openspec/changes/notes-standard/proposal.md <<'MD'
## Why

A notes file and its README line.

## Implementation

Implementation: standard
MD
cat > openspec/changes/notes-standard/design.md <<'MD'
## Decisions

Two independent artifacts: a data file and a doc line.
MD
cat > openspec/changes/notes-standard/specs/notes/spec.md <<'MD'
## ADDED Requirements

### Requirement: Notes file exists
The project SHALL have a `notes.txt` file containing `hello`.

#### Scenario: Notes file exists
- **WHEN** `notes.txt` is read
- **THEN** it contains `hello`
MD
cat > openspec/changes/notes-standard/tasks.md <<'MD'
## 1. Notes

- [ ] 1.1 Create `notes.txt` containing `hello` — covers: notes/Notes file exists
- [ ] 1.2 Document `notes.txt` in `NOTES.md` (prose only, no runtime behavior) — covers: none (documentation)
MD
python3 "$OS_SDD/scripts/fingerprint.py" --artifacts notes-standard
cat > openspec/changes/notes-standard/REVIEW.md <<MD
Verdict: READY
Fingerprint: <FINGERPRINT>
Date: 2026-09-17
MD
git add -A && git commit -q -m init
```

## Prompt — standard change

```bash
claude -p "/os-apply notes-standard" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c2-standard.jsonl
```

## Setup — tdd change with a manual scenario

Same shape as `c1`'s tdd setup, plus a second scenario in `## Seams` marked
`manual: <verification>` (e.g. a scenario that requires eyeballing rendered
output) alongside the automatable one.

## Prompt — tdd change

```bash
claude -p "/os-apply notes-tdd" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c2-tdd.jsonl
```

## Pass criteria

- `1.1` (standard): evidence cites a real test run (command, exit code,
  tail of output) that covers `notes.txt`; no `- [x]` before that evidence
  exists.
- `1.2` (standard): evidence is `no tests: <reason>` plus an alternative
  check (e.g. `cat NOTES.md`), not a fabricated test run.
- tdd automatable scenario: a visible red run (failing for the right
  reason) before the passing one — never a single green run with no red
  first.
- tdd manual scenario: evidence is the named verification's actual output,
  not a skipped or fabricated check.
- Neither run's diff touches files outside its task's declared scope; if the
  model notices an urge to do so, it flags it before marking the task.
- Once both tasks are done, the close message recommends `/os-verify
  <name>` and doesn't re-run the full suite.

## Last run

2026-09-17 — **NOT EXECUTED**. Before writing this case, a live check of
whether nested `claude -p` calls are even possible this session was run
directly (`claude -p "say ok" --output-format stream-json --verbose`): it
returned `api_error_status: 429`, `"result": "You've hit your session
limit · resets 1:40pm (America/Havana)"` — the same limit this outer
session is itself running under at reduced priority. Since a single trivial
call already fails, the multi-turn `/os-apply` runs this case needs were not
attempted. The evidence rules this eval targets — mode-specific "Implement
and evidence" in `modes/standard.md` / `modes/tdd.md`, "Lightweight review"
and "Close" in `apply-common.md` — are unchanged in substance from the
previous two-skill version (already covered live by `b9-apply-review-gate.md`,
also unexecuted for the same reason) and pass `python3 -m unittest discover
tests`, but the live-model behavior is **unverified** by a real run.
