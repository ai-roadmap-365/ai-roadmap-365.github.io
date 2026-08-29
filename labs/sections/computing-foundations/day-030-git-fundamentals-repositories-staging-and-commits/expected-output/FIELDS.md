# What to expect in the output (all platforms)

`sample-run.txt` in this directory is a **real captured run** of
`examples/git_basics.sh` (macOS, Git 2.50.1, 2026-07-12). The same script
produces the same *shape* on any Linux with Git installed.

## Lines that are identical every run

- The eight `----- N. ... -----` step banners, in order.
- `?? notes.txt` — the untracked file in step 2.
- `A  notes.txt` — the staged file in step 3 (note the two spaces after `A`).
- ` M notes.txt` — the modified-but-unstaged file in step 5 (leading space).
- The `git diff` hunk showing one context line and one added line
  (`+a second line, added later`).
- In step 7, `git status --short` prints **nothing** for `secret.key`; the
  `check-ignore` line reads `.gitignore:1:secret.key	secret.key`.
- `git log --oneline` lists the three commit subjects, newest first.
- The summary reports `Commits in history: 3`.

## Lines that legitimately differ between runs

- **Commit hashes.** The short hashes (e.g. `b4b4836`) are computed from the
  snapshot content **plus the commit timestamp and author**, so every run
  produces different hashes. That is correct and expected — it is the whole
  point of a content-addressed history. Two learners will never share a hash.
- **The `index` line inside the diff** (`index 841d9f2..47a4a5f`) references
  blob hashes, which are stable for identical content — you should see the
  same short blob ids because the file bytes are the same, but do not rely on
  them.
- **The temp-directory path** in the final line (`.gitdemo.XXXXXX`) has a
  random suffix and is deleted immediately after.

No field should ever show `secret.key` in a `git status`; if it does, the
`.gitignore` step did not work — see `troubleshooting.md`.
