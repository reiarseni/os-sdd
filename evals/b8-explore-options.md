# B8 — `os-explore`: initial options, methods, prototypes and closing

Covers (per `design.md`'s `## Seams`, all 16 `os-discovery` scenarios): the
initial options are asked and recorded; each method (Pocock, Superpowers,
openspec-explore stance) is applied distinctly; `scoped` is decided by
open-decisions, not by "existing vs. new" flow; `ambiguous` recommends
`/os-propose-grill`; a preliminary team-lead summary is offered at close;
ASCII diagrams; a bounded/small/ambiguous/large request each classify
correctly; a spike resolves and reclassifies; a prototype in a git project
lives on `prototype/<name>` and isn't deleted, in a non-git project lives in
a temp dir outside it, or is declined entirely; the exploration file is
resumed by path or by same-day topic; closing fills every section.

`OS_SDD` below is the absolute path of this repository.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes openspec/explorations
cat > api.py <<'PY'
def handle_request(req):
    return {"status": "ok"}
PY
git add -A && git commit -q -m init
```

## Prompt (ambiguous/large request)

```bash
claude -p "/os-explore I'm not sure how to add background job processing to this API — could be a queue, could be cron, could be something else entirely" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" "AskUserQuestion" > b8.jsonl
```

## Pass criterion

The first question covers web research, method (with a reasoned pick, not
just a menu), and prototypes, before any exploration content is written.

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL, initial-options step
confirmed**. Ran the prompt above for real (`b8.jsonl`). No exploration file
was created yet (the turn ended at the initial question, as `-p` always
does). The model's single combined question hit all three parts correctly:

1. Web research, framed as a real choice ("check prior art... or skip
   straight to reasoning").
2. Method, with **reasoning tied to the repo's actual state** (a 3-line
   stub, no dependency manifest, empty `openspec/`) leading to a specific
   recommendation — Superpowers brainstorming — and explicitly inviting
   correction. This is a genuine reasoned pick, not a bare menu.
3. Prototypes, framed around a concrete viability doubt
   ("will a cron-based approach even fit how this API is deployed?") and
   naming the `prototype/<name>` branch convention correctly.

It also read `api.py` and correctly discounted `b8.jsonl` itself (its own
output-redirect target, visible in the sandbox) as irrelevant noise —
sensible fact-gathering, not fabricated.

**Not executed** in this pass, and reported as open rather than invented:
the `scoped`-by-open-decisions vs. `ambiguous` classification actually being
applied (needs the interview to proceed past step 1), each method's
distinct mechanics in practice, ASCII diagrams, a `spike` resolving and
reclassifying, an actual prototype being built (in a git repo and in a
non-git one), resuming an exploration by path or same-day topic, and the
closing step filling every template section including the optional
`## Team-lead summary`. This is by far the largest scenario set of any
`evals/b*` file (16 scenarios) and would need many separate scripted
multi-turn runs to cover for real; only the initial-options mechanism was
verified here.
