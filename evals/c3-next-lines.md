# C3 — Single `Next: /os-apply` line after the merge

Covers: `os-review` ending a mid-implementation adjustment round with
`Next: /os-apply <name>` (never `/os-apply-tdd`, regardless of the change's
mode); `os-verify` ending a `BLOCK` verdict with `Next: /os-apply <name>`
(never a mode-conditional line).

`OS_SDD` below is the absolute path of this repository.

## Setup — tdd change mid-implementation, one task already done

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes/mid-tdd/specs/greeting
cat > openspec/changes/mid-tdd/proposal.md <<'MD'
## Why

Say hello, tdd mode, mid-implementation.

## Implementation

Implementation: tdd
MD
cat > openspec/changes/mid-tdd/design.md <<'MD'
## Decisions

A plain function.

## Seams

| Seam | Scenarios |
|---|---|
| `greet.py` `greet()` | greeting/Hello returns greeting |
MD
cat > openspec/changes/mid-tdd/specs/greeting/spec.md <<'MD'
## ADDED Requirements

### Requirement: Hello returns greeting
The project SHALL expose a `greet()` function returning `hello`.

#### Scenario: Hello returns greeting
- **WHEN** `greet()` is called
- **THEN** it returns `hello`
MD
cat > openspec/changes/mid-tdd/tasks.md <<'MD'
## 1. Greeting

- [x] 1.1 Implement `greet()` in `greet.py` — covers: greeting/Hello returns greeting
- [ ] 1.2 Add a `greet_loudly()` variant — covers: none (adjustment target)
MD
git add -A && git commit -q -m init
```

## Prompt — mid-implementation review round

```bash
claude -p "/os-review mid-tdd" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c3-review-mid.jsonl
```

## Setup — standard change ready to verify, forced BLOCK

Same shape as `b9`'s standard setup, but with `tasks.md` already fully
checked and a `VERIFY.md`-worthy defect deliberately left in place (e.g. the
required file missing its content) so `os-verify` returns `Verdict: BLOCK`.

## Prompt — verify BLOCK

```bash
claude -p "/os-verify block-standard" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > c3-verify-block.jsonl
```

## Pass criteria

- `c3-review-mid.jsonl`: ends with `Next: /os-apply mid-tdd` — no
  `/os-apply-tdd` anywhere in the transcript.
- `c3-verify-block.jsonl`: ends with `Next: /os-apply block-standard` — no
  mode-conditional `Next:` line.
- `grep -c "os-apply-tdd" c3-*.jsonl` is `0` for both files.

## Last run

2026-09-17 — **NOT EXECUTED**, for the same reason recorded in
`c1-apply-mode-loading.md` and `c2-apply-evidence.md`: a direct
`claude -p "say ok"` probe returned `api_error_status: 429` (session limit,
resets 1:40pm America/Havana) before this case's setup was attempted.
Static verification stands in for it: `grep -rn "os-apply-tdd" skills
shared hooks scripts` returns no results, and both `skills/os-review/
SKILL.md` step 9 and `skills/os-verify/SKILL.md` step 7 were rewritten to
emit only `Next: /os-apply <name>`, unconditional on mode — but whether the
live model actually produces that exact line at the end of a real
interview/verify run is **unverified**.
