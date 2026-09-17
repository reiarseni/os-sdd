---
name: os-review
description: Use when a change's artifacts are ready and need review before or during implementation — checks proposal.md, design.md, delta specs and tasks.md for coherence, scenario coverage, implementation mode/seams and unjustified decisions, proposes concrete fixes, and marks the change READY or BLOCK on disk. Not for reviewing the implementation itself; use os-verify for that.
disable-model-invocation: true
argument-hint: "[change]"
metadata:
  shared:
    - select-change.md
    - implementation-mode.md
    - session-options.md
    - proposal-templates.md
    - next-step.md
  shared-scripts:
    - fingerprint.py
---

# os-review

Review of a change's **artifacts**, before implementation starts or while
tasks are still pending. Implementation fidelity is `/os-verify`'s job, and
`/os-review` refuses to run once every task is already done.

Before step 1, read `select-change.md`, `implementation-mode.md`, `session-options.md`, `proposal-templates.md` and `next-step.md`.

## 1. Select the change and check scope

Apply `select-change.md`. Then check `tasks.md`:

- **All tasks `- [x]`**: refuse — tell the user this is `/os-verify`'s job
  and stop, without writing `REVIEW.md`.
- **No tasks done yet, or some done**: continue. If some are done, this is
  a mid-implementation review (see step 5).

## 2. Web research question

Ask the "Web research question" from `session-options.md` before reading
the artifacts, if this looks like a review that could benefit from prior
art (a design decision the request seems unsure about, an unfamiliar
library or protocol). Skip asking when the change is small and internal
enough that research wouldn't change anything.

## 3. Read

`openspec/changes/<name>/proposal.md`, `design.md`, every delta spec under
`specs/`, and `tasks.md`. Determine the mode with `implementation-mode.md`.
If `TEAMLEAD.md` exists and has an unprocessed `## Team-lead feedback`
section, read it too (see step 7).

## 4. Check

- **Coherence across artifacts**: does `design.md` actually address what
  `proposal.md` promises? Do the delta specs match the decisions in
  `design.md`?
- **Scenario coverage**: every `#### Scenario:` in every delta spec must
  appear in at least one task's `— covers:` suffix. A scenario missing from
  `tasks.md` is a **blocking** finding.
- **Declared verification**: every task must say how it's verified (see
  "How a task is verified" in `proposal-templates.md`). A task with no
  verification is a **blocking** finding.
- **Mode and seams**: if the mode is `tdd`, `design.md` must have a
  `## Seams` section. Missing it is a **blocking** finding. If present,
  check every scenario appears in the seams table exactly once (as a seam
  or as `manual:`).
- **Open Questions**: anything already in `design.md`'s Open Questions is a
  **risk** finding, not blocking — but it should be visible before
  implementation.
- **Edge cases and unjustified decisions**: decisions in `design.md` with no
  stated alternative or rationale, and edge cases that didn't make it into
  a scenario.
- **Team-lead feedback**, if step 3 found unprocessed feedback: turn each
  point into its own finding, same as any other.

## 5. Turn findings into proposals

For each finding, propose a concrete before/after edit to the artifact that
would resolve it — never just describe the problem. Present all findings in
one **AskUserQuestion** call with `multiSelect: true`, so the user picks
which proposed edits to apply. Group blocking findings first.

- Findings the user **doesn't** select are not silently dropped: a
  **blocking** finding left unselected goes to `REVIEW.md`'s Open Questions
  and forces `Verdict: BLOCK`. A **risk** or **nit** left unselected is just
  noted in `REVIEW.md`'s Notes.
- After applying the selected edits, ask **"¿Cambiar algo más de la spec?"**
  (open-ended). Keep looping edits until the answer is no.
- If everything comes back unselected or "no" and all findings were
  blocking, the change stays `BLOCK` — say so plainly, don't soften it.

## 6. Mid-implementation adjustments

If some tasks were already `- [x]` (step 1): never revert a checked task
to `- [ ]` just because the review changes something nearby. Instead:

- Reopen only the tasks whose `— covers:` scenarios are directly
  invalidated by an applied edit.
- Add new tasks to retire any code the edit invalidates (e.g. a seam that
  no longer exists) — `— covers: none (retirement)` if nothing new is
  covered.
- Leave every other `- [x]` untouched.

## 7. Team-lead round trip

Offer to write or refresh `TEAMLEAD.md` from `TEAMLEAD-TEMPLATE.md`:
summarize the change in plain language, list the decisions most worth a
team lead's attention, and run `openspec show <change> --diff` to fill in
"Implications" with what actually changes on disk. Copy `REVIEW.md`'s Open
Questions into it.

If step 3 found feedback under `## Team-lead feedback` that step 4 already
turned into findings and step 5 already resolved: move that section's
content into a new `## Processed feedback (<date>)` block and regenerate
the rest of `TEAMLEAD.md` from the current state.

## 8. Write REVIEW.md

Always write `openspec/changes/<name>/REVIEW.md` from `REVIEW-TEMPLATE.md`,
even when nothing needed fixing:

- `Verdict: BLOCK` if any blocking finding is unresolved or was rejected;
  `Verdict: READY` otherwise.
- `Fingerprint:` the output of
  `${CLAUDE_SKILL_DIR}/scripts/fingerprint.py --artifacts <name>`, run
  *after* any edits from this review.
- List every finding with its before/after and status.

`REVIEW.md` and `TEAMLEAD.md` are outside both fingerprints (project and
artifacts) — editing them never invalidates a `PASS` or a `READY`.

## 9. Close

If `Verdict: READY`: end with `Next: /os-apply <name>`. If `Verdict: BLOCK`:
end with `Next: /os-review <name>` once the user has had a chance to
resolve the Open Questions — don't recommend applying against a blocked
review.
