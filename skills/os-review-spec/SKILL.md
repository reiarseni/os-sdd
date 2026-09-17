---
name: os-review-spec
description: Use when a change's artifacts are ready and need adversarial review before implementing — checks proposal.md, design.md, delta specs and tasks.md for coherence, scenario coverage, implementation mode/seams and unjustified decisions. Not for reviewing the implementation itself; use os-verify for that.
disable-model-invocation: true
argument-hint: "[change]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - next-step.md
---

# os-review-spec

Adversarial review of a change's **artifacts**, before implementation
starts. Implementation fidelity is `/os-verify`'s job.

Before step 1, read `select-change.md`, `implementation-mode.md` and
`next-step.md`.

## 1. Select the change

Apply `select-change.md`.

## 2. Scope check

If the change already has tasks marked `- [x]`, review only the artifacts
and tell the user that implementation fidelity is `/os-verify`'s job.

## 3. Read

`openspec/changes/<name>/proposal.md`, `design.md`, every delta spec under
`specs/`, and `tasks.md`. Determine the mode with `implementation-mode.md`.

## 4. Check

- **Coherence across artifacts**: does `design.md` actually address what
  `proposal.md` promises? Do the delta specs match the decisions in
  `design.md`?
- **Scenario coverage**: every `#### Scenario:` in every delta spec must
  appear in at least one task's `— covers:` suffix. Any scenario missing
  from `tasks.md` is a **blocking** finding.
- **Mode and seams**: if the mode is `tdd`, `design.md` must have a
  `## Seams` section. Missing it is a **blocking** finding. If present,
  check every scenario appears in the seams table exactly once (as a seam
  or as `manual:`).
- **Open Questions**: anything in `design.md`'s Open Questions is a **risk**
  finding, not blocking — but it should be visible before implementation.
- **Edge cases and unjustified decisions**: decisions in `design.md` with no
  stated alternative or rationale, and edge cases that didn't make it into
  a scenario.

## 5. Report and offer to fix

Present findings grouped by severity (blocking / risk / nit). For each,
name the file and what's missing or inconsistent. Offer to fix the
artifacts directly — if the user accepts, edit them and re-run step 4's
checks until clean.

## 6. Close

If there were no blocking findings (or they're now fixed), end with
`Next: /os-apply <name>` or `Next: /os-apply-tdd <name>` depending on the
mode. If tasks were already done (step 2), end with
`Next: /os-verify <name>` instead.
