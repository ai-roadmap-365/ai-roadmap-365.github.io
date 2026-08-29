# Expected output — Day 049 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14, 2026-07-12). Your numbers will match
exactly, because the converter is deterministic — the same input always
produces the same output on every platform.

## Files

- `sample-run.txt` — the reference program run on several good and bad
  inputs, plus the `python3 -c` import check.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (12 checks, 0 failures).

## Required behaviour on every platform

A correct converter must, for these inputs, produce exactly:

| Command | Standard output | Exit code |
| ------- | --------------- | --------- |
| `converter.py 100 C` | `100.0 C = 212.0 F` | 0 |
| `converter.py 32 F` | `32.0 F = 0.0 C` | 0 |
| `converter.py 98.6 F` | `98.6 F = 37.0 C` | 0 |
| `converter.py hot C` | (stderr) `error: 'hot' is not a number` | 1 |
| `converter.py 100 K` | (stderr) `error: unit must be C or F, not 'K'` | 1 |
| `converter.py 100` | (stderr) `error: expected 2 arguments: ...` | 1 |
| `converter.py -300 C` | (stderr) `error: -300.0 C is below absolute zero` | 1 |

The only platform difference is the shell prompt shown before each command
(`$` here); the program's own output is identical everywhere Python 3 runs.

## Test-suite counts

- With the starter unfinished: `12 checks, 0 failure(s).`
- Once you complete all five starter exercises: `18 checks, 0 failure(s).`
  (the six extra checks run your starter through the same good/bad inputs as
  the reference, plus a check that it has the main guard).
