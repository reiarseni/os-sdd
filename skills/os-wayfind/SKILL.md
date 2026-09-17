---
name: os-wayfind
description: Use when work doesn't fit in one session or one change — chains several unresolved decisions. Maintains a local map at openspec/maps/<name>.md, resolving one open decision per invocation, and hands finished stretches to os-propose. Never implements.
disable-model-invocation: true
argument-hint: "[map name]"
metadata:
  shared:
    - next-step.md
---

# os-wayfind

A local map of decisions for work too large for a single OpenSpec change.
Purely planning — this skill never writes production code.

Before step 1, read `next-step.md`.

## 1. Find or create the map

If `openspec/maps/<name>.md` doesn't exist yet, agree on the destination's
name with the user and create it (template: `MAP-TEMPLATE.md`) with the
decisions you can already see.

## 2. Compute the frontier

The frontier is every **open decision** whose `Blocked by:` list is empty or
fully resolved. If the user asks to resolve a decision that's still blocked,
say so and offer one from the frontier instead.

## 3. Resolve one decision

Pick one decision from the frontier (the user's choice if they named one and
it's in the frontier). Interview them about just that decision. Once
resolved:

- Add a one-line entry to **Decisions so far**.
- Put the detail (what was decided, why, alternatives considered) in that
  decision's block.
- Remove it from **Open decisions**.

Resolve exactly one decision per invocation, even if the next one is now
unblocked.

## 4. Stretch ready?

A "stretch" is a coherent slice of the destination whose decisions are all
resolved. When one has no open decisions left, don't implement it —
recommend `/os-propose <map>#<stretch>`. Once the user creates the change,
link `openspec/changes/<change>` from that stretch in the map.

## 5. Close

End with either:
- `Next: /os-wayfind <name>` if there's still frontier to resolve, or
- `Next: /os-propose <map>#<stretch>` if a stretch just became ready.
