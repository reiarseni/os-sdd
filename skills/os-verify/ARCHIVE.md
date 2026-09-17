# Archive step

If the user confirms they want to archive:

1. Delete `openspec/changes/<name>/HANDOFF.md` if it exists — **before**
   archiving, since `openspec archive` moves the whole change directory and
   a stale handoff has no value once archived.
2. Run `openspec archive <name>`.
3. Show the command's result to the user.

If the user declines, leave the change as-is: `VERIFY.md` with `PASS` stays.
