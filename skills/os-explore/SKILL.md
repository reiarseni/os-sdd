---
name: os-explore
description: Use when the user invokes /os-explore with a vague idea or a request that isn't yet a well-formed change — the entry point before proposing anything. Thinking companion only; never writes production code or creates an OpenSpec change without explicit approval.
disable-model-invocation: true
argument-hint: "[idea | openspec/explorations/<file>.md]"
metadata:
  shared:
    - next-step.md
---

# os-explore

A thinking companion. You read code, specs and existing changes; you don't
write production code and you don't run `openspec new change` unless the
user explicitly approves it first.

Before step 1, read `next-step.md`.

## 1. Classify out loud

Before your first question, read enough of the repo and existing
`openspec/changes/` and `openspec/specs/` to classify the request with one
of these labels, written exactly like this:

| Label | When | Recommended skill |
|---|---|---|
| `spike` | a viability doubt that needs a throwaway experiment, not a design decision | reclassify once the doubt is answered |
| `scoped` | modifies a flow that already exists in the repo and fits in one session | `/os-propose` |
| `ambiguous` | fits in one change but has open, high-impact design decisions | `/os-propose-drill` |
| `large` | doesn't fit in one session, or chains several unresolved decisions | `/os-wayfind` |

Say the label and your reasoning. If the user corrects it, keep exploring
under the corrected label.

## 2. Explore

Read code, specs, and related changes. For a `spike`, build the minimal
prototype needed to answer the doubt — in a temp directory or a throwaway
branch, never in production code — and delete it once answered; only the
finding survives, in the exploration file.

If the user suggests starting to write code: summarize what you'd do and
name the label's recommended skill instead of implementing.

## 3. Write the exploration file

Always write the exploration file (template: `EXPLORATION-TEMPLATE.md`):

- If invoked with a path under `openspec/explorations/`, update that file.
- Otherwise create `openspec/explorations/<YYYY-MM-DD>-<topic>.md`, with
  `<topic>` a short kebab-case slug. If that file already exists, add `-2`,
  `-3`… (`2026-09-16-export-2.md`) until the name is free.
- Never pick an existing file because its topic looks similar.

Fill every section of the template: classification (and any correction),
facts with `file:line`, web sources with their conclusion, leaning
decisions with why, open questions, recommended skill, next step. The file
is permanent: archiving a change never moves or deletes it.

## 4. Close

Whether the exploration finishes or the user interrupts it, make sure every
template section is filled in (or explicitly marked empty), then end with
`Next: /os-<skill> <exploration path>` for the recommended skill.
