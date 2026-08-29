# Expected output — Day 044 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, Python 3.14.0, 2026-07-12):

- `example-run.txt` — the full console output of `python3 examples/types_demo.py`.
- `test-run.txt` — the full console output of `bash tests/run_tests.sh`.

## What must appear on every platform

`python3 examples/types_demo.py` is deterministic **except** for the identity
numbers, which reflect memory addresses and differ every run. A correct run
always prints, regardless of OS or Python 3.x version:

1. The five core-type lines with type names `int`, `float`, `bool`, `str`,
   and `NoneType`.
2. A dynamic-typing block where the name `thing` prints first as `int`, then
   as `str` (`same name, different type`).
3. A mutability block asserting `id unchanged after append: True` (list) and
   `id changed after '+': True` (string).
4. A safe-conversion block: `'30'  -> 30 (int)` and
   `could not convert (ValueError handled)` for `'oops'`.

`bash tests/run_tests.sh` ends with `12 checks, 0 failure(s).` and exits 0.

## Platform notes

- **macOS / Linux:** identical output; both use `python3`.
- **Windows:** the interpreter may be invoked as `python` rather than
  `python3`; the printed lines are the same. Run inside PowerShell or WSL.
- The literal `id()` numbers are intentionally not captured as a stable
  value — only the *comparisons* (`True`) are stable and checked.
