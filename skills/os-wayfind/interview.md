# Interview contract

Shared by `os-propose` and `os-propose-grill`. Each skill defines how it
chooses what to ask (thematic rounds vs. decision-tree frontier); this file
defines what both must cover and how. The TDD/standard question lives in
`session-options.md`, asked at the end, not as a checklist point here.
`os-wayfind` also reads this file but applies only "Tool", "Round summary" and
"Research", scoped to the one decision it is resolving.

## Goal

Cover everything needed to write a proposal, design, specs and tasks that
`os-review` won't bounce back. Not "ask a few questions" — cover the
checklist.

## Coverage checklist

Every checklist point must end resolved or marked `n/a: <reason>`:

1. Scope and non-goals
2. User and problem
3. Design decisions, with alternatives considered
4. Edge cases and errors
5. Permissions and security
6. Data, migration and compatibility
7. Interaction with existing functionality

## Stopping

Never present the pre-summary with an unconfirmed assumption still in it —
either resolve it with a question or mark it `n/a: <reason>`.

- `os-propose`: stop as soon as the checklist is fully resolved (or `n/a`'d).
  Otherwise stop at a **fixed limit of 10 rounds**: on round 10, stop
  regardless of what's left, present the pre-summary, and move whatever's
  unresolved into `design.md`'s Open Questions. Never extend past round 10.
- `os-propose-grill`: no round limit. Stop only when the decision tree's
  frontier is empty — every question it opened has an answer or is marked
  `n/a: <reason>`.

## Tool

Use **AskUserQuestion** for every question that has finite options. Put your
recommended answer as the first option, labeled "(Recommended)", with the
reasoning in its `description` or `preview`. Ask open-ended questions in
plain text.

## Round summary

Close every round with a compact summary of what got decided that round — a
few bullet lines, not a transcript.

## Research

Investigate before round 1: code, `openspec/specs/` and existing changes.
Between rounds, only chase facts a specific answer just opened up; don't
re-research things already settled.
