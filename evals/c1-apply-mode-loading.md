# C1 — `os-apply`: mode file loading and mode handling

Covers: `os-apply` on a `tdd` change (reads only `modes/tdd.md`, announces
`Mode: tdd (from proposal.md)`); `os-apply` on a `standard` change (reads
only `modes/standard.md`, announces `Mode: standard (from proposal.md)`); a
change with no `Implementation:` line (asks which mode instead of assuming);
a request to force the other mode (explains the mode comes from
`proposal.md`/`os-review`, doesn't switch silently); resuming after
compaction/`/clear` (re-reads the mode file, not the other artifacts);
starting from a `HANDOFF.md` handoff; the skill installed and invoked from a
different project (portable `${CLAUDE_SKILL_DIR}` paths).

`OS_SDD` below is the absolute path of this repository.

## Setup — tdd change

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes/greet-tdd/specs/greeting
cat > openspec/changes/greet-tdd/proposal.md <<'MD'
## Why

Say hello, tdd mode.

## Implementation

Implementation: tdd
MD
cat > openspec/changes/greet-tdd/design.md <<'MD'
## Decisions

A plain function.

## Seams

| Seam | Scenarios |
|---|---|
| `greet.py` `greet()` | greeting/Hello returns greeting |
MD
cat > openspec/changes/greet-tdd/specs/greeting/spec.md <<'MD'
## ADDED Requirements

### Requirement: Hello returns greeting
The project SHALL expose a `greet()` function returning `hello`.

#### Scenario: Hello returns greeting
- **WHEN** `greet()` is called
- **THEN** it returns `hello`
MD
cat > openspec/changes/greet-tdd/tasks.md <<'MD'
## 1. Greeting

- [ ] 1.1 Implement `greet()` in `greet.py` — covers: greeting/Hello returns greeting
MD
python3 "$OS_SDD/scripts/fingerprint.py" --artifacts greet-tdd
# paste the printed fingerprint into REVIEW.md below
cat > openspec/changes/greet-tdd/REVIEW.md <<MD
Verdict: READY
Fingerprint: <FINGERPRINT>
Date: 2026-09-17
MD
git add -A && git commit -q -m init
```

## Prompt — tdd change

```bash
claude -p "/os-apply greet-tdd" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c1-tdd.jsonl
```

## Setup — standard change

Same shape, `Implementation: standard`, no `## Seams`, task
`Create hello.txt containing hello`, fresh `REVIEW.md`.

## Prompt — standard change

```bash
claude -p "/os-apply greet-standard" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c1-standard.jsonl
```

## Setup — no `Implementation:` line

Same as the standard change, but `proposal.md` has no `## Implementation`
section at all.

## Prompt — no mode line

```bash
claude -p "/os-apply greet-nomode" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c1-nomode.jsonl
```

## Pass criteria

- `c1-tdd.jsonl`: a `Read` tool call for `modes/tdd.md`, none for
  `modes/standard.md`; the text output contains `Mode: tdd`.
- `c1-standard.jsonl`: a `Read` tool call for `modes/standard.md`, none for
  `modes/tdd.md`; the text output contains `Mode: standard`.
- `c1-nomode.jsonl`: the model asks which mode the change is (via
  `AskUserQuestion` or, per the headless fallback, plain text) instead of
  silently assuming `standard`.

## Last run

2026-09-17 — **NOT EXECUTED — nested `claude -p` nested-session evals were
not run this pass** (this session is itself running in a usage-limited,
lower-priority continuation; launching further metered `claude -p`
subprocesses to drive the eval was judged out of scope for this turn). The
mode-loading behavior it targets — `os-apply` step 1 announcing
`Mode: <mode> (from proposal.md)` and reading only `modes/<mode>.md`,
`implementation-mode.md` asking via `AskUserQuestion` when the line is
missing, `apply-common.md`'s "Read once" re-reading the mode file after
compaction — is implemented and passes `python3 tests/lint_skills.py`
(which checks both mode files exist and neither is named in "Before
step 1") and the full `python3 -m unittest discover tests` suite, but the
actual live-model behavior described above is **unverified** by a real run.
