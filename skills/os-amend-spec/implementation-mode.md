# Implementation mode

Contract shared by every `os-*` skill that needs to know whether a change is
`tdd` or `standard`.

1. Read `openspec/changes/<name>/proposal.md`.
2. Grep it **literally** for a line matching `Implementation: tdd` or
   `Implementation: standard`. Do not infer the mode from prose elsewhere in
   the file — only that literal line counts.
3. If the line is missing, assume `standard` and tell the user:
   `proposal.md has no "Implementation:" line — assuming standard.`
4. If a skill built for one mode is invoked against a change declared in the
   other mode (`os-apply` on a `tdd` change, `os-apply-tdd` on a `standard`
   one), warn and name the matching skill, then only continue if the user
   confirms. Never switch mode silently.
