# Proposal templates

Formats shared by the skills that write or amend a change's artifacts. The
TDD/standard question and its `## Implementation` line are asked and written
per `session-options.md`, not here.

## Starting from an exploration

If invoked with a path under `openspec/explorations/`, read that file first.
Don't repeat the research it already covers. Its "Leaning decisions" become
confirmation questions in your first round instead of open questions. When
you write `proposal.md`, link the exploration:

```
Exploration: openspec/explorations/<file>.md
```

## Starting from a map stretch

If invoked with `openspec/maps/<name>.md#<stretch>`, read that stretch's
`Decisions:` line in `## Stretches`. Each quoted title names a
`### <decision>` block under `## Decisions so far`; read those blocks.

- If `Decisions:` has no quoted titles, or a quoted title matches no block,
  ask the user which blocks belong to the stretch before round 1 — don't
  deduce it.
- The stretch's decisions are already resolved: never ask them again. They
  count as resolved decisions within checklist point 3, which stays open
  for any decision the stretch doesn't cover.
- Copy each one into `design.md`'s Decisions, with the alternatives its
  block records.
- Reopen one only if the code or the specs contradict it: ask the user
  about that decision, citing the file that contradicts it.

When you write `proposal.md`, link the stretch:

```
Map: openspec/maps/<name>.md#<stretch>
```

`os-wayfind` fills in that stretch's `Change:` line by searching for this
`Map:` line across changes, so write it exactly once, verbatim.

## Seams (tdd only)

A **seam** is a stable public interface a scenario is tested through — a CLI
command, an HTTP endpoint, a module's exported function.

When the mode is `tdd`, `design.md` MUST include a `## Seams` section: a
table mapping each seam to the scenarios tested through it. A scenario that
can't be automated appears as `manual: <verification>` with its reason
instead of a seam:

```
## Seams

| Seam | Scenarios |
|---|---|
| `export` CLI command | Export to CSV, Export with no rows |
| manual: open the exported file in a spreadsheet app | Accented characters survive export (manual: depends on the app's encoding detection) |
```

Every scenario in the change's delta specs must appear in this table exactly
once.

## Task → scenario link

Every task in `tasks.md` ends with a `— covers:` suffix, after the task
text, on the same line as the `- [ ] X.Y` checkbox (the CLI still reads that
checkbox literally):

```
- [ ] 1.1 Add the export command skeleton — covers: none (scaffolding)
- [ ] 2.1 Write rows as CSV — covers: data-export/Export to CSV, data-export/Export with no rows
```

Use `— covers: none (<reason>)` only for infrastructure/docs tasks that
don't map to a scenario. Every scenario in the delta specs must be covered
by at least one task.

## How a task is verified

Every task states, in its own text, the command or check that verifies it —
`openspec` tracks this per OpenSpec ≥ 1.10. In `standard` mode this can be
any check (a command, a manual step); in `tdd` mode it's the seam's test
command, and `tasks.md` is organized in vertical slices: each task covers
one seam's scenarios and starts from a red test before the implementation,
not a task per file or per layer.
