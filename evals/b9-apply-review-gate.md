# B9 — `os-apply*`: REVIEW.md freshness gate

Covers: applying without any `REVIEW.md` warns and asks before continuing;
a `REVIEW.md` whose `Fingerprint:` no longer matches the artifacts (stale
review) is treated the same as missing; a test that doesn't fail first is
still caught by `tests.md`'s red-for-the-right-reason step; a `manual:`
scenario's evidence is the named verification's real output, not a
fabricated pass.

`OS_SDD` below is the absolute path of this repository.

## Setup — no REVIEW.md at all

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes/greeting/specs/greeting
cat > openspec/changes/greeting/proposal.md <<'MD'
## Why

Say hello.

## Implementation

Implementation: standard
MD
cat > openspec/changes/greeting/design.md <<'MD'
## Decisions

A plain text file.
MD
cat > openspec/changes/greeting/specs/greeting/spec.md <<'MD'
## ADDED Requirements

### Requirement: Hello file
The project SHALL have a `hello.txt` file.

#### Scenario: Hello file
- **WHEN** `hello.txt` is read
- **THEN** it contains `hello`
MD
cat > openspec/changes/greeting/tasks.md <<'MD'
## 1. Greeting

- [ ] 1.1 Create `hello.txt` containing `hello` (verify: cat hello.txt) — covers: greeting/Hello file
MD
git add -A && git commit -q -m init
```

## Prompt — no REVIEW.md

```bash
claude -p "/os-apply greeting" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > b9-noreview.jsonl
```

## Setup — stale REVIEW.md (fingerprint mismatch)

Same as above, plus:

```bash
python3 "$OS_SDD/scripts/fingerprint.py" --artifacts greeting  # capture as OLD_FP
cat > openspec/changes/greeting/REVIEW.md <<MD
Verdict: READY
Fingerprint: 0000000000000000000000000000000000000000000000000000000000000000
Date: 2026-09-01
MD
# artifacts already differ from a fake fingerprint, so this is stale by construction
git add -A && git commit -q -m "stale review"
```

## Prompt — stale REVIEW.md

```bash
claude -p "/os-apply greeting" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > b9-stale.jsonl
```

## Pass criterion

Both runs mention `/os-review` and don't silently proceed to implement
`1.1` without at least surfacing the missing/stale review first.

## Last run

2026-09-17 — **NOT EXECUTED — session rate limit**. The no-review setup was
prepared and the `claude -p "/os-apply greeting"` call was launched for
real, but it failed immediately with `api_error_status: 429`,
`"result": "You've hit your session limit · resets 1:40pm (America/Havana)"`
— confirmed with a second trivial `claude -p "say ok"` call that failed the
same way. All further `claude -p` eval subprocesses became unavailable for
the rest of this session at that point. The "Review gate" section added to
`shared/apply-common.md` (task 11.1) and its wiring into `os-apply`/
`os-apply-tdd` step 2 pass `tests/lint_skills.py` and don't touch any
existing test file, so nothing here is known-broken — but the actual model
behavior (whether it warns correctly, whether it computes and compares the
fingerprint correctly, whether it asks before proceeding) is **unverified**
by a live run. Reporting the rate limit as the reason rather than
fabricating a transcript.
