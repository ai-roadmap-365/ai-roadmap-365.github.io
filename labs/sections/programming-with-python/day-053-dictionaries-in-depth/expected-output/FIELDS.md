# Expected output — Day 053 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14, 2026-07-13). Your numbers will match
exactly, because the program is deterministic — the same input always
produces the same output on every platform.

## Files

- `sample-run.txt` — the reference program run on several inputs (counting,
  records, a bad-input error) plus the `python3 -c` import check.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (12 checks, 0 failures).

## Required behaviour on every platform

A correct program must, for these inputs, produce exactly:

| Command | Standard output | Exit code |
| ------- | --------------- | --------- |
| `wordstats.py "a a b"` | `a: 2` / `b: 1` / `most common: a (2)` | 0 |
| `wordstats.py "the cat sat on the mat the cat"` | `the: 3` first (insertion order), then `cat: 2`, `sat: 1`, `on: 1`, `mat: 1`, `most common: the (3)` | 0 |
| `wordstats.py --records` | `engineers: ['Ada', 'Alan']` / `admirals: ['Grace']` / `names A-M: ['Ada', 'Alan', 'Grace']` | 0 |
| `wordstats.py` (no argument) | (stderr) `error: expected text to count, or --records` | 1 |

Two details are load-bearing and identical on every platform:

- **Insertion order.** Counts print in the order each word first appeared,
  not alphabetically — this is the Python 3.7+ guarantee. `the` prints before
  `cat` because it was seen first.
- **Tie-breaking.** `most common` breaks ties in favour of the word seen
  first, because the ranking uses a strictly-greater comparison.

The only platform difference is the shell prompt shown before each command
(`$` here); the program's own output is identical everywhere Python 3.7+ runs.

## Test-suite counts

- With the starter unfinished: `12 checks, 0 failure(s).`
- Once you complete all four starter exercises: `18 checks, 0 failure(s).`
  (the six extra checks run your starter through the same counting and records
  inputs as the reference, plus a check that it has the main guard).
