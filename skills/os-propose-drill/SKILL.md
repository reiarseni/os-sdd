---
name: os-propose-drill
description: Use when a new change's request is ambiguous or high-stakes and its design decisions depend on each other, so questions can't be asked in a fixed topic order — interviews only the questions whose prerequisites are already answered, round after round, then writes proposal.md, design.md, delta specs and tasks.md. For a scoped request with a clear shape use os-propose instead.
disable-model-invocation: true
argument-hint: "[request | openspec/explorations/<file>.md]"
metadata:
  shared:
    - interview.md
    - proposal-flow.md
    - proposal-templates.md
    - next-step.md
---

# os-propose-drill

Chooses what to ask by the decision tree's frontier instead of by topic,
then writes the change's artifacts.

Before step 1, read `interview.md`, `proposal-flow.md`,
`proposal-templates.md` and `next-step.md`.

## 1. Setup

See "Setup" in `proposal-flow.md`.

## 2. Interview by frontier

Follow `interview.md`, choosing each round's questions like this:

- Ask **every** checklist item whose prerequisites are already resolved —
  that's the frontier. A question that depends on another question from
  the same round waits for a later round.
- If the frontier has more than 4 questions, split it into several
  AskUserQuestion calls in the same round; no call may depend on an earlier
  call's answer.
- When a frontier question needs a fact from the repo or the system (a
  config value, whether a dependency exists, current test coverage), find
  it yourself instead of asking.
- Ask the "Implementation mode question" from `proposal-templates.md` as
  soon as scope and whether the change touches a seam are resolved.

## 3. Confirm before writing

See "Confirm before writing" in `proposal-flow.md`.

## 4. Write the artifacts

See "Write the artifacts" in `proposal-flow.md`.

## 5. Close

See "Close" in `proposal-flow.md`.
