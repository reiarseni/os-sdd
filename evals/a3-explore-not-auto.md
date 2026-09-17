# A3 — `os-explore` doesn't trigger on a plain question

A question about the code, without `/os-explore`, must be answered without
loading the skill or writing an exploration file.

## Setup

```bash
OS_SDD=/path/to/os-sdd
EVAL="$(mktemp -d)" && cd "$EVAL" && git init -q
"$OS_SDD/install.sh" "$EVAL"
mkdir -p openspec/specs openspec/changes
cat > export.py <<'PY'
def export(rows, path):
    with open(path, "w") as f:
        for row in rows:
            f.write(",".join(row) + "\n")
PY
```

## Prompt

```bash
claude -p "How does export() in export.py handle a row that contains a comma? I'm thinking about changing it." \
  --output-format stream-json --verbose \
  --permission-mode acceptEdits --allowedTools "Read" > a3.jsonl
```

## Pass criterion

```bash
ls openspec/explorations 2>/dev/null | wc -l
grep -c '"skill":"os-explore"' a3.jsonl
```

Passes if both commands print `0`.

## Last run

2026-09-16, Claude Code 2.1.273 — **PASS**. Both commands printed `0`; the
session answered the question directly (`export.py:4`, no quoting).
