---
name: os-propose
description: Use when a request is scoped and fits in one session, ready for a straightforward interview — writes proposal.md, design.md, delta specs and tasks.md for a new OpenSpec change, one topic at a time.
disable-model-invocation: true
argument-hint: "[request | openspec/explorations/<file>.md | openspec/maps/<file>.md#<stretch>]"
metadata:
  shared:
    - interview.md
    - proposal-flow.md
    - proposal-templates.md
    - session-options.md
    - next-step.md
---

# os-propose

Interviews the user by **topic**, in checklist order, then writes the
change's artifacts. For requests whose decisions cascade into each other,
`/os-propose-grill` fits better.

Before step 1, read `interview.md`, `proposal-flow.md`, `proposal-templates.md`, `session-options.md` and `next-step.md`.

## 1. Before the interview

See "Before the interview" in `proposal-flow.md`.

## 2. Interview by topic, deep-style

Follow `interview.md`. Order rounds by theme, 2–4 questions per round (one
AskUserQuestion call):

1. **Round 1 — scope and intent**: scope, non-goals, user and problem.
2. **Round 2 — key decisions**: design decisions, each with its trade-offs.
3. **Round 3 — edge cases**: edge cases, errors, permissions, security,
   data, migration, compatibility, interaction with existing functionality.
4. **Rounds 4–10 — extra**: only for checklist points still unresolved or
   unconfirmed after round 3. See "Stopping" in `interview.md` for when to
   close early and the round-10 ceiling.

Stop once the checklist is resolved.

## 3. After the interview

See "After the interview" in `proposal-flow.md`.
