# Session options

Contract shared by `os-propose`, `os-propose-grill`, `os-review` and
`os-explore`: two questions that belong to the user, not to the skill.

## Web research question

Before round 1 (or before the first check, in `os-review`), ask with
**AskUserQuestion** whether to research the web for this topic — prior art,
library docs, upstream behavior — before proceeding.

- If accepted, do the research before asking anything else and use it to
  inform later questions and the pre-summary.
- If declined, proceed without it. Don't ask again later in the same
  session.

## TDD question

At the end of the interview, once the checklist (or the grill's frontier) is
resolved, ask with **AskUserQuestion** whether to plan and write the change
with TDD or standard, recommending based on what the session has seen
(existing test coverage, whether the change touches a pure-logic seam vs.
glue code):

- standard (recommended when there's no obvious seam or the change is mostly
  glue/config)
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
