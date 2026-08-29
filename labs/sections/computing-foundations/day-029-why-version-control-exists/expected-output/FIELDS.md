# Expected output — what is stable, what varies

`sample-run.txt` in this directory is a real captured run of
`examples/history_demo.sh` (macOS, Apple Silicon, git 2.50.1, 2026-07-12).
A correct run on any platform prints, in order:

1. `=== Version control history demo ===`
2. `Creating a throwaway repository in a temporary directory...`
3. `(temporary directory: <path>)` — **the path varies** by machine and run.
4. `Made commit 1: Start notes with a first point`
5. `Made commit 2: Expand the notes with a second point`
6. `Made commit 3: Add a closing line to the notes`
7. `--- git log --oneline (newest first) ---` followed by **three** commit
   lines, newest first. **The short commit ids vary** — a commit's hash is
   computed from its content, author, and time, so they differ every run.
8. `--- git diff between commit 1 and commit 2 (notes.txt) ---` followed by
   `+Point two: every commit records who, when, and why.`
9. `--- git show of commit 2 ---` followed by the author and message.
10. `--- Time machine: restoring notes.txt to commit 1 ---` and
    `Point one: version control keeps history.`
11. `Cleaning up the temporary repository...` and `Done. Nothing left behind.`

## Platform notes

- **Commit ids differ every run** on every platform — this is expected and
  correct, not a failure. The messages and structure are what stay fixed.
- **The temporary path differs** by OS: macOS puts it under a long
  `/var/folders/...` path; Linux typically uses `/tmp`. The script honors
  `$TMPDIR` if set.
- **`git restore` vs `git checkout`.** The script prefers `git restore`
  (git 2.23 and newer). On an older git it automatically falls back to
  `git checkout <commit> -- notes.txt`; the printed result is identical.
- No field depends on network access; the whole demo is local.
