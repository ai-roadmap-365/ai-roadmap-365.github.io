# Required output fields (all platforms)

A correct run of `toolkit_check.sh` prints, in order:

1. `=== Computing Foundations Toolkit Check ===`
2. `Generated on: YYYY-MM-DD`
3. `Operating system kernel: Darwin` (macOS) or `Linux`
4. `-- Tool inventory --`
5. Six tool lines, each `[ok]` or `[--]`, for: `shell`, `git`, `curl`,
   `python3`, `sqlite3`, `editor` — every line names the Course 1 day it
   maps to (contains `maps to Day`).
6. `-- Skill checks --`
7. Three skill lines, each `[ok]` or `[--]`:
   `git init + commit works`, `shell pipeline works`, `sqlite query works`.
8. `-- Readiness --`
9. `Tools present: <n> / 6   Skills passed: <n> / 3`
10. A verdict line: `You are ready for Course 2. ...` when git, the
    pipeline, and python3 are all present, otherwise the "Almost there" line.
11. `=== End of check ===`

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, 2026-07-12) where all six tools are present and all three skills
pass. `tests-macos.txt` is the captured test run (`22 checks, 0 failure(s).`).

## Platform differences

- **Linux** output has the same shape; the kernel line reads `Linux`, the
  `shell` line usually shows `/bin/bash`, and the `python3`/`sqlite3`
  versions differ. All six tools are present on a standard developer install.
- **Missing tool** (any platform): its line reads `[--] <tool> : not found —
  <install day>` instead of `[ok]`, the readiness counts drop accordingly,
  and — if git, the pipeline, or python3 is the missing piece — the verdict
  becomes the "Almost there" line. The script never crashes on a missing
  tool; that graceful degradation is the point.
