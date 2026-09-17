# Implementation mode

Contract shared by every `os-*` skill that needs to know whether a change is
`tdd` or `standard`.

1. Read `openspec/changes/<name>/proposal.md`.
2. Grep it **literally** for a line matching `Implementation: tdd` or
   `Implementation: standard`. Do not infer the mode from prose elsewhere in
   the file — only that literal line counts.
3. If the line is missing, ask with `AskUserQuestion`:
   `proposal.md has no "Implementation:" line — which mode is this change?`,
   options `standard` and `tdd`. Use the answer as the mode for this
   session — don't guess it.
