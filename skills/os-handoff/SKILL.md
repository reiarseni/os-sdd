---
name: os-handoff
description: Use when a session is ending and the next one (or a different agent) needs to pick up a change or exploration without re-deriving context — rewrites HANDOFF.md entirely, or the exploration file's Next step if there's no change.
disable-model-invocation: true
argument-hint: "[change] [focus for the next session]"
metadata:
  shared:
    - next-step.md
---

# os-handoff

Rewrites the handoff document **entirely** — never appends — so the next
session gets a current picture instead of an accumulating log.

Before step 1, read `next-step.md`.

## 1. Find what to hand off

Pick the target with the first rule that applies, in this order:

1. A change named in the argument (a word matching an active change in
   `openspec list --json`).
2. A change the user mentioned in this conversation.
3. The only active change in `openspec list --json`.
4. The exploration file under `openspec/explorations/` this session worked
   in.
5. The map under `openspec/maps/` this session worked in, if no exploration
   applies either.
6. Otherwise (several active changes and no context, or nothing else
   applies): ask the user to pick with AskUserQuestion before writing
   anything.

A change goes to `openspec/changes/<name>/HANDOFF.md`. An exploration gets
its `Next step` section updated instead — never create `HANDOFF.md` for it.
A map gets its `## Notes` section updated the same way — append what the
next session needs (the frontier decision in progress, anything learned
about a blocked one), never create `HANDOFF.md` for it either. Having no
active change is not a reason to stop.

## 2. Focus

Whatever the argument says besides the change name is the focus for the
next session: put it first in the document, stated as a concrete action.

## 3. Write

For a change, rewrite `openspec/changes/<name>/HANDOFF.md` from scratch
with:

- **State**: phase, which tasks are done vs. pending.
- **Next step**: one concrete action, not a vague pointer.
- **Session decisions**: anything decided this session that isn't already
  in an artifact (if it is, reference the file and section instead).
- **Traps**: anything the next session would otherwise rediscover the hard
  way (a flaky test, a gotcha in a dependency, a false start).
- **Suggested skills**: which `os-*` skill(s) make sense next.

Reference artifacts and files by path — never copy their content. Redact
secrets and personal data (API keys, tokens, real emails/names from logs):
describe them ("the .env value that was wrong") instead of pasting them.

For an exploration, write the same content into its `Next step` section
only; leave its other sections untouched. For a map, write it into `## Notes`
as a dated entry; leave its other sections untouched.

## 4. Close

End with the `Next:` line for whichever skill the state points to (e.g.
`Next: /os-apply <name>`).
