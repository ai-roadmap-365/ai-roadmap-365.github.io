"""Exercise 7 -- .isin() versus chained ==, and the empty-list trap.

Run: python3 07_isin_vs_chained.py

`series.isin(values)` and a chain of `(series == v1) | (series == v2) |
...` compute the identical boolean mask -- `.isin()` is simply the version
that scales to any number of values without writing one `==`/`|` pair per
value, and reads as "is this value one of these" rather than a wall of
`|`. The one behaviour worth knowing on purpose: `.isin([])` -- an empty
list of wanted values -- returns an all-False mask, and filtering with it
gives an EMPTY frame, not the original untouched frame. It is easy to
assume "no filter values given" means "no filter applied"; pandas disagrees,
correctly, because "is this row's value among these zero values" can only
ever be false.
"""

import pandas as pd

checks = 0
failures = 0


def check(label, condition):
    global checks, failures
    checks += 1
    if condition:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}")
        failures += 1


staff = pd.DataFrame(
    {
        "name": ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay", "Gio", "Hu"],
        "dept": ["eng", "sales", "eng", "hr", "sales", "eng", "hr", "sales"],
    }
)
print("staff:")
print(staff)

wanted = ["eng", "hr"]
via_isin = staff[staff.dept.isin(wanted)]
via_chained = staff[(staff.dept == "eng") | (staff.dept == "hr")]
print(f"\nisin(['eng', 'hr']):                 {via_isin.name.tolist()}")
print(f"(dept == 'eng') | (dept == 'hr'):    {via_chained.name.tolist()}")

check("isin() and the chained == form select the identical rows", via_isin.equals(via_chained))
check("both forms select exactly the 5 eng/hr staff", len(via_isin) == 5)

# Three-value case: isin scales with no extra | per value; the chained form
# needs one more == and one more | for every value added.
wanted3 = ["eng", "hr", "sales"]
via_isin3 = staff[staff.dept.isin(wanted3)]
via_chained3 = staff[(staff.dept == "eng") | (staff.dept == "hr") | (staff.dept == "sales")]
check("with a third value, isin() and the chained form still agree exactly", via_isin3.equals(via_chained3))
check("isin() with all departments listed returns the whole frame", len(via_isin3) == len(staff))

# The empty-list trap.
empty_wanted: list[str] = []
via_empty = staff[staff.dept.isin(empty_wanted)]
print(f"\nisin([]) -- an empty wanted list -- rows returned: {len(via_empty)}")

check("isin([]) returns zero rows, NOT the whole untouched frame", len(via_empty) == 0)
check("isin([]) produces an all-False mask, one entry per row", (~staff.dept.isin(empty_wanted)).all())
check(
    "isin([]) does NOT mean 'no filter' -- it means 'exclude everything', the opposite intuition",
    len(via_empty) != len(staff),
)

# The corresponding negation, ~isin, correctly means "none of these" and
# with an empty list correctly keeps everything -- worth contrasting.
via_not_in_empty = staff[~staff.dept.isin(empty_wanted)]
print(f"~isin([]) -- 'is dept NOT one of these zero values' -- rows returned: {len(via_not_in_empty)}")
check("~isin([]) DOES return every row, since nothing is excluded by an empty exclusion list", len(via_not_in_empty) == len(staff))

print(f"\n{checks} checks, {failures} failure(s).")
if failures:
    raise SystemExit(1)
print("07_isin_vs_chained.py: every assertion held.")
