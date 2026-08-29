# Expected output — Day 055 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14, 2026-07-13). Your numbers will match
exactly, because the program is deterministic — the same input always
produces the same output on every platform where Python 3 runs.

## Files

- `sample-run.txt` — the reference program (`python3 examples/pipeline.py`)
  plus the `python3 -c` one-liner that pulls a single record from the reader
  generator with `next()`.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (12 checks, 0 failures). Absolute paths are shown as
  `<repo>`; the runner itself prints no machine paths.

## Required behaviour on every platform

A correct program must produce exactly:

| Line | Value |
| ---- | ----- |
| high scorers (list) | `['ALICE', 'CAROL', 'FRANK']` |
| name -> score (dict) | `{'alice': 88, 'bob': 72, 'carol': 95, 'dave': 60, 'erin': 79, 'frank': 84}` |
| distinct teams (set) | `['design', 'engineering', 'marketing']` (printed sorted, so stable) |
| first 3 ids (itertools) | `[1000, 1001, 1002]` |
| engineering average (lazy pipeline) | `87.3` |
| engineering average (loop baseline) | `87.3` |
| final line | `match: lazy pipeline == loop baseline` |

The engineering average is `(88 + 95 + 79) / 3 = 262 / 3 = 87.333...`, shown
to one decimal place as `87.3`. The two averages are identical by design: the
lazy generator pipeline and the eager loop compute the same quantity, and an
`assert` in the program fails loudly if they ever diverge.

## Notes on non-determinism

- **Sets are unordered.** The distinct-teams line is printed through
  `sorted(...)` precisely so it is stable to compare; comparing the raw
  `set` repr across runs or Python versions is not reliable.
- **Dict order** is insertion order in Python 3.7+, so the `name -> score`
  line is stable across every supported Python.

## Test-suite counts

- With the starter unfinished: `12 checks, 0 failure(s).`
- Once you complete all five starter exercises: still `12 checks, 0
  failure(s).` — the two structural starter checks are replaced by two strict
  checks that run your completed starter and assert its list comprehension,
  so the total stays the same while the bar rises.
