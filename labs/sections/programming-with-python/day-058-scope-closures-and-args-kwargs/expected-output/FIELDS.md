# Expected output — Day 058 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The module is deterministic:
the same inputs produce the same values and the same printed demo on every
platform Python 3 runs on.

## Files

- `sample-run.txt` — the reference module's demo (`python3 examples/flexible.py`)
  followed by a `python3 -c` import check that drives two independent counters.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (18 checks, 0 failures). Absolute paths are shown as
  `<repo>`; on your machine they are your real repository path.

## Required behaviour on every platform

A correct module must produce exactly these values:

| Call | Result |
| --- | --- |
| `total()` | `0` |
| `total(2, 4, 6)` | `12` |
| `average(10, 20, 30)` | `20.0` |
| `average()` | `0.0` |
| `average(1, 2, 3, ndigits=4)` | `2.0` |
| `average(1, 2, 3, 4)` | `2.5` (the `4` is a number; `ndigits` is keyword-only) |
| `make_counter()` called four times | `0`, `1`, `2`, `3` |
| a second `make_counter(100)` | `100`, independent of the first |
| `make_counter(10, 5)` called three times | `10`, `15`, `20` |
| `make_multiplier(3)(5)` | `15` |
| `make_multiplier(10)(5)` | `50` |
| `build_request("hello")` | `{'prompt': 'hello', 'temperature': 0.7, 'max_tokens': 256, 'model': 'demo'}` |
| `build_request("hi", temperature=0.2, max_tokens=500)` | overrides `temperature` and `max_tokens`; `model` stays `'demo'` |

`DEFAULTS` must be unchanged after any `build_request` call — the merge
builds a *new* dict rather than mutating the module-level defaults.

## Test-count summary

- **Unfinished starter:** the reference is tested strictly (functions + demo)
  and the starter structurally, for a total of **18 checks, 0 failures**.
- **Finished starter:** once every `NotImplementedError` is gone, the suite
  runs the same strict function and demo checks against your starter and adds
  a `nonlocal` check, for a total of **30 checks, 0 failures**.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- Dictionaries print in insertion order (guaranteed since Python 3.7), so the
  `build_request` output order is stable across platforms.
- No files are written and no network is used; the tests import the module in
  separate `python3 -c` processes, and `PYTHONDONTWRITEBYTECODE=1` keeps the
  tree free of `__pycache__`.
