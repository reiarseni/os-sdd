# B11 — `os-handoff` with maps, `os-wayfind` stretches and `Change:` fill-in

Covers: `os-handoff` with an in-progress exploration updates its `Next
step`; with no active change but an exploration, still writes a handoff
(doesn't stop for lack of a change); with an in-progress map, updates its
`## Notes` instead of creating `HANDOFF.md`; with several active changes and
no context, asks instead of guessing; `os-wayfind` recommends
`/os-propose openspec/maps/<name>.md#<stretch>` once a stretch's decisions
are all resolved; and a change created from a stretch (its `proposal.md`
carries a `Map: openspec/maps/<name>.md#<stretch>` line) gets its `Change:`
field filled in on the map the next time `/os-wayfind` runs — also when
that change is already archived; resolving a decision that makes a fog
entry moot removes it from `## Not yet specified` without touching `## Out
of scope`; a resolved decision in no stretch blocks completion; the map
flips to `Status: complete` with no `Next:` line once every stretch has a
change; and `os-propose` started from a stretch doesn't ask about that
stretch's decisions.

`OS_SDD` below is the absolute path of this repository.

## Setup — map handoff

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes openspec/maps
cat > openspec/maps/notifications.md <<'MD'
# Notification system overhaul

Status: open

## Destination

Replace the polling-based notification system with push.

## Notes

- none yet

## Decisions so far

- Use a message queue, not direct websockets — see "Transport"

### Transport

Decided on a message queue for horizontal scaling. Alternatives: direct
websockets (rejected, doesn't scale past one instance without sticky
sessions).

## Open decisions

### Delivery guarantees

Blocked by: none

At-least-once or at-most-once delivery?

## Stretches

## Not yet specified

- Retry policy for failed deliveries

## Out of scope

- Email digest notifications
MD
git add -A && git commit -q -m init
```

## Prompt — map handoff

```bash
claude -p "/os-handoff notifications focus: decide delivery guarantees next session" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" > b11-maphandoff.jsonl
```

## Setup — stretch → change → `Change:` fill-in

Same map, but with "Delivery guarantees" already resolved (its own
`### Delivery guarantees` block under `## Decisions so far`) and moved to
`## Stretches`:

```
### Transport and delivery

Decisions: "Transport", "Delivery guarantees"
Change: none yet
```

plus an active change whose `proposal.md` has `Map: openspec/maps/notifications.md#Transport and delivery`.

## Prompt — `Change:` fill-in

```bash
claude -p "/os-wayfind notifications" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" "AskUserQuestion" > b11-fillin.jsonl
```

## Setup — archived change

Same as the fill-in setup, but the change lives only under
`openspec/changes/archive/2026-09-20-push-transport/` (its `proposal.md`
keeps the `Map:` line) and nothing under `openspec/changes/` is active.

## Prompt — archived change

Same command as the fill-in prompt, writing to `b11-archived.jsonl`.

## Setup — dissolved fog

The map handoff setup, with `- Sticky sessions for websocket fan-out` added
to `## Not yet specified` next to the retry-policy entry, and a new open
decision:

```
### Fan-out

Blocked by: none

Fan out through the queue's topics, or through a websocket gateway?
```

## Prompt — dissolved fog

```bash
claude -p "/os-wayfind notifications — resolve Fan-out: fan out through the queue's topics, because the queue already scales horizontally; alternative rejected: a websocket gateway (needs sticky sessions). Skip web research. I confirm that block as written." \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" "AskUserQuestion" > b11-fog.jsonl
```

## Setup — orphan decision

The fill-in setup with `Change:` already set to the active change, `##
Open decisions` and `## Not yet specified` both empty, and a third block
`### Retry policy` under `## Decisions so far` that no stretch quotes.

## Prompt — orphan decision

Same command as the fill-in prompt, writing to `b11-orphan.jsonl`.

## Setup — map complete

The orphan setup without the `### Retry policy` block (and without its
line in `## Decisions so far`), and with `Change: none yet` so this run has
to fill it in from the active change.

## Prompt — map complete

Same command as the fill-in prompt, writing to `b11-complete.jsonl`.

## Setup — `os-propose` from a stretch

The fill-in setup without the active change, so the stretch still says
`Change: none yet`.

## Prompt — `os-propose` from a stretch

```bash
claude -p "/os-propose openspec/maps/notifications.md#Transport and delivery" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" "AskUserQuestion" > b11-propose.jsonl
```

## Pass criterion

`b11-maphandoff.jsonl`: no `HANDOFF.md` created anywhere, and
`openspec/maps/notifications.md`'s `## Notes` section is no longer "none
yet" and mentions delivery guarantees. `b11-fillin.jsonl`: the map's
`### Transport and delivery` stretch's `Change:` line is filled in with the
real change's path.

`b11-archived.jsonl`: that `Change:` line holds
`openspec/changes/archive/2026-09-20-push-transport`, and the map gained
nothing else outside `## Stretches`.

`b11-fog.jsonl`: "Fan-out" is gone from `## Open decisions` and has a line
and block in `## Decisions so far`; "Sticky sessions" is gone from `## Not
yet specified` and the `### Fan-out` block mentions it as dissolved; `##
Out of scope` still holds only the email digest line; the retry-policy
entry is either still in `## Not yet specified` or moved to `## Open
decisions` with a `Blocked by:` line, never in both.

`b11-orphan.jsonl`: an `AskUserQuestion` call asks which stretch "Retry
policy" belongs to (or whether it opens a new one), and the map still says
`Status: open`.

`b11-complete.jsonl`: the stretch's `Change:` line holds the active
change's path, the map says `Status: complete`, and the final assistant
message has no `Next:` line.

`b11-propose.jsonl`: no `AskUserQuestion` call (nor plain-text question)
asks about the transport or the delivery guarantee; the new change's
`design.md` lists both decisions with the alternatives from their blocks,
and its `proposal.md` has
`Map: openspec/maps/notifications.md#Transport and delivery`.

## Last run

2026-09-17 — **NOT EXECUTED — session rate limit**. Both setups were
prepared and ready to run, but every `claude -p` invocation is failing with
`api_error_status: 429` ("You've hit your session limit · resets 1:40pm
(America/Havana)") — confirmed again with a trivial `claude -p "say ok"`
check immediately before writing this file. The underlying code changes
(`os-handoff`'s map branch in "Find what to hand off" and "Write";
`os-wayfind`'s `## Stretches` handling and `Change:` search; `MAP-TEMPLATE.md`'s
new `## Stretches` section) pass `tests/lint_skills.py` and don't touch any
existing test file, so nothing here is known-broken, but the actual model
behavior across all four scenarios above is **unverified** by a live run.
Reporting the rate limit as the reason rather than fabricating a transcript.

2026-09-18 — archived change, dissolved fog, orphan decision, map complete
and `os-propose` from a stretch added (change `wayfind-propose-coherence`);
**not run yet**.
