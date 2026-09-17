---
name: os-propose-grill
description: Use when a new change's request is ambiguous or high-stakes and its design decisions depend on each other, so questions can't be asked in a fixed topic order — grills the decision tree's frontier, round after round with no cap, then writes proposal.md, design.md, delta specs and tasks.md. For a scoped request with a clear shape use os-propose instead.
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

# os-propose-grill

Chooses what to ask by the decision tree's frontier, grilling it Matt
Pocock-style until nothing's left, then writes the change's artifacts.

Before step 1, read `interview.md`, `proposal-flow.md`, `proposal-templates.md`, `session-options.md` and `next-step.md`.

## 1. Setup

See "Setup" and "Detect an existing change or spec" in `proposal-flow.md`.

## 2. Web research question

Ask the "Web research question" from `session-options.md` before the first
round.

## 3. Grill the frontier

Build the decision tree implied by the checklist in `interview.md`, then
work it round after round:

- The **frontier** is every question whose prerequisites are already
  resolved. A question that depends on another question from the same round
  waits for a later round.
- Ask each question in the ❓ (open question) / ➡️ (its consequence, why it
  matters) format, so the user sees what hinges on the answer before
  answering it.
- Separate **facts** (checkable in the repo or environment — find them
  yourself, never ask) from **decisions** (only the user can make the call —
  ask those).
- Skip a question only if answering it truly requires code or a prototype
  to resolve, not because it "could" be resolved by talking — if talking it
  through can settle it, ask it.
- If the frontier has more than 4 questions, split it into several
  AskUserQuestion calls in the same round; no call may depend on an earlier
  call's answer.
- **No round limit.** See "Stopping" in `interview.md` for when the
  frontier counts as empty.
- When the frontier is empty, do one final confirmation pass: restate every
  decision and `n/a` back to the user before moving to the pre-summary — no
  unconfirmed assumption survives past this point.

## 4. TDD question

Once the frontier is empty and confirmed, ask the "TDD question" from
`session-options.md`.

## 5. Confirm before writing

See "Confirm before writing" in `proposal-flow.md`.

## 6. Write the artifacts

See "Write the artifacts" in `proposal-flow.md`.

## 7. Close

See "Close" in `proposal-flow.md`.
