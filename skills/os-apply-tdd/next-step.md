# Next step

Contract shared by every `os-*` skill.

- End the skill's **final** message with a single line:
  `Next: /os-<skill> <arg>` naming the one recommended next command and its
  argument (change name, exploration path, or map path). Intermediate
  messages — interview rounds, confirmation questions, progress updates —
  never carry a `Next:` line.
- This line is a **recommendation**, never an action. No skill invokes
  another skill, via the Skill tool or otherwise — the user decides whether
  to run it.
- If nothing follows (e.g. the user stopped mid-exploration with no
  classification yet, or explicitly said they're done), omit the line rather
  than invent a next step.
