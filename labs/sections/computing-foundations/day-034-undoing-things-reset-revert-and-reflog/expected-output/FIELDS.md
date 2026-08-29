# Expected output — Day 034 lab

`sample-run.txt` in this directory is a **real captured run** of
`examples/undo_recover.sh` on macOS (Apple Silicon, git 2.50.1, 2026-07-12).

## What every correct run must show, in order

1. Section `1. Build a small history` — a three-commit log (`Frist commit`,
   `Second commit`, `Third commit`).
2. Section `2. git commit --amend fixes the last message` — the HEAD subject
   changes from `Third commit` to `Third commit (message fixed)`.
3. Section `3. git restore --staged un-stages a file` — `scratch.txt` moves
   from staged (`A  scratch.txt`) to untracked (`?? scratch.txt`).
4. Section `4. git restore discards a working-tree change` — the unwanted last
   line disappears; `notes.txt`'s last line returns to `step three`.
5. Section `5. git reset --soft ...` — the change stays staged (`M  notes.txt`)
   after the soft reset, then is re-committed.
6. Section `6. git revert ...` — a new commit whose subject begins with
   `Revert "..."` appears above the original.
7. Section `7. DISASTER ...` — commit count drops from `4` to `2` after
   `git reset --hard HEAD~2`.
8. Section `8. RECOVER with git reflog` — the reflog lists the pre-disaster
   commit, and after recovery the commit count returns to `4`.
9. Final line: `SUCCESS: recovered 4 commits — nothing was truly lost.`

## Values that will differ on your machine

- **Commit hashes** (short SHAs like `a6ed65f`) are computed from content,
  author, and timestamp, so every run produces different hashes. Only the
  *structure* — subjects, counts, and the recovery — is fixed.
- **Timestamps** in the revert commit's `Date:` line reflect when you run it.

## Platform differences

The commands are identical on macOS and Linux; only `mktemp`'s temp path
differs (honoured by the `${TMPDIR:-/tmp}` default in the scripts). On Windows,
run inside WSL or Git Bash. Output shape is otherwise the same everywhere.
