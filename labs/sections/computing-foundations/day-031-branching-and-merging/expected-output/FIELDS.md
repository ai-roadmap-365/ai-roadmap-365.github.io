# Expected output — what is fixed and what varies

`sample-run.txt` in this directory is a **real captured run** of
`examples/branch_merge.sh` (macOS, git 2.50.1, 2026-07-12). Because git makes
new commits and a new temporary directory every time, two things change on
every run and are **not** errors:

- **The workspace path** on the `Workspace:` line (a random `mktemp` name such
  as `/var/folders/.../day031-branch-merge.XXXXXX` on macOS or
  `/tmp/day031-branch-merge.XXXXXX` on Linux).
- **The seven-character commit hashes** (`493ba6c`, `84e0a3a`, …). Git derives
  each hash from the commit's content, author, and timestamp, so yours will
  differ. Their **relationships** are what matter, not their values.

Everything else must appear, in this order, on every platform:

1. `=== Branch, Conflict, Merge ===`
2. Step 1: the base commit line `<hash> Add base pancake recipe`
3. Step 2: `feature-blueberries now says:` then `milk: 2 cups`
4. Step 3: `main now says:` then `milk: 1 cup buttermilk`
5. Step 4: git's own conflict report —
   `CONFLICT (content): Merge conflict in recipe.txt`,
   `UU recipe.txt`, and the three marker lines
   `<<<<<<< HEAD`, `=======`, `>>>>>>> feature-blueberries`
6. Step 5: the resolved file with `milk: 2 cups buttermilk` and **no markers**
7. Step 6: a `git log --graph` diamond — a `Merge branch 'feature-blueberries'`
   node above a `|\` split that rejoins at `|/`
8. Step 7: `Fast-forward` and a linear graph with the new commit on top
9. `=== Done. Temporary repository will be deleted on exit. ===`

## Platform differences

- **macOS** temp paths live under `/var/folders/...`; **Linux** under `/tmp`.
  The script uses `${TMPDIR:-/tmp}`, so both are handled automatically.
- Some git versions phrase the fast-forward and merge lines slightly
  differently (e.g. `Merge made by the 'ort' strategy`). The shape — a
  conflict that is resolved into a two-parent merge commit, plus a separate
  fast-forward — is identical.
- Git 2.23+ is assumed for `git switch`. On older git, `git checkout -b` and
  `git checkout <branch>` do the same thing; see `troubleshooting.md`.
