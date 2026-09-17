# B5 — `os-propose`: generated artifacts in `tdd` vs `standard` mode

Covers: a `tdd` change gets a single, unambiguous seam definition and
test-first tasks with verification; a `standard` change still gets tasks
generated with verification; `openspec validate` passes on what's written.

`OS_SDD` below is the absolute path of this repository.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes
git add -A && git commit -q -m init
```

## Prompt (tdd, compressed to finish in one turn)

A prompt that tells the model to self-answer every interview question with
sensible defaults instead of pausing — the only way to get a full
propose→write→validate run out of a single non-interactive `claude -p` call.

```bash
claude -p "/os-propose Add a pure function slugify(text) to a small Python utils module that turns a title into a URL slug (lowercase, spaces to hyphens, strip non-alphanumeric). Skip web research. To move fast: for every interview question, just pick the most sensible default yourself, state it as a decision, and move on without waiting for me. Resolve the checklist in as few rounds as possible, then use TDD (there's an obvious pure seam), then write all the artifacts and confirm the plan is ready. Go all the way to writing proposal.md, design.md, specs and tasks.md, then run openspec validate." \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Edit" "Bash" "AskUserQuestion" > b5-tdd.jsonl
```

## Pass criterion

```bash
find openspec/changes -type f
grep -n "Implementation:" openspec/changes/*/proposal.md
grep -n -A5 "## Seams" openspec/changes/*/design.md
cat openspec/changes/*/tasks.md
openspec validate --change <the-generated-name>
```

Passes if: `Implementation: tdd` is written, `## Seams` maps exactly one
seam to the change's scenarios, `tasks.md` starts from a red/failing-test
task before any implementation task, every task carries `— covers:` and a
verification command, and `openspec validate` exits clean.

## Last run

2026-09-17, Claude Code 2.1.274 — **PARTIAL, tdd branch run for real**.
Ran the compressed tdd prompt; it went all the way through: wrote
`openspec/changes/add-slugify-util/{proposal,design,tasks}.md` and
`specs/text-utils/spec.md`, and `openspec validate` printed "Change
'add-slugify-util' is valid" in the transcript.

- `proposal.md` has the literal `Implementation: tdd` line.
- `design.md`'s `## Seams` maps exactly one seam
  (`` `slugify(text)` function in `utils/text.py` ``) to all six scenarios —
  single unambiguous seam definition holds.
- `tasks.md` has three tasks, each with `— covers:` and a `pytest` command
  as its verification, and starts red-then-green (1.1 write failing tests
  and confirm the fail reason, 1.2 implement and confirm green, 1.3 an
  optional refactor with `covers: none`).
- **Deviation from the ideal in "How a task is verified" /
  `tests.md`'s "one scenario, one slice"**: task 1.1 bundles *all six*
  scenarios into one red test task instead of one task per seam-scenario
  vertical slice. This is a real, worth-tracking gap between what
  `proposal-templates.md`/`shared/proposal-flow.md` describe and what the
  model actually generated under a "move fast" prompt — not something to
  paper over.

The `standard`-mode branch was **not executed** (a second full compressed
run of the same cost) — deferred for time; noting the gap rather than
inventing a result.
