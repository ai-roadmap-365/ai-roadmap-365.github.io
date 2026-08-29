# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'pandas'`

The lab's dependencies live in its own `.venv`, not on your system Python.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the test suite at a Python that already has pandas 3.0.5
installed: `PYTHON=/path/to/python3 bash tests/run_tests.sh`.

## `pytest examples starter` reports fewer failures than you expected, or none

Do not pass both directories to one `pytest` invocation. `starter/` and
`examples/` both define a module named `test_groupby.py`, and pytest
imports test modules by their dotted name; the second one collected
shadows the first, so `pytest examples starter` can silently run only one
directory's tests under the other's name. Run them as two separate
commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## Exercise 1's grouped sum does not equal `orders['amount'].sum()`

That is the point of exercise 1, not a bug in your code — `groupby`
excludes rows whose key is missing by default. Group with `dropna=False`
if you want the parts to add back up to the whole; the gap under the
default (`dropna=True`) should equal exactly the total of the rows whose
`region` is missing.

## Exercise 2's `size` and `count` are equal on every group

You are counting the wrong thing, or grouping the wrong column. `size()`
counts rows and is the same number no matter which column you ask about;
`count()` is a **per-column** method (`grouped['amount'].count()`, not
`grouped.count()` alone) that counts only non-missing values in that one
column. Confirm you introduced the missing `amount` values by inspecting
`orders['amount'].isna()` directly before grouping anything.

## `TypeError: agg function failed [how->mean,dtype->object]`

You called `.agg('mean')` (or `.transform('mean')`) on a `GroupBy` built
from the whole DataFrame rather than from one numeric column or a numeric
subset — `sales.groupby('region').agg('mean')` tries to average every
column, including the non-numeric `rep`. Select the column first:
`sales.groupby('region')['amount'].agg('mean')`.

## Exercise 4's z-score does not average to (approximately) zero

Check that you used `transform`, not `agg`, for both the group mean and
the group standard deviation — `agg` returns one row per group, and
subtracting a 4-row Series from a 12-row Series aligns by label rather
than raising the error you might expect, producing mostly `NaN`.
`transform` is the one that returns a value for every original row.

## Exercise 6's `as_index=False` result has different values than the `MultiIndex` version

It should not — if it does, you likely grouped a different key order or
column selection between the two calls. Compare exactly the same
`groupby(["region", "rep"])["amount"].sum()` call, once with
`as_index=False` and once without, before comparing values.

## Exercise 7's `observed=False` count is not 20

Confirm both `region` and `rep` are genuinely `pandas.Categorical` with
the categories declared in `data.py` (5 and 4 respectively, including one
unused category each) — grouping a plain `object`/`str` column never
manufactures unobserved rows regardless of `observed=`, because there is
no fixed category list to draw the unseen combinations from.

## Exercise 8's ratio assertion fails on a fast or heavily loaded machine

The 3.0x floor is deliberately conservative — this machine measured
roughly 10-15x. If your machine is unusually fast, lightly loaded, or the
run happens to catch a slow build of `apply`'s Python-level call overhead,
the ratio should still clear 3x; if it does not even after a couple of
re-runs, increase `n` in `build_large()` (in `data.py`) so the built-in
path's per-call savings dominate more clearly, and note the change rather
than lowering the assertion.

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab. Retry on a connection that can
reach `pypi.org`, or ask whoever manages your network for a mirror.
