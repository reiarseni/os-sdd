---
name: os-wayfind
description: Use when work doesn't fit in one session or one change — chains several unresolved decisions. Maintains a local map at openspec/maps/<name>.md, resolving one open decision per invocation, and hands finished stretches to os-propose. Never implements.
disable-model-invocation: true
argument-hint: "[map name]"
metadata:
  shared:
    - interview.md
    - session-options.md
    - next-step.md
---

# os-wayfind

A local map of decisions for work too large for a single OpenSpec change.
Purely planning — this skill never writes production code.

Before step 1, read `interview.md`, `session-options.md` and `next-step.md`.

## 1. Find or create the map

If `openspec/maps/<name>.md` doesn't exist yet, agree on the destination's
name with the user and create it (template: `MAP-TEMPLATE.md`) with the
decisions you can already see.

If it exists, bring it up to date before anything else:

- No `Status:` line under the title → add `Status: open`.
- A stretch whose `Decisions:` line has unquoted summaries → rewrite it
  with the quoted titles of the matching `### <decision>` blocks when each
  summary matches exactly one block. If any summary matches several blocks
  or none, ask the user which block it means and leave that line as it is
  until they answer.
- A stretch with `Change: none yet` → search for its
  `Map: openspec/maps/<name>.md#<stretch>` line in
  `openspec/changes/*/proposal.md` and
  `openspec/changes/archive/*/proposal.md`, and fill in the path of every
  change that has it, comma-separated.
- A `Change:` path that no longer exists → rewrite it with the path the
  change was archived under, `openspec/changes/archive/<date>-<change>`.

## 2. Compute the frontier

The frontier is every **open decision** whose `Blocked by:` list is empty or
fully resolved. If the user asks to resolve a decision that's still blocked,
say so and offer one from the frontier instead.

If there are open decisions but the frontier is empty, their `Blocked by:`
lists form a cycle: name the decisions that block each other and ask with
AskUserQuestion which block to remove. Then carry on with the new frontier
in this same invocation.

## 3. Resolve one decision

Ask the web research question from `session-options.md` first. Pick one
decision from the frontier (the user's choice if they named one and it's in
the frontier) and interview them about just that decision, following
"Tool", "Round summary" and "Research" in `interview.md`, with no round
limit.

When the interview reaches an answer, propose the decision's block — what
was decided, why, alternatives considered. It is resolved only once the
user confirms that block; until then the map doesn't change. Once
confirmed:

- Add a one-line entry to **Decisions so far**.
- Put the confirmed detail in that decision's block.
- Remove it from **Open decisions**.
- Apply "Fog and scope" below.

Resolve exactly one decision per invocation, even if the next one is now
unblocked.

## Fog and scope

After each resolution, walk **Not yet specified**:

- An entry you can now phrase as a precise question (not necessarily
  answer) → move it to **Open decisions** with its `Blocked by:`.
- An entry the resolution made moot — it raises no question and is not
  outside the destination → remove it and note it as dissolved in one line
  of the resolving decision's block. It doesn't go to **Out of scope**.

Taking something out of scope changes the destination, so propose it with
AskUserQuestion and move it to **Out of scope** only if the user confirms,
with one line saying what it is and why it's out. Nothing in **Out of
scope** ever returns to **Open decisions** or **Not yet specified**.

## 4. Stretch ready?

A "stretch" is a coherent slice of the destination whose decisions are all
resolved. When one has no open decisions left, add it to `## Stretches`
with `Decisions:` quoting the exact titles of its decision blocks
(`Decisions: "<decision 1>", "<decision 2>"`) and `Change: none yet` —
don't implement it.

## 5. Close

The map is complete when **Open decisions** and **Not yet specified** are
empty, every block in **Decisions so far** is quoted in some stretch's
`Decisions:` line, and no stretch says `Change: none yet`. If a resolved
decision is in no stretch, ask with AskUserQuestion which stretch it
belongs to or whether it opens a new one; the map isn't complete until
that's settled. While any condition is missing, keep `Status: open`.

End with, in this order of priority:

1. `Next: /os-propose openspec/maps/<name>.md#<stretch>` if a stretch just
   became ready or still says `Change: none yet` — the first one in map
   order if there are several.
2. `Next: /os-wayfind <name>` if there's still frontier to resolve.
3. If the map is complete: set `Status: complete` and end without a
   `Next:` line.
