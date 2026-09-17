# Manual behavior evals

One case per behavior fix that unit tests can't catch, because the failure
is in how the model reads a skill. Run each case by hand in a clean session
(a fresh `claude -p` process, as in the case's commands) and record the
outcome under **Last run** in the case file. These are not part of
`python3 -m unittest`.

Each case has: setup commands, the exact prompt, an observable pass
criterion (a command whose output decides it) and the last run's result.

**Known constraint**: `AskUserQuestion` is not available in headless
`claude -p` sessions — every skill that calls for it falls back to plain
text and reports the tool as unavailable, and a single non-interactive `-p`
turn always ends at the first such question. A case can verify a question's
content, order and reasoning, but not that the literal tool call fires, and
verifying what happens *after* the user answers needs a scripted multi-turn
`-c -p` conversation (expensive — several of the `b*` cases below flag the
post-answer behavior as not yet covered for exactly this reason).

| Case | Behavior |
|---|---|
| `a1-task-brief-id.md` | `os-apply` passes the task id `X.Y` to `task_brief.py` |
| `a2-handoff-without-change.md` | `os-handoff` with no active change updates the exploration |
| `a3-explore-not-auto.md` | `os-explore` doesn't trigger on a plain question about the code |
| `b1-session-options.md` | The shared web-research question, asked before round 1 |
| `b2-propose-interview.md` | `os-propose`'s deep-style rounds, confirmation before writing |
| `b3-propose-grill.md` | `os-propose-grill`'s frontier grilling, facts vs. decisions |
| `b4-propose-sources.md` | Detecting an overlapping change or an already-covered spec |
| `b5-propose-artifacts.md` | Generated `tdd`/`standard` artifacts, seams, test-first tasks |
| `b6-review-adjustments.md` | `os-review`'s findings, all-tasks-done refusal |
| `b7-review-teamlead.md` | `os-review`'s `TEAMLEAD.md` round trip |
| `b8-explore-options.md` | `os-explore`'s initial web/method/prototype question |
| `b9-apply-review-gate.md` | `os-apply*` warning without a fresh `REVIEW.md` |
| `b10-verify-package.md` | `os-verify`'s evidence package and fidelity subagent |
| `b11-handoff-wayfind.md` | `os-handoff`/`os-wayfind` with maps and stretches |
| `c1-apply-mode-loading.md` | `os-apply` loads only its mode's file, asks when the mode is missing |
| `c2-apply-evidence.md` | `os-apply`'s evidence per mode: standard and tdd, including manual scenarios |
| `c3-next-lines.md` | Single `Next: /os-apply` line from `os-review` and `os-verify` after the merge |

`OS_SDD` below is the absolute path of this repository.
