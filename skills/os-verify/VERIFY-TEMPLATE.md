# VERIFY.md template

Written to `openspec/changes/<name>/VERIFY.md`. The header lines are
machine-read on the next run — keep them literal.

```
Verdict: PASS
Date: <YYYY-MM-DD>
Fingerprint: <sha256 printed by the fingerprint script>
Commands: <suite command> | <lint command> | <typecheck command>

## Cheap checks

$ <suite command>
<tail of output>
exit 0

$ <lint command>
<tail of output>
exit 0

## Scenario → evidence

| Scenario | Evidence |
|---|---|
| data-export/Export to CSV | tests/test_export.py::test_writes_csv_rows |
| data-export/Accented characters survive export | manual: opened out.csv in a spreadsheet app, accents shown correctly |

## Findings

None.
```

For a `BLOCK` verdict, use `Verdict: BLOCK`, keep `Fingerprint` (still
computed — it's just not a valid PASS to reuse) and replace `## Findings`
with the blocking items, one per line, each naming what's missing and where
(a scenario with no evidence, a failing command with its real output, a
quality risk that should be fixed before archiving).
