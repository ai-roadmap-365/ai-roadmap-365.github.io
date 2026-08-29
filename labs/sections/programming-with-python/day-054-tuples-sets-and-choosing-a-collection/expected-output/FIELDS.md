# Expected output — Day 054 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14.0, bash 3.2, 2026-07-13). Your numbers
will match exactly, because the program is deterministic — every group is
**sorted** before printing, so the same input always produces the same output
on every platform, regardless of the fact that a `set` itself is unordered.

## Files

- `sample-run.txt` — the reference program run on good and bad inputs, plus
  two `python3 -c` import checks (`dedupe` and `compare`).
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (13 checks, 0 failures).

## Required behaviour on every platform

A correct program must, for these inputs, produce exactly:

| Command (arguments abbreviated) | Key output line | Exit code |
| ------------------------------- | --------------- | --------- |
| `"apple,banana,apple,cherry" "banana,cherry,date,date"` | `List A: 4 items read, 3 unique after dedupe` | 0 |
| (same) | `Common (A & B): banana, cherry` | 0 |
| (same) | `Only in A (A - B): apple` | 0 |
| (same) | `Only in B (B - A): date` | 0 |
| (same) | `Symmetric difference (A ^ B): apple, date` | 0 |
| `"banana" "banana,cherry"` | `Only in A (A - B): (none)` | 0 |
| `"apple,banana"` (one argument) | (stderr) `error: expected 2 arguments: ...` | 1 |
| `" , ," "banana"` (empty after cleaning) | (stderr) `error: each list must contain at least one item` | 1 |

The only platform difference is the shell prompt shown before each command
(`$` here); the program's own output is identical everywhere Python 3 runs.
Because every group is sorted, the ordering you see is guaranteed — it does
**not** depend on set iteration order.

## Test-suite counts

- With the starter unfinished: `13 checks, 0 failure(s).`
- Once you complete all five starter exercises: `20 checks, 0 failure(s).`
  (the seven extra checks run your starter through the same good/bad inputs as
  the reference, plus a check that it has the main guard).

## Windows note

On native Windows (outside WSL), use `python` instead of `python3` if that is
how Python is exposed, and run the test suite from Git Bash or WSL (it is a
bash script). The program's output is byte-for-byte identical; only the
launcher name and the shell differ.
