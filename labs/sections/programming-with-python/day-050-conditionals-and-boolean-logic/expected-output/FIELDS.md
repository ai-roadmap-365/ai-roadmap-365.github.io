# Expected output — Day 050 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14, 2026-07-13). Your numbers will match
exactly, because the decision engine is deterministic — the same input always
produces the same output on every platform.

## Files

- `sample-run.txt` — the reference program run on good and bad inputs, plus the
  `python3 -c` import check.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (14 checks, 0 failures).

## Required behaviour on every platform

A correct decision engine must, for these inputs, produce exactly:

| Command | Standard output | Exit code |
| ------- | --------------- | --------- |
| `triage.py 0.95 verified` | `score=0.95 verified=True  -> AUTO_ACCEPT (confidence: high)` | 0 |
| `triage.py 0.95 unverified` | `score=0.95 verified=False -> REVIEW (confidence: high)` | 0 |
| `triage.py 0.30 verified` | `score=0.30 verified=True  -> REJECT (confidence: low)` | 0 |
| `triage.py 0.90 verified` | `score=0.90 verified=True  -> AUTO_ACCEPT (confidence: high)` | 0 |
| `triage.py 0.50 verified` | `score=0.50 verified=True  -> REVIEW (confidence: medium)` | 0 |
| `triage.py hot verified` | (stderr) `error: 'hot' is not a number` | 2 |
| `triage.py 1.5 verified` | (stderr) `error: score 1.5 is out of range ...` | 2 |
| `triage.py 0.8 maybe` | (stderr) `error: status must be verified or unverified ...` | 2 |
| `triage.py 0.8` | (stderr) `error: expected 2 arguments: ...` | 2 |

The classification prints to standard output; errors print to standard error
and set exit code 2. The only platform difference is the shell prompt shown
before each command (`$` here); the program's own output is identical
everywhere Python 3 runs. On Windows, substitute `python` for `python3` if that
is how Python is exposed, or run inside WSL.

## Test-suite counts

- With the starter unfinished: `14 checks, 0 failure(s).`
- Once you complete all five starter exercises: `22 checks, 0 failure(s).`
  (the extra checks run your starter through the same nine good/bad inputs as
  the reference, plus a check that it has the main guard).
