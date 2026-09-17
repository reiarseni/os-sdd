# B3 — `os-propose-grill`'s frontier grilling

Covers: no round cap, a question that depends on another still-open question
waits, a frontier of more than 4 questions splits across calls, a fact
checkable in the repo/environment is found rather than asked, and an empty
frontier needs no further confirmation round.

`OS_SDD` below is the absolute path of this repository.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes
cat > config.json <<'JSON'
{"maxUploadSizeMb": 25}
JSON
git add -A && git commit -q -m init
```

## Prompt (round 1, single turn)

An ambiguous, cascading request: whether per-file or per-user limits apply
changes what "size" even means, which changes what the error UX looks like.

```bash
claude -p "/os-propose-grill Enforce upload size limits that adapt per user plan tier" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash" "AskUserQuestion" > b3-round1.jsonl
```

## Pass criterion

```bash
python3 -c "
import json
for line in open('b3-round1.jsonl'):
    d = json.loads(line)
    if d.get('type') == 'assistant':
        for c in d['message'].get('content', []):
            if c.get('type') == 'text':
                print(c['text'][:2500])
"
```

Passes if: `config.json`'s existing `maxUploadSizeMb` is read and cited as a
fact (not asked about), the first round's questions are the ones with no
unresolved prerequisite (tier definitions, not yet the error-UX questions
that depend on them), and no round-limit language ("round 10", "ronda 10")
appears anywhere — a full run should never mention a cap.

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL**. Ran the round-1 prompt for
real (`b3-round1.jsonl`). The model read `config.json` itself and cited
`maxUploadSizeMb: 25` as the existing default in its own summary before
asking anything — fact-vs-decision separation held. It used the exact
❓/➡️ format the skill specifies (falling back to plain text only because
`AskUserQuestion` isn't available under `claude -p`, same infra caveat as
`b1-session-options.md`), asking the web-research question first: "❓
Should I research the web first... ➡️ This shapes whether I recommend a
specific enforcement mechanism...". No mention of a round cap appeared
before the run's single turn ended (it stopped at the web question, as
`-p` always does absent a reply). Not verified in this pass: the actual
round-1 frontier questions past the web question, a frontier of more than 4
questions splitting across calls, and the full multi-round grill reaching
an empty frontier — a single-turn run can't reach those without a scripted
`-c -p` continuation, which wasn't run here for time.
