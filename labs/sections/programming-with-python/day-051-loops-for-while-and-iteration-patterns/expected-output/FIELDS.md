# Expected output — Day 051 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14.0, 2026-07-13). Your numbers will match
exactly, because the program is deterministic — the same input always
produces the same output on every platform where Python 3 runs.

## Files

- `sample-run.txt` — the reference program run on the `demo` command and on
  each pattern with numbers piped in on standard input, plus one bad-input
  case and the `python3 -c` import check.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (15 checks, 0 failures).

## Required behaviour on every platform

A correct program must, for these inputs, produce exactly:

| Command (stdin in quotes) | Standard output | Exit code |
| ------------------------- | --------------- | --------- |
| `patterns.py demo` (no stdin) | five-pattern report; `total    -> count=8 sum=31` etc. | 0 |
| `"3 1 4 1 5 9 2 6"` → `total` | `count=8 sum=31` | 0 |
| `"3 1 4 1 5 9 2 6"` → `filter 4` | `[5, 9, 6]` | 0 |
| `"3 1 4 1 5 9 2 6"` → `transform` | `[9, 1, 16, 1, 25, 81, 4, 36]` | 0 |
| `"3 1 4 1 5 9 2 6"` → `search 5` | `found 5 at index 4 after 5 comparisons` | 0 |
| `"3 1 4 1 5 9 2 6"` → `search 7` | `7 not found after 8 comparisons` | 1 |
| `"1 2 2 3 3 3"` → `histogram` | `1 | #` / `2 | ##` / `3 | ###` | 0 |
| `"1 x 3"` → `total` | (stderr) `error: 'x' is not a whole number` | 1 |
| `"1 2 3"` → `frobnicate` | (stderr) `error: unknown command 'frobnicate'` | 1 |
| `"1 2 3"` → `filter` (no threshold) | (stderr) `error: filter needs one threshold, ...` | 1 |

Two details make this deterministic and testable:

- **Input comes from standard input (or the built-in `demo` sample), not an
  interactive prompt.** That is why the tests can pipe data with `echo` and
  never hang waiting for a human.
- **The found and not-found search cases exit with different codes (0 vs 1),**
  so another program can tell whether the value was present without parsing
  the text.

The only platform difference is the shell prompt (`$`) shown before each
command; the program's own output is identical everywhere Python 3 runs. On
Windows, run inside WSL, or substitute `python` for `python3` if that is how
Python is exposed.

## Test-suite counts

- With the starter unfinished: `15 checks, 0 failure(s).`
- Once you complete all five starter exercises: `24 checks, 0 failure(s).`
  (the ten extra checks run your finished starter through the same
  good/bad inputs as the reference, plus a check that it has the main guard).
