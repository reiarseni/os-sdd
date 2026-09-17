# Proposal templates

Formats shared by the skills that write or amend a change's artifacts.

## Starting from an exploration

If invoked with a path under `openspec/explorations/`, read that file first.
Don't repeat the research it already covers. Its "Leaning decisions" become
confirmation questions in your first round instead of open questions. When
you write `proposal.md`, link the exploration:

```
Exploration: openspec/explorations/<file>.md
```

## Implementation mode question

Always ask, with AskUserQuestion, whether the change will be built with TDD
or standard, recommending based on what you've seen (existing test coverage,
whether the change touches a pure-logic seam vs. glue code):

- standard (recommended when there's no obvious seam or the change is
  mostly glue/config)
- tdd (recommended when the change adds testable logic behind a seam)

Write the literal line in `proposal.md`, in its own `## Implementation`
section:

```
## Implementation

Implementation: tdd
```
or
```
## Implementation

Implementation: standard
```

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
