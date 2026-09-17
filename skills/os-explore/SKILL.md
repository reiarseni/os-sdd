---
name: os-explore
description: Use when the user invokes /os-explore with a vague idea or a request that isn't yet a well-formed change — the entry point before proposing anything. Thinking companion only; never writes production code or creates an OpenSpec change without explicit approval.
disable-model-invocation: true
argument-hint: "[idea | openspec/explorations/<file>.md]"
metadata:
  shared:
    - session-options.md
    - next-step.md
---

# os-explore

A thinking companion. You read code, specs and existing changes; you don't
write production code and you don't run `openspec new change` unless the
user explicitly approves it first.

Before step 1, read `session-options.md` and `next-step.md`.

## 1. Initial options

Before your first question, read enough of the repo and existing
`openspec/changes/` and `openspec/specs/` to say something concrete, then
ask one **AskUserQuestion** covering:

- The "Web research question" from `session-options.md`.
- **Method**: how to think this through —
  - **Pocock grilling**: frontier-driven, ❓/➡️, no round cap — for a request
    whose decisions cascade into each other.
  - **Superpowers brainstorming**: one question at a time, converge on 2-3
    concrete approaches, then design section by section — for a request
    that needs a shape before it needs decisions.
  - **openspec-explore stance**: light-touch, only chase ambiguities that
    would materially change the outcome, record everything else as a minor
    assumption — for a request that's mostly clear already.
- **Prototypes**: whether a throwaway prototype is allowed if a viability
  doubt comes up (see "Prototypes" below).

## 2. Classify out loud

Classify the request with one of these labels, written exactly like this:

| Label | When | Recommended skill |
|---|---|---|
| `spike` | a viability doubt that needs a throwaway experiment, not a design decision | reclassify once the doubt is answered |
| `scoped` | no open, high-impact design decisions remain once explored | `/os-propose` |
| `ambiguous` | fits in one change but has open, high-impact design decisions | `/os-propose-grill` |
| `large` | doesn't fit in one session, or chains several unresolved decisions | `/os-wayfind` |

`scoped` vs. `ambiguous` is decided by whether open decisions remain after
exploring — not by whether the request touches new or existing code. Say
the label and your reasoning. If the user corrects it, keep exploring under
the corrected label.

## 3. Explore, with the chosen method

Read code, specs, and related changes, following the method picked in step
1. Draw any flow or architecture diagram in **ASCII only**.

## 4. Prototypes

If a viability doubt comes up and prototypes were allowed in step 1:
confirm the specific prototype with the user before building it — one
question, answered, then build.

- In a git repo: build it on a branch named `prototype/<name>`. It's never
  merged and never deleted — it stays as executable evidence, unlike a
  `spike`'s throwaway experiment which is deleted once its doubt is
  answered.
- Outside a git repo: build it in a temporary directory outside the
  project, not under version control.

Record the prototype's location and finding in the exploration file's
`## Prototypes` section; only the finding needs to survive if the user
declines to keep the branch.

If the user suggests starting to write production code instead: summarize
what you'd do and name the label's recommended skill instead of
implementing.

## 5. Write the exploration file

Always write the exploration file (template: `EXPLORATION-TEMPLATE.md`):

- If invoked with a path under `openspec/explorations/`, update that file.
- Otherwise create `openspec/explorations/<YYYY-MM-DD>-<topic>.md`, with
  `<topic>` a short kebab-case slug. If that file already exists, add `-2`,
  `-3`… (`2026-09-16-export-2.md`) until the name is free.
- Never pick an existing file because its topic looks similar.

Fill every section of the template: initial options chosen, classification
(and any correction), facts with `file:line`, web sources with their
conclusion, diagrams, prototypes built, leaning decisions with why, open
questions, recommended skill, next step. The file is permanent: archiving a
change never moves or deletes it.

## 6. Close

Whether the exploration finishes or the user interrupts it, make sure every
template section is filled in (or explicitly marked empty). Offer an
optional `## Team-lead summary` — a short plain-language recap for someone
who hasn't read the exploration — if the user wants one. End with
`Next: /os-<skill> <exploration path>` for the recommended skill.
