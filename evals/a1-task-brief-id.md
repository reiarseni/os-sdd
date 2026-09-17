# A1 — `os-apply` passes the task id to `task_brief.py`

The first unchecked task is `2.1`, which is the 3rd checkbox: passing its
position (`3`) or a guessed number instead of the id fails the case.

## Setup

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
## 1. Setup

- [x] 1.1 Create the change — covers: none (scaffolding)
- [x] 1.2 Write the spec — covers: none (docs)

## 2. Greeting

- [ ] 2.1 Create `hello.txt` containing `hello` — covers: greeting/Hello file
MD
```

## Prompt

```bash
claude -p "/os-apply greeting" --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Bash" > a1.jsonl
```

## Pass criterion

```bash
grep -oE 'task_brief\.py\\?"? greeting [0-9.]+' a1.jsonl | sort -u
```

Passes if every line printed ends in `greeting 2.1` and at least one line is
printed.

## Last run

2026-09-16, Claude Code 2.1.273 — **PASS**. The criterion printed one line,
`task_brief.py greeting 2.1`; the session also created `hello.txt` and
marked `2.1`.
