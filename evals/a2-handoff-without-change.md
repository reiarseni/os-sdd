# A2 — `os-handoff` with no active change updates the exploration

`openspec list --json` returns no changes; the session worked on an
exploration. The skill must not stop for lack of a change, must not create
`HANDOFF.md`, and must rewrite the exploration's `Next step`.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes openspec/explorations
cat > export.py <<'PY'
def export(rows, path):
    with open(path, "w") as f:
        for row in rows:
            f.write(",".join(row) + "\n")
PY
cat > openspec/explorations/2026-09-16-export.md <<'MD'
# export

Date: 2026-09-16

## Classification

scoped — changes the existing export function in export.py

## Facts

- rows are joined with a comma — `export.py:4`

## Web sources

- none

## Leaning decisions

- quote fields that contain the delimiter — avoids broken rows

## Open questions

- which delimiter should be the default?

## Recommended skill

/os-propose

## Next step

SENTINEL-NOT-UPDATED
MD
```

## Prompt

Two turns in the same session: the first puts the exploration in context,
the second is the handoff.

```bash
claude -p "Read openspec/explorations/2026-09-16-export.md and export.py; we are exploring whether to quote CSV fields. Don't write anything yet." \
  --allowedTools "Read" > a2-turn1.txt
claude -c -p "/os-handoff next session: decide the default CSV delimiter" \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" "Bash(openspec list:*)" > a2.jsonl
```

## Pass criterion

```bash
find . -name HANDOFF.md
grep -c SENTINEL-NOT-UPDATED openspec/explorations/2026-09-16-export.md
sed -n '/^## Next step/,$p' openspec/explorations/2026-09-16-export.md
```

Passes if `find` prints nothing, `grep -c` prints `0` and the `Next step`
section mentions the delimiter.

## Last run

2026-09-16, Claude Code 2.1.273 — **PASS**. `find` printed nothing, `grep -c`
printed `0`, and `Next step` opens with "Focus: decide the default CSV
delimiter". An earlier run without `Read` in `--allowedTools` couldn't read
the skill's `next-step.md` and stopped before writing; the case now allows
`Read`.
