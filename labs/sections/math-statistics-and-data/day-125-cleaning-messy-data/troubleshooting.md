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

## `pytest examples starter` errors out, or silently runs fewer tests than you expected

Do not pass both directories to one `pytest` invocation. `starter/` and
`examples/` both define a module named `test_cleaning.py`, and pytest
imports test modules by their dotted name — the second one collected
either errors with an `import file mismatch` (what this lab measured) or,
depending on pytest version and cache state, can silently shadow the
first. Run them as two separate commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## Exercise 1's correlation assertion fails because you expected it to go UP

That is very likely the point, not a bug. Mean imputation strictly
**attenuates** (shrinks toward zero) a correlation with an untouched
column — it can never inflate one. An imputed value sits exactly at the
column mean, so its deviation from the mean is exactly zero, and a
zero-deviation term contributes exactly zero to the covariance sum in the
Pearson correlation formula, regardless of what the other column's value
is at that row. Work through `starter/00_brief.md`'s exercise 1 section
for the full derivation.

## Exercise 2's mean shift comes out positive instead of negative

Check which direction you subtracted (`after - before`, not
`before - after`) and confirm you are averaging the whole `reading_c`
column, including the negative station-C readings, not a filtered subset.

## Exercise 3's `thresh=2` count does not match

`thresh` counts **non-null** fields required to keep a row, not missing
ones — a row needs at least 2 non-null values among its 3 nullable
columns (`email`, `phone`, `signup_date`) to survive `thresh=2`. Print
`dropna_frame.notna().sum(axis=1)` to see each row's non-null count
directly before predicting the result.

## Exercise 4's "wrong" and "correct" ffill results look identical

Confirm you actually skipped the sort in the "wrong" test — `ffill()`
operates on the DataFrame's current row order, so if you sorted before
calling it in both branches, both will (correctly) agree, and the
exercise will not demonstrate the bug it is designed to demonstrate.

## `TypeError` from `pd.to_numeric` in exercise 6

Confirm you passed `errors="coerce"` (not `errors="raise"`, the default) —
without it, the first unparseable string raises immediately instead of
becoming `NaN`.

## Exercise 7's raw groupby count is 2, not 8

You likely normalised the column before grouping. Exercise 7's first
groupby is deliberately run on `country_raw`, the **unnormalised** column,
to demonstrate the failure; the second groupby, on the normalised column,
is the one that should give 2.

## Exercise 8's duplicate counts are equal

Confirm you passed `subset=['customer_id', 'item']` (a list) to the
second call, not a single column name or the default (`duplicated()` with
no arguments checks every column, which is exact-duplicate behaviour, not
subset behaviour).

## Exercise 9's contract does not raise on the bad frame

Check you are calling `assert_cleaning_contract` (not
`assert_cleaning_contract(...)` wrapped in something that swallows the
exception) and that `pytest.raises(...)` wraps only the call, not the
frame-construction code above it — if `match=` does not find your
expected substring, print the raised message directly first to see the
real text.

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab. Retry on a connection that can
reach `pypi.org`, or ask whoever manages your network for a mirror.
