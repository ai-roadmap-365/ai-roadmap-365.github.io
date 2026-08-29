# Expected output — Day 048 lab

Two captures live in this directory, both from real runs on the authoring
machine (macOS, Python 3.14.0, 2026-07-12):

- `tracebacks.txt` — the three genuine tracebacks the buggy programs produce,
  one per exception type (IndexError, KeyError, TypeError). The `File "..."`
  path is shown in relative form; on any machine only the path wording
  changes, never the exception, message, or line number.
- `walkthrough.txt` — the full output of `bash examples/debug_walkthrough.sh`,
  which reads each traceback bottom-up (exception type + culprit line) and
  then runs the fixed versions to show they succeed.

## What must be true on every platform

1. `examples/buggy/average_scores.py` fails with `IndexError: list index out of range` on line 5.
2. `examples/buggy/lookup_capital.py` fails with `KeyError: 'Germany'` on line 6.
3. `examples/buggy/total_price.py` fails with `TypeError: can only concatenate str (not "int") to str` on line 4.
4. All three `examples/fixed/*.py` programs run to completion and exit 0.
5. `bash tests/run_tests.sh` prints `9 checks, 0 failure(s).` and exits 0.

## Platform and version notes

- The caret/underline marks (`~~~^^^`) under the failing sub-expression appear
  on Python 3.11 and newer; on older versions the traceback omits them but is
  otherwise the same.
- On Linux the behavior is identical; only the resolved file path differs.
- On Windows, use `py` or `python` in place of `python3`; the exceptions and
  line numbers are unchanged.
