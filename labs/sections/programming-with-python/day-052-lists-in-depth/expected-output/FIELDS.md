# Expected output — Day 052 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14.0, 2026-07-13). Your numbers will match
exactly, because the toolkit is deterministic — the same input always
produces the same output on every platform.

## Files

- `sample-run.txt` — the reference program's demo pipeline, plus two
  `python3 -c` import checks calling `dedupe` and `flatten`.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (13 checks, 0 failures). The repository path is shown as
  `<repo>` so nothing machine-specific leaks in.

## Required behaviour on every platform

A correct toolkit must, for these inputs, produce exactly:

| Operation | Input | Result |
| --------- | ----- | ------ |
| `top_n(scores, 3)` | `[88, 72, 95, 72, 60, 95, 81]` | `[95, 95, 88]` |
| slice `scores[::2]` | `[88, 72, 95, 72, 60, 95, 81]` | `[88, 95, 60, 81]` |
| slice `scores[-2:]` | `[88, 72, 95, 72, 60, 95, 81]` | `[95, 81]` |
| `sort_by_length(words)` | `['pear','fig','apple','kiwi','plum','fig']` | `['fig','fig','pear','kiwi','plum','apple']` |
| `dedupe(words)` | `['pear','fig','apple','kiwi','plum','fig']` | `['pear','fig','apple','kiwi','plum']` |
| `flatten(matrix)` | `[[1,2,3],[4,5,6]]` | `[1, 2, 3, 4, 5, 6]` |
| `with_appended([10,20,30], 40)` | original stays | `[10, 20, 30]` (unchanged) |

The only platform difference is the shell prompt shown before each command
(`$` here); the program's own output is identical everywhere Python 3 runs.
Python guarantees a stable sort, so `sort_by_length` produces the same order
on every platform and version.

## Test-suite counts

- With the starter unfinished: `13 checks, 0 failure(s).`
- Once you complete all five starter exercises: `20 checks, 0 failure(s).`
  (the eight extra checks run your starter through the same demo pipeline as
  the reference, plus a check that it copies before mutating).
