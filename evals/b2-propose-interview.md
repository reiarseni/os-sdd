# B2 — `os-propose`'s deep-style interview mechanics

Covers: artifacts aren't written before confirmation, the checklist can
close before round 10, the round-10 limit is a hard stop, no unconfirmed
assumption survives to the pre-summary, AskUserQuestion recommendations are
marked, and rounds follow the scope → decisions → edge-cases theme order.

`OS_SDD` below is the absolute path of this repository.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes
git add -A && git commit -q -m init
```

## Prompt (round 1, single turn)

```bash
claude -p "/os-propose Add color tags to notes in a note-taking app, so users can assign one of a few preset colors to each note and filter by color. Skip web research." \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" "AskUserQuestion" > b2-round1.jsonl
```

## Prompt (full interview, scripted, multi-turn)

Continue the same session with `claude -c -p`, answering each round tersely
until the checklist closes or round 10 hits, then confirm to write. This
needs one `-c -p` call per round and is the expensive part of this eval.

## Pass criterion

```bash
grep -c "openspec new change" b2-round1.jsonl   # must be 0 before confirmation
python3 -c "
import json
for line in open('b2-round1.jsonl'):
    d = json.loads(line)
    if d.get('type') == 'assistant':
        for c in d['message'].get('content', []):
            if c.get('type') == 'text':
                print(c['text'][:2000])
"
```

Passes if: no artifact is written before the user confirms; round 1's
questions are scope/non-goals/user-and-problem (not edge cases or the TDD
question); a recommended option is marked in any AskUserQuestion-shaped
list; and, over a full multi-turn run, either the checklist closes early
with the pre-summary having no unconfirmed assumption, or round 10 is a hard
stop.

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL**. Ran the round-1 single-turn
prompt for real (`b2-round1.jsonl`, `--allowedTools` without `WebSearch` and
"Skip web research" in the prompt so it wouldn't stall on that question).
`grep -c "openspec new change"` printed `1`, but both matches are the skill
file's own prose (`proposal-flow.md`'s "Never run `openspec new change`..."
line) being echoed back while reading the skill — not an invoked command;
no artifact or change directory was created (artifacts-before-confirmation
holds). The model explicitly labeled its questions "Ronda 1 — alcance e
intención" and asked scope/palette/non-goals/user-problem — matching "Round
1 — scope and intent" coming first, before any edge-case or TDD question.
The full scripted multi-turn interview (reaching round 10, or a resolved
checklist with a clean pre-summary) was **not executed** — a realistic run
is 3-10 round-trips of `claude -c -p`, too expensive to script and run for
real within this session. Recommended options being marked as such, and the
round-10 hard stop specifically, remain unverified; noting this as a gap
rather than asserting a pass.
