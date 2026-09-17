# B10 — `os-verify`: evidence package and fidelity subagent

Covers: a scenario with no evidence in the package is reported MISSING
(blocking), not inferred as covered; a test cited in `covers:`/seams but
outside the diff (already existed) is still visible to the fidelity
subagent because the package includes its full content, not just diff
hunks.

`OS_SDD` below is the absolute path of this repository.

## Functional check (not a model eval): `diff_base.py`'s shell invocation

Verified for real that the exact command block in `os-verify/SKILL.md` step
4 works:

```bash
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q -b main && git commit -q --allow-empty -m init
mkdir -p openspec/changes/foo && cat > openspec/changes/foo/.openspec.yaml <<'Y'
schema: spec-driven
Y
git add -A && git commit -q -m "add change"
git checkout -q -b feature
echo x > x.txt && git add x.txt && git commit -q -m "work"
CLAUDE_SKILL_DIR=/path/to/os-sdd/skills/os-verify
BASE="$(python3 "$CLAUDE_SKILL_DIR/scripts/diff_base.py" foo 2>&1 >/tmp/diff_base_out)"
BASE="$(grep -o 'BASE=.*' /tmp/diff_base_out | cut -d= -f2)"
echo "BASE=$BASE"
```

Result: `BASE` resolved to the commit that added `.openspec.yaml` ("add
change"), exactly per `diff_base.py`'s own tested behavior
(`tests/test_diff_base.py`, section 3) — the SKILL.md's shell plumbing
around it (the two-step `BASE=` extraction via a temp file, since a
subshell's stderr/stdout can't both be captured inline in one assignment)
works as written, not just in isolation.

## Setup — scenario with no evidence

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/changes/greeting/specs/greeting
cat > openspec/changes/greeting/proposal.md <<'MD'
## Implementation

Implementation: standard
MD
cat > openspec/changes/greeting/specs/greeting/spec.md <<'MD'
## ADDED Requirements

### Requirement: Hello file
#### Scenario: Hello file
- **WHEN** hello.txt is read
- **THEN** it contains hello

#### Scenario: Goodbye file
- **WHEN** goodbye.txt is read
- **THEN** it contains goodbye
MD
cat > openspec/changes/greeting/tasks.md <<'MD'
- [x] 1.1 Create hello.txt (verify: cat hello.txt) — covers: greeting/Hello file, greeting/Goodbye file
MD
echo hello > hello.txt
git add -A && git commit -q -m "implement hello only, claim goodbye too"
```

## Prompt

```bash
claude -p "/os-verify greeting" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" "Agent" > b10.jsonl
```

## Pass criterion

`VERIFY.md`'s scenario → evidence table marks `Goodbye file` MISSING and the
overall verdict is `BLOCK`, since no `goodbye.txt` was ever created despite
the task claiming to cover it.

## Last run

2026-09-17 — **NOT EXECUTED (model eval) — session rate limit**. The
functional check above for `diff_base.py`'s shell invocation was run for
real and passed. The full model eval (launching `/os-verify` against a
change that over-claims coverage, and inspecting whether the fidelity
subagent correctly reports `Goodbye file` as MISSING rather than assuming
it's covered because `hello.txt` exists) requires a `claude -p` call, which
hit the same session-wide rate limit reported in `b9-apply-review-gate.md`
("You've hit your session limit · resets 1:40pm (America/Havana)") right
before this task was reached. Reporting the gap rather than fabricating a
subagent transcript.
