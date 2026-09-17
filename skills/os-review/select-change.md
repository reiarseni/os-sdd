# Select change

Contract shared by every `os-*` skill that acts on an existing OpenSpec
change.

1. If the skill was invoked with a change name, use it directly.
2. Otherwise, infer it from the conversation if the user just mentioned one.
3. Otherwise, run `openspec list --json` and:
   - If exactly one active change exists, use it.
   - If several exist, use **AskUserQuestion** to let the user pick one.
   - If none exist, say so and stop — do not invent a change.

Never guess a change name that doesn't appear in `openspec list --json`.
