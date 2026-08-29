# Expected output — Day 061 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The score summariser is
deterministic: given the same numbers it prints the same report and the same
exit code on every platform Python 3 runs on. The whole point of the lab is
that the messy starter and the clean reference produce **identical** output —
refactoring changes readability, never behaviour.

## Files

- `sample-run.txt` — the messy starter and the clean reference driven on the
  same input (byte-for-byte identical, confirmed with `diff`), plus an
  even-count median, a floating-point set, a single value, the empty-input
  path, and a `python3 -c` import of one function.
- `test-run.txt` — a real run of `bash tests/run_tests.sh`. The first block is
  the suite with the starter still messy (10 checks, 2 skipped); the second
  block is the extra readability checks that run once the starter has been
  refactored (14 checks, 2 skipped).

## Required behaviour on every platform

For the input `70 85 90 55 60`, every correct version of the tool must print
exactly these lines and exit 0:

| Line | Value | Why |
| --- | --- | --- |
| `count: 5` | number of scores | `len(scores)` |
| `mean: 72.00` | arithmetic mean | `360 / 5`, two decimals |
| `median: 70.00` | middle of the sorted list | sorted `[55,60,70,85,90]`, index 2 |
| `min: 55.00` | smallest score | `min(scores)` |
| `max: 90.00` | largest score | `max(scores)` |
| `stdev: 13.64` | population standard deviation | `sqrt(930/5) = sqrt(186)` |
| `passing: 80.0%` | share at or above the pass mark 60 | 4 of 5, one decimal |

Other captured cases (reference tool):

| Command | Key output | Exit code |
| --- | --- | --- |
| `report.py 70 85 90 55` | `median: 77.50` (even count → mean of two middle) | 0 |
| `report.py 100` | `stdev: 0.00`, `passing: 100.0%` | 0 |
| `report.py` (no args) | `no data` (stderr path in spirit; printed plainly here) | 1 |

## Skipped-tool behaviour (important)

The optional Black and Ruff/flake8 checks are **skipped, not failed**, when
those tools are not installed — which is the case on a plain Python install,
including the authoring machine (see the two `skip:` lines in
`test-run.txt`). A missing optional tool must never turn the suite red. If you
install them (`python3 -m pip install black ruff`), the same command runs
them on the reference and reports two extra `ok:` lines instead of skips.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- Scores may be integers or decimals; they are parsed with `float()`, so
  `90` and `90.0` are equivalent and always print with two decimals.
- The tool writes no files and makes no network calls; there is nothing to
  clean up.
