# os-sdd

A family of 8 `os-*` skills that drives the [OpenSpec](https://github.com/)
CLI (`spec-driven` schema) **without modifying it**. Skills never invoke each
other: each one ends with a `Next: /os-<skill> <arg>` line, and the user
decides whether to follow it.

## Cycle

```
os-explore ──┬─→ os-propose ───────┐
             └─→ os-propose-grill ─┤
                                    ↓
                              os-review
                                    ↓
                                os-apply
                                    ↓
                              os-verify ──→ (archive)

     os-review:   also runs mid-implementation, to change course without
                   fragmenting the cycle into a separate skill
     os-handoff:  multi-session handoff, within any phase
     os-wayfind:  decision map for work that doesn't fit in one session
                  → resolved stretches become changes via os-propose
```

`os-propose`, `os-propose-grill`, `os-review` and `os-explore` all open by
asking whether to research the web first, and `os-propose*` asks whether to
plan with TDD only at the end of the interview — see `shared/session-options.md`.

## The 8 skills

| Skill | When | Produces |
|---|---|---|
| `os-explore` | Vague idea or request with no shape yet (only via `/os-explore`) | Exploration file; never code or changes |
| `os-propose` | Scoped request, known shape | `proposal.md`, `design.md`, delta specs, `tasks.md` — deep-style topic interview, ≤10 rounds |
| `os-propose-grill` | Ambiguous request, cascading decisions | Same as `os-propose` — interview driven by the decision tree's frontier, no round cap |
| `os-review` | Artifacts ready, before implementing or mid-implementation | Findings as concrete proposals, `REVIEW.md` (`READY`/`BLOCK`), optional `TEAMLEAD.md` round trip |
| `os-apply` | Change with pending tasks | Code + checked tasks, with evidence per task — standard, or tdd's red→green cycles on the declared seams, per `proposal.md`'s mode |
| `os-verify` | All tasks done | `VERIFY.md` (`PASS`/`BLOCK`); offers to archive on `PASS` |
| `os-handoff` | End of session, handoff needed | `HANDOFF.md` rewritten in full (or the exploration's/map's own section) |
| `os-wayfind` | Work that doesn't fit in one session | Map in `openspec/maps/<name>.md`; ready stretches → `os-propose` |

## Artifact conventions

They remain valid OpenSpec — the CLI ignores them, the family reads them.

- **`## Implementation`** in `proposal.md`, with the literal line
  `Implementation: tdd` or `Implementation: standard`. `os-apply` reads it
  with a literal grep and loads only `modes/<mode>.md`; if missing, it asks
  which mode the change is.
- **`## Seams`** in `design.md`, only for `tdd`: a `seam → scenarios` table.
  A scenario that can't be automated is written as `manual: <check>` with its
  reason.
- **`— covers: <capability>/<scenario>[, …]`** at the end of every task in
  `tasks.md` (or `— covers: none (<reason>)` for infrastructure tasks). The
  `- [ ] X.Y` checkbox is unchanged, so `openspec` still counts it.

## Files outside the OpenSpec schema

- `openspec/changes/<name>/VERIFY.md` — `os-verify` verdict with a content fingerprint
  (`scripts/fingerprint.py`); archived together with the change.
- `openspec/changes/<name>/REVIEW.md` — `os-review` verdict (`READY`/`BLOCK`)
  with an artifacts-only fingerprint (`scripts/fingerprint.py --artifacts`);
  `os-apply*` and the hook only accept a fresh `READY`.
- `openspec/changes/<name>/TEAMLEAD.md` — human-language summary and
  implications for a team lead, with a `## Team-lead feedback` section
  `os-review` reads back in; outside both fingerprints.
- `openspec/changes/<name>/HANDOFF.md` — multi-session handoff; `os-verify` deletes it
  before archiving.
- `openspec/explorations/<YYYY-MM-DD>-<topic>.md` — bridge from `os-explore`
  to `os-propose*`; never moved or deleted.
- `openspec/maps/<name>.md` — `os-wayfind` maps.
- `prototype/<name>` (branch, in a git project) — a confirmed prototype from
  `os-explore`; never merged, never deleted. Outside a git project it's a
  temporary directory outside the project instead.
- `openspec/os.yaml` — optional project configuration.

> **Gitignore build artifacts** (`__pycache__/`, `*.pyc`, `dist/`,
> `node_modules/`, …). `scripts/fingerprint.py` hashes everything
> `git ls-files -co --exclude-standard` returns; if a build artifact is
> tracked or not ignored, every test run regenerates it and the `os-verify`
> `PASS` goes stale on its own, every session.

## `openspec/os.yaml`

```yaml
version: 1
session_hook: off   # on | off
```

Missing file ⇒ everything disabled. Edited by hand; no script writes it.

## `SessionStart` hook

Suggests (never forces) the next skill based on the phase of each open
change, in ≤5 lines of context. Exits silently with code 0 if there is no
`openspec/`, if `session_hook` isn't `on`, or on any internal error.

Installing into a consumer project:

```bash
python3 scripts/install-hook.py /path/to/project
```

Copies the scripts into `<project>/.claude/hooks/os/` (versioned) and
registers the entry in `<project>/.claude/settings.json` without duplicating
or replacing existing hooks. `--update` refreshes only the copy. The team
gets the hook on `pull`, without installing `os-sdd`.

## Installing the family

Per project (default mode — each project that wants the family installs it
this way):

```bash
./install.sh /path/to/project   # symlinks skills/os-* into <project>/.claude/skills/, idempotent
```

Globally, for personal use in any project:

```bash
./install.sh                    # symlinks skills/os-* into ~/.claude/skills/, idempotent
```

Both modes create symlinks to this repo, not copies — unlike the hook (copied
so the team gets it without installing `os-sdd`), the family is only used by
whoever has `os-sdd` cloned locally. `install.sh` never overwrites a
destination that isn't one of its own symlinks.

## Uninstalling

Delete the installed `os-*` symlinks (per project or in `~/.claude/skills/`).
The `os-sdd` source directories are never touched by installation.

## Shared content (`shared/`)

`select-change.md`, `implementation-mode.md`, `next-step.md`,
`interview.md`, `proposal-templates.md`, `apply-common.md`,
`proposal-flow.md`, `session-options.md`: a contract shared by several
skills. `session-options.md` is the web-research and TDD questions, shared
by `os-propose`, `os-propose-grill`, `os-review` and `os-explore`.
`scripts/sync-shared.py` copies each file into the skills that declare it
under `metadata:` in their frontmatter:

```yaml
metadata:
  shared:
    - select-change.md
  shared-scripts:
    - task_brief.py
```

`tests/lint_skills.py` fails if a copy diverges from its source, or if
`shared:` / `shared-scripts:` sit at the top level of the frontmatter. A skill never borrows steps from another one
("same as `os-apply`") — the other skill isn't loaded, so common steps live
here, and the linter rejects those phrases.

Scripts a skill runs (`task_brief.py`, `fingerprint.py`) are declared under
`metadata.shared-scripts` and copied from `scripts/` into `skills/<skill>/scripts/`,
so the skill invokes them as `${CLAUDE_SKILL_DIR}/scripts/<file>` from any
project it's installed into. `scripts/` stays the source of truth (the hook
and tests import from it). The linter fails on a bare `scripts/<file>` path
in `SKILL.md`, and on any script path or `${CLAUDE_SKILL_DIR}` in supporting
files, since Claude Code only substitutes that variable in `SKILL.md`.

Each rule lives in one file. The linter also fails when:

- a normalized run of 8 or more words appears both in a `SKILL.md` and in
  one of its shared files (lowercased, markdown stripped) — remove the
  duplicate, there are no exceptions;
- a reference points at a missing section (`"<Section>" in <file>.md`,
  `see <file>.md ("<Section>")`, `"<Section>" below`), or says
  "below"/"above" without naming a section.

Every `SKILL.md` opens with "Before step 1, read …" listing the contracts it
always uses, and declares `argument-hint`. `task_brief.py <change> <id>`
takes the task id as written in `tasks.md` (`2.1`); a plain integer is still
read as the task's position.

## Behavior evals (`evals/`)

Manual cases for failures that live in how the model reads a skill rather
than in code. Each case has setup, the exact prompt, an observable pass
criterion and its last result; run them by hand in a clean session (see
`evals/README.md`). They are not part of `unittest`.

- `a1`-`a3`: `os-apply` passing the task id, `os-handoff` with no active
  change, `os-explore` not triggering on a plain question.
- `b1`-`b11`: the session-options contract, both propose interviews, source
  detection, generated-artifact quality, `os-review`'s findings/adjustments/
  team-lead round trip, `os-explore`'s initial options, the apply review
  gate, the verify evidence package, and handoff/wayfind with maps.

**Known constraint**: `AskUserQuestion` is not available in headless
`claude -p` sessions (confirmed while running `b1`-`b8`) — every skill falls
back to plain text and reports the tool as unavailable. A `b*` eval can
verify a question's content, order and reasoning this way, but not that the
literal tool call fires, and a single non-interactive `-p` turn always ends
at the first such question — verifying what happens after the user answers
needs a scripted multi-turn `-c -p` conversation.

## Archive order

`clarify-os-skill-instructions` modifies requirements that
`add-os-skill-family` adds, so archive `add-os-skill-family` first.
`reshape-os-cycle` renames/retires skills that both of those reference by
name; archive it after them. `merge-os-apply-modes` builds on the `os-review`
capability `reshape-os-cycle` adds, so archive it after `reshape-os-cycle`.

## Migration

`reshape-os-cycle` renamed and retired three skills. A project with an
active change or a habit built around the old names should switch to the
new ones — nothing migrates their in-flight changes automatically.

| Old name | New name | Notes |
|---|---|---|
| `os-propose-drill` | `os-propose-grill` | Same role; the interview is now Pocock-style grilling with no round cap. |
| `os-review-spec` | `os-review` | Same role; now also runs mid-implementation, proposes concrete fixes, and always writes `REVIEW.md`. |
| `os-amend-spec` | *(retired)* | Its role — changing course with tasks already done — is now `os-review`'s mid-implementation path. |
| `os-apply-tdd` | `os-apply` | Same role; `os-apply` now reads `Implementation:` from `proposal.md` and picks the mode itself. |

## Acknowledgements

| Idea | Source | Where it lands |
|---|---|---|
| `proposal → design, specs → tasks` cycle, `status/instructions/validate/archive` CLI | OpenSpec | All skills |
| `context`/`instructions --json`/`requires` graph/`status --all`/`show --diff`/`root` check | OpenSpec ≥ 1.11-1.13 | `shared/proposal-flow.md`, `hooks/os_state.py`, `os-review` |
| Thinking partner, no implementation without approval | Superpowers (`brainstorming`) | `os-explore` — one method option |
| Throwaway spike for viability doubts, deleted once answered | Superpowers (`prototype`) | `os-explore` — spikes |
| Verification before claiming completion, real evidence | Superpowers (`verification-before-completion`) | `os-verify` |
| Per-task brief, delegation with progress log | Superpowers (`subagent-driven-development`) | `scripts/task_brief.py`, `os-apply` |
| Per-file red→green cycle | Superpowers (`test-driven-development`) | `os-apply` — `tdd` mode |
| `SessionStart` hook | Superpowers | `hooks/session-start.py` |
| Questioning along the decision tree's frontier, ❓/➡️ format | Matt Pocock (`grilling`) | `os-propose-grill`, `os-explore` — one method option |
| Confirmed prototype on a branch, kept rather than deleted | Matt Pocock (`prototype`) | `os-explore` — prototypes |
| Seam-based TDD, `/implement` + `/tdd` | Matt Pocock | `os-apply` — `tdd` mode |
| Multi-session handoff | Matt Pocock (`handoff`) | `os-handoff` |
| Local decision map, stretches | Matt Pocock (`wayfinder`) | `os-wayfind` |
| Light-touch ambiguity resolution, minor assumptions recorded rather than asked | `openspec-explore` (upstream) | `os-explore` — one method option |
| Fixed-purpose rounds with a pre-summary before writing | `openspec-propose-deep` | `os-propose` |

## Requirements

`openspec` CLI ≥ 1.13, Python 3 (stdlib only, no external dependencies),
`git`, `bash` (for `install.sh`).

## Tests

```bash
python3 -m unittest discover tests
python3 tests/lint_skills.py
python3 scripts/sync-shared.py
```
