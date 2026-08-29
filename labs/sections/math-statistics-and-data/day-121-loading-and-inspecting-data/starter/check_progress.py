"""Run from this directory (or `python3 starter/check_progress.py` from the
lab root): reports how many of the nine exercises in exercises.py are
complete and correct, against the same expected values the reference
examples/ scripts assert.

Exit code is 0 only when all nine are correct, matching the convention the
rest of this lab's tests use.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exercises as ex

passed = 0
total = 9


def report(number, description, fn, expected_check):
    """Run one exercise function, catching the NameError an unfilled blank
    raises, and check its return value against expected_check(value)."""
    global passed
    try:
        result = fn()
    except NameError as exc:
        print(f"  {number}. {description}: NOT YET COMPLETE ({exc})")
        return
    except Exception as exc:  # noqa: BLE001 -- report any other mistake too
        print(f"  {number}. {description}: ERROR -- {exc!r}")
        return
    try:
        ok = expected_check(result)
    except Exception as exc:  # a malformed return value shouldn't crash the report
        print(f"  {number}. {description}: WRONG    (return value {result!r} raised {exc!r})")
        return
    if ok:
        passed += 1
        print(f"  {number}. {description}: correct  (got {result!r})")
    else:
        print(f"  {number}. {description}: WRONG    (got {result!r})")


report(
    1,
    "the Namibia trap",
    ex.ex01_the_namibia_trap,
    lambda r: (isinstance(r[0], float) and math.isnan(r[0])) and r[1] == "NA",
)
report(
    2,
    "leading zeros",
    ex.ex02_leading_zeros,
    lambda r: r[0] == 123 and r[1] == "00123",
)
report(
    3,
    "precision loss",
    ex.ex03_precision_loss,
    lambda r: r[0] == 2**53 + 1 and r[1] == 2**53,
)
report(
    4,
    "dates",
    ex.ex04_dates,
    lambda r: r[0] == "str" and r[1].startswith("datetime64"),
)
report(
    5,
    "encoding",
    ex.ex05_encoding,
    lambda r: r == "UnicodeDecodeError",
)
report(
    6,
    "chunking",
    ex.ex06_chunking,
    lambda r: r[0] == 28 and r[1] == 28,
)
report(
    7,
    "CSV vs Parquet",
    ex.ex07_csv_vs_parquet,
    lambda r: r[0] != "Int64" and r[1] == "Int64",
)
report(
    8,
    "inspection battery",
    ex.ex08_inspection_battery,
    lambda r: r == (1, "north"),
)
report(
    9,
    "category memory",
    ex.ex09_category_memory,
    lambda r: r[0] > r[1] and (r[0] / r[1]) >= 2.0,
)

print(f"\n{passed} of {total} exercises complete.")
sys.exit(0 if passed == total else 1)
