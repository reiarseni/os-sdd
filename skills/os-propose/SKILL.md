---
name: os-propose
description: Use when a request is scoped (fits in one session, modifies an existing flow) and ready for a straightforward interview — writes proposal.md, design.md, delta specs and tasks.md for a new OpenSpec change, one topic at a time.
disable-model-invocation: true
argument-hint: "[request | openspec/explorations/<file>.md]"
metadata:
  shared:
    - interview.md
    - proposal-flow.md
    - proposal-templates.md
    - next-step.md
---

# os-propose

Interviews the user by **topic**, in checklist order, then writes the
change's artifacts. For requests whose decisions cascade into each other,
`/os-propose-drill` fits better.

Before step 1, read `interview.md`, `proposal-flow.md`,
`proposal-templates.md` and `next-step.md`.

## 1. Setup

See "Setup" in `proposal-flow.md`.

## 2. Interview by topic

Follow `interview.md`. Order rounds by the "Coverage checklist" in
`interview.md`, 2–4 questions per round (one AskUserQuestion call): scope,
non-goals, user and problem come in the first round, before edge cases or
migration. Ask the "Implementation mode question" from
`proposal-templates.md` as part of the checklist.

## 3. Confirm before writing

See "Confirm before writing" in `proposal-flow.md`.

## 4. Write the artifacts

See "Write the artifacts" in `proposal-flow.md`.

## 5. Close

See "Close" in `proposal-flow.md`.
