# Proposal flow

Contract shared by `os-propose` and `os-propose-grill`: the artifacts both
write and the gates before writing them.

## Root check

Run `openspec context --json` first. If `root` is missing or null, the
project has no OpenSpec root — say so and stop rather than guessing a
location or running `openspec init` unasked.

## Detect an existing change or spec

Before interviewing, run `openspec list --json` (active changes),
`openspec status --all --json` (each active change's `isPlanningComplete`
and task counts) and `openspec list --specs` (capabilities the project
already covers):

- A change with the same name, or whose capabilities overlap the request:
  - **No tasks checked yet**: ask whether to continue that change or start a
    new one. Continuing skips `openspec new change` entirely — write only
    what's missing or different, don't recreate existing artifacts.
  - **Some tasks checked**: this is mid-implementation. Don't propose over
    it — end pointing at `/os-review <name>` instead.
- A spec (`list --specs`) already covers the requested behavior with no
  change needed: say so, cite the spec, and stop rather than proposing a
  no-op change.

## Setup

- If invoked with an `openspec/explorations/*.md` path or a
  `openspec/maps/<name>.md#<stretch>` path, see "Starting from an
  exploration" / "Starting from a map stretch" in `proposal-templates.md`.
- Otherwise, read enough of the repo, `openspec/specs/` and
  `openspec/changes/` to understand the surrounding system.
- Apply the project's `context`/`rules` (from `openspec context --json`) as
  constraints on what you write — don't copy their text into the artifacts.

## Confirm before writing

Present the pre-summary: the resolved checklist, the `n/a`'d points, and
anything pushed to Open Questions at the round limit. Never run
`openspec new change` or create any artifact until the user confirms it.

## Write the artifacts

1. For a new change: `openspec new change <name>` (schema `spec-driven`).
   For a continued change (see "Detect an existing change or spec"), skip
   this — the change directory already exists.
2. For each artifact (`proposal`, `design`, the delta specs, `tasks`), run
   `openspec instructions <artifact> --change <name> --json` and follow its
   `instruction`/`template`, in the order its `dependencies` require —
   `proposal` before `design`/specs, both before `tasks`. A `done` artifact
   in `openspec status --json` only means the file exists; re-run its
   `instructions` if the content needs to change.
3. `proposal.md`: Why / What Changes / Capabilities / `## Implementation` /
   Non-Goals / Impact. Link the exploration or map stretch if one was used.
4. `design.md`: Context / Decisions (with alternatives considered) / Risks /
   Open Questions. Add `## Seams` if the mode is `tdd`.
5. Delta specs per capability under `specs/<capability>/spec.md`, one
   `#### Scenario:` per behavior discussed.
6. `tasks.md`: every task ends with `— covers:` (see "Task → scenario link"
   in `proposal-templates.md`), states how it's verified (see "How a task is
   verified"), and every scenario in the delta specs is covered.

## Close

Run `openspec validate --change <name>` and fix anything it flags. End with
`Next: /os-review <name>`.
