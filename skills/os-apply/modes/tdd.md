# TDD mode

Vertical slices — one scenario at a time, red for the right reason, then the
minimum code to go green — in the seams `design.md` declares. Adapted from
Matt Pocock's `tdd`/`implement` and Superpowers' `test-driven-development`.

## Implement and evidence

For each scenario in the task's brief, follow "One scenario, one slice"
below, or "Manual scenarios" below if its seam is `manual:`. If the brief
says the seam is not declared, see "Undeclared seams" below.

**Evidence**: the red→green transcript (or the manual verification's
result) for every scenario of the task.

## One scenario, one slice

A seam is defined in "Seams (tdd only)" in `proposal-templates.md`. Don't
write all the tests for a task up front. Take the scenario in front of you,
in its declared seam, and:

1. **Write one test** for that scenario, calling the seam's real interface
   (never a mock of the code you're about to write).
2. **Run it and watch it fail for the expected reason** — e.g. "function
   doesn't exist" or "returns X, expected Y", not a typo or import error.
   If it fails for the wrong reason, fix the test/setup before writing any
   implementation.
3. **If the test passes immediately**: either the test is invalid (doesn't
   exercise the new behavior — fix it and re-run red) or the behavior
   already exists (verify that, then record the passing run as evidence —
   no implementation needed).
4. **Write the minimum implementation** to make that one test pass — not the
   general solution to every scenario in the task.
5. **Run it and confirm green.**
6. Move to the next scenario in the task and repeat.

## Manual scenarios

A scenario whose seam is `manual: <verification>` in `## Seams` skips the
cycle. Run the verification named there and cite its actual result
(command + output, or the concrete steps taken and what was observed) as
that scenario's evidence.

## Undeclared seams

If a scenario needs an interface that isn't in `## Seams`, stop before
writing the test: don't invent a seam. End with
`Next: /os-review <name>` so the seam gets declared in `design.md`.
