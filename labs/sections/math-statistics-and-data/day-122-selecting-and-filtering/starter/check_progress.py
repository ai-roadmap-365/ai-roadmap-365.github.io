"""Run from this directory (or `python3 starter/check_progress.py` from the
lab root): reports how many of the nine exercises in exercises.py are
complete and correct, against the same expected values the reference
examples/ scripts assert.

Exit code is 0 only when all nine are correct, matching the convention the
rest of this lab's tests use.
"""

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
    ok = expected_check(result)
    if ok:
        passed += 1
        print(f"  {number}. {description}: correct  (got {result!r})")
    else:
        print(f"  {number}. {description}: WRONG    (got {result!r})")


report(
    1,
    "partition invariant",
    ex.ex01_partition_invariant,
    lambda r: r == (3, 3, 8, 2),
)
report(
    2,
    "and/or raise",
    ex.ex02_and_or_raise,
    lambda r: r[0] is True and r[1] == [True, False, False, False],
)
report(3, "precedence", ex.ex03_precedence, lambda r: r == [False, False, True, True, True])
report(4, "mask alignment", ex.ex04_mask_alignment, lambda r: r == [10, 12])
report(
    5,
    "str.contains na",
    ex.ex05_str_contains_na,
    lambda r: r == ["Alice Smith", "dave"],
)
report(6, "query equivalence", ex.ex06_query_equivalence, lambda r: r == ["Bo"])
report(7, "isin empty", ex.ex07_isin_empty, lambda r: r == 0)
report(8, "nlargest ties", ex.ex08_nlargest_ties, lambda r: r == 3)
report(
    9,
    "drop_duplicates subset",
    ex.ex09_drop_duplicates_subset,
    lambda r: r == ["Ada", "Bo"],
)

print(f"\n{passed} of {total} exercises complete.")
sys.exit(0 if passed == total else 1)
