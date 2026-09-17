# Proposal flow

Contract shared by `os-propose` and `os-propose-drill`: the artifacts both
write and the gates before writing them.

## Setup

- If invoked with an `openspec/explorations/*.md` path, see "Starting from
  an exploration" in `proposal-templates.md`.
- Otherwise, read enough of the repo, `openspec/specs/` and
  `openspec/changes/` to understand the surrounding system.

## Confirm before writing

Present the pre-summary: the resolved checklist, the `n/a`'d points, and
anything pushed to Open Questions at the round limit. Never run
`openspec new change` or create any artifact until the user confirms it.

## Write the artifacts

1. `openspec new change <name>` (schema `spec-driven`).
2. `openspec/changes/<name>/proposal.md`: Why / What Changes / Capabilities /
   `## Implementation` / Non-Goals / Impact. Link the exploration file if
   one was used.
3. `design.md`: Context / Decisions (with alternatives considered) / Risks /
   Open Questions. Add `## Seams` if the mode is `tdd`.
4. Delta specs per capability under `specs/<capability>/spec.md`, one
   `#### Scenario:` per behavior discussed.
5. `tasks.md`: every task ends with `— covers:` (see "Task → scenario link"
   in `proposal-templates.md`), and every scenario in the delta specs is
   covered.

## Close

Run `openspec validate --change <name>` and fix anything it flags. End with
`Next: /os-review-spec <name>`.
