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


report(1, "build three ways", ex.ex01_build_three_ways, lambda r: r[1] == ["a", "b", "c"])
report(2, "alignment", ex.ex02_alignment, lambda r: set(r) == {"a", "d"})
report(3, "dtype promotion", ex.ex03_dtype_promotion, lambda r: r == "float64")
report(
    4,
    "copy-on-write",
    ex.ex04_copy_on_write,
    lambda r: r[0] == [10, 20, 30] and r[1] == [10, 20, 30] and r[2] == [10, 0, 0],
)
report(5, "loc vs iloc", ex.ex05_loc_vs_iloc, lambda r: r == (3, 2))
report(6, "nan semantics", ex.ex06_nan_semantics, lambda r: r is False)
report(7, "vectorized vs apply", ex.ex07_vectorized_vs_apply, lambda r: r == [108.0, 216.0, 324.0])
report(8, "string dtype", ex.ex08_string_dtype, lambda r: r == "str")
report(9, "describe", ex.ex09_describe, lambda r: tuple(r) == (8.0, 5.0, 2.0, 9.0))

print(f"\n{passed} of {total} exercises complete.")
sys.exit(0 if passed == total else 1)
