# Expected output — Day 060 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The tally is deterministic:
given the same directory contents, the tool produces the same counts on
every platform Python 3 runs on. The one field that changes between runs is
`generated_at`, because it is the current time — the tests deliberately
ignore it.

## Files

- `sample-run.txt` — the reference tool run against the bundled `sample-data`
  folder: printed report, the same report written with `--out report.json`,
  the file on disk, and a `python3 -c` import check of `tally_extensions`.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (14 checks, 0 failures). Absolute paths are shown as
  `<repo>`; on your machine they are your real repository path.

## Required behaviour on every platform

The bundled `sample-data` folder holds six files — three `.csv` (one nested
in `sub/`), two `.json`, and one `.txt` — so a correct tool prints:

| Field | Value for `sample-data` | Notes |
| --- | --- | --- |
| `generated_at` | an ISO-8601 timestamp, e.g. `2026-07-13T11:56:58` | the current time; changes every run; not tested |
| `directory` | `sample-data` | the string passed to `--dir` |
| `total_files` | `6` | files found by walking the tree recursively |
| `by_extension` | `{".csv": 3, ".json": 2, ".txt": 1}` | ordered largest-first |

The test suite builds its own temporary tree with seven files — including one
uppercase `.CSV` and one file with no extension — and asserts:

| Behaviour | Expected |
| --- | --- |
| `total_files` | `7` |
| `.csv` count | `3` — `.CSV` and `.csv` count together (case-insensitive) |
| `.json` count | `2` |
| `.txt` count | `1` |
| no-extension file | counted under `(none)` (`1`), not dropped |
| ordering | `by_extension` is largest-count first (`.csv` before `.json`) |
| `--out FILE` | writes the same report as valid JSON to `FILE` |

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- `rglob("*")` walks subdirectories on every platform, so the nested
  `sub/c.csv` is always found and counted.
- The test runner uses `mktemp -d` to build a throwaway directory tree and
  removes it on exit. On Linux `mktemp -d -t toolkit-test.XXXXXX` behaves the
  same as on macOS; the path is quoted and removed regardless.
- On Windows, run inside WSL and follow the Linux path; the tool is pure
  standard-library Python and behaves identically.
