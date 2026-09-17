# os-sdd

A family of 10 `os-*` skills that drives the [OpenSpec](https://github.com/)
CLI (`spec-driven` schema) **without modifying it**. Skills never invoke each
other: each one ends with a `Next: /os-<skill> <arg>` line, and the user
decides whether to follow it.

## Cycle

```
os-explore ──┬─→ os-propose ───────┐
             └─→ os-propose-drill ─┤
                                    ↓
                            os-review-spec
                                    ↓
                       os-apply / os-apply-tdd
                                    ↓
                              os-verify ──→ (archive)

     os-amend-spec: changes the course of an existing change, in any phase
     os-handoff:    multi-session handoff, within any phase
     os-wayfind:    decision map for work that doesn't fit in one session
                     → resolved legs become changes via os-propose
```

## The 10 skills

| Skill | When | Produces |
|---|---|---|
| `os-explore` | Vague idea or request with no shape yet (only via `/os-explore`) | Exploration file; never code or changes |
| `os-propose` | Scoped request, known shape | `proposal.md`, `design.md`, delta specs, `tasks.md` — topic-based interview |
| `os-propose-drill` | Ambiguous request, cascading decisions | Same as `os-propose` — interview driven by the decision tree's frontier |
| `os-review-spec` | Artifacts ready, before implementing | Findings report by severity, offer to fix |
| `os-amend-spec` | Change of course mid-implementation | Updated artifacts, completed tasks preserved |
| `os-apply` | `standard` change with pending tasks | Code + checked tasks, with evidence per task |
| `os-apply-tdd` | `tdd` change with pending tasks | Same, via red→green cycles on the declared seams |
| `os-verify` | All tasks done | `VERIFY.md` (`PASS`/`BLOCK`); offers to archive on `PASS` |
| `os-handoff` | End of session, handoff needed | `HANDOFF.md` rewritten in full (or the exploration's `Next step`) |
| `os-wayfind` | Work that doesn't fit in one session | Map in `openspec/maps/<name>.md`; ready legs → `os-propose` |

## Artifact conventions

They remain valid OpenSpec — the CLI ignores them, the family reads them.

- **`## Implementation`** in `proposal.md`, with the literal line
  `Implementation: tdd` or `Implementation: standard`. `os-apply*` reads it
  with a literal grep; if missing, it assumes `standard` and warns.
- **`## Seams`** in `design.md`, only for `tdd`: a `seam → scenarios` table.
  A scenario that can't be automated is written as `manual: <check>` with its
  reason.
- **`— covers: <capability>/<scenario>[, …]`** at the end of every task in
  `tasks.md` (or `— covers: none (<reason>)` for infrastructure tasks). The
  `- [ ] X.Y` checkbox is unchanged, so `openspec` still counts it.

## Files outside the OpenSpec schema

- `openspec/changes/<name>/VERIFY.md` — `os-verify` verdict with a content fingerprint
  (`scripts/fingerprint.py`); archived together with the change.
- `openspec/changes/<name>/HANDOFF.md` — multi-session handoff; `os-verify` deletes it
  before archiving.
- `openspec/explorations/<YYYY-MM-DD>-<topic>.md` — bridge from `os-explore`
  to `os-propose*`; never moved or deleted.
- `openspec/maps/<name>.md` — `os-wayfind` maps.
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
`proposal-flow.md`: a contract shared by several skills.
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
than in code: `os-apply` passing the task id, `os-handoff` with no active
change, and `os-explore` not triggering on a plain question. Each case has
setup, the exact prompt, an observable pass criterion and its last result;
run them by hand in a clean session (see `evals/README.md`). They are not
part of `unittest`.

## Archive order

`clarify-os-skill-instructions` modifies requirements that
`add-os-skill-family` adds, so archive `add-os-skill-family` first.

## Acknowledgements

| Idea | Source | Where it lands |
|---|---|---|
| `proposal → design, specs → tasks` cycle, `status/instructions/validate/archive` CLI | OpenSpec | All skills |
| Thinking partner, no implementation without approval | Superpowers (`brainstorming`) | `os-explore` |
| Throwaway prototype for viability doubts | Superpowers (`prototype`, via Pocock) | `os-explore` — spikes |
| Verification before claiming completion, real evidence | Superpowers (`verification-before-completion`) | `os-verify` |
| Per-task brief, delegation with progress log | Superpowers (`subagent-driven-development`) | `scripts/task_brief.py`, `os-apply*` |
| Per-file red→green cycle | Superpowers (`test-driven-development`) | `os-apply-tdd` |
| `SessionStart` hook | Superpowers | `hooks/session-start.py` |
| Questioning along the decision tree's frontier | Matt Pocock (`grilling`) | `os-propose-drill` |
| Seam-based TDD, `/implement` + `/tdd` | Matt Pocock | `os-apply-tdd` |
| Multi-session handoff | Matt Pocock (`handoff`) | `os-handoff` |
| Local decision map | Matt Pocock (`wayfinder`) | `os-wayfind` |

## Requirements

`openspec` CLI ≥ 1.3, Python 3 (stdlib only, no external dependencies),
`git`, `bash` (for `install.sh`).

## Tests

```bash
python3 -m unittest discover tests
python3 tests/lint_skills.py
python3 scripts/sync-shared.py
```
