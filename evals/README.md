# Manual behavior evals

One case per behavior fix that unit tests can't catch, because the failure
is in how the model reads a skill. Run each case by hand in a clean session
(a fresh `claude -p` process, as in the case's commands) and record the
outcome under **Last run** in the case file. These are not part of
`python3 -m unittest`.

Each case has: setup commands, the exact prompt, an observable pass
criterion (a command whose output decides it) and the last run's result.

| Case | Behavior |
|---|---|
| `a1-task-brief-id.md` | `os-apply` passes the task id `X.Y` to `task_brief.py` |
| `a2-handoff-without-change.md` | `os-handoff` with no active change updates the exploration |
| `a3-explore-not-auto.md` | `os-explore` doesn't trigger on a plain question about the code |

`OS_SDD` below is the absolute path of this repository.
