# B11 — `os-handoff` with maps, `os-wayfind` stretches and `Change:` fill-in

Covers: `os-handoff` with an in-progress exploration updates its `Next
step`; with no active change but an exploration, still writes a handoff
(doesn't stop for lack of a change); with an in-progress map, updates its
`## Notes` instead of creating `HANDOFF.md`; with several active changes and
no context, asks instead of guessing; `os-wayfind` recommends
`/os-propose openspec/maps/<name>.md#<stretch>` once a stretch's decisions
are all resolved; and a change created from a stretch (its `proposal.md`
carries a `Map: openspec/maps/<name>.md#<stretch>` line) gets its `Change:`
field filled in on the map the next time `/os-wayfind` runs.

`OS_SDD` below is the absolute path of this repository.

## Setup — map handoff

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes openspec/maps
cat > openspec/maps/notifications.md <<'MD'
# Notification system overhaul

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

Same map, but with "Delivery guarantees" already resolved and moved to
`## Stretches` as `### Transport and delivery` with `Change: none yet`, plus
an active change whose `proposal.md` has `Map: openspec/maps/notifications.md#Transport and delivery`.

## Prompt — `Change:` fill-in

```bash
claude -p "/os-wayfind notifications" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Write" "Bash" "AskUserQuestion" > b11-fillin.jsonl
```

## Pass criterion

`b11-maphandoff.jsonl`: no `HANDOFF.md` created anywhere, and
`openspec/maps/notifications.md`'s `## Notes` section is no longer "none
yet" and mentions delivery guarantees. `b11-fillin.jsonl`: the map's
`### Transport and delivery` stretch's `Change:` line is filled in with the
real change's path.

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
