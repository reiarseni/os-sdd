# B1 — `session-options.md`: web research question

`os-propose` must ask, with AskUserQuestion, whether to research the web
before round 1, honor both answers, and ask the TDD question only at the
end of the interview once the checklist resolves. `os-review`'s reuse of the
same web question is re-verified once `os-review` exists (task 9.1) — see
"Last run" below for that follow-up.

`OS_SDD` below is the absolute path of this repository.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes
git add -A && git commit -q -m init
```

## Prompt (web research declined)

```bash
claude -p "/os-propose Add color tags to notes in a note-taking app, so users can assign one of a few preset colors to each note and filter by color" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" "AskUserQuestion" > b1-decline.jsonl
```

## Prompt (web research accepted, abbreviated)

```bash
claude -p "/os-propose Add color tags to notes in a note-taking app, so users can assign one of a few preset colors to each note and filter by color. If you ask about web research, say yes." \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" "AskUserQuestion" "WebSearch" > b1-accept.jsonl
```

## Pass criterion

```bash
python3 -c "
import json
for f in ('b1-decline.jsonl','b1-accept.jsonl'):
    for line in open(f):
        d = json.loads(line)
        if d.get('type') != 'assistant': continue
        for c in d['message'].get('content', []):
            if c.get('type') == 'text' and 'web' in c['text'].lower():
                print(f, '-> mentions web research')
"
```

Passes if the question about web research appears (as tool call or text)
before any scope/round-1 question, and the accept run's transcript shows a
`WebSearch` (or `WebFetch`) call while the decline run's doesn't.

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL, infra caveat found**. Ran the
decline prompt for real (`b1-decline.jsonl`, headless single-shot, after
fixing the topic to not reference a nonexistent repo file). The model
correctly asked the web-research question *before* any round-1 scope
question — order is right. But it explicitly reported `AskUserQuestion` as
unavailable ("No `AskUserQuestion` tool is available in this environment"),
searched for it via `ToolSearch`, and fell back to plain numbered text. This
looks like a real constraint of `claude -p` headless mode rather than a
skill defect: **`AskUserQuestion` is an interactive-only tool not offered
in `-p` sessions**, so this eval method (and every other `evals/b*` case
that expects an `AskUserQuestion` call) can only verify that the question is
asked in substance and in the right order — not that the literal tool fires.
Worth a note in `evals/README.md` (see task 12.1). The accept-branch run and
the `os-review` re-check (task 9.1) were not executed in this pass — left
open rather than fabricated.
