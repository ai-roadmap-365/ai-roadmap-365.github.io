# Day 125 lab — the brief

Nine exercises, in order. Work top to bottom in `test_cleaning.py`. Every
table comes from a fixture defined in `conftest.py` (`income_spending`,
`temperature_readings`, `dropna_frame`, `sensor_timeseries`,
`coerce_frame`, `country_frame`, `duplicates_frame`, `clean_customers`,
`contract_violating_customers`) — read `data.py` once to see exactly what
each one contains before you start.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `19 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert exact values everywhere except where floating-point arithmetic
makes `pytest.approx` the honest choice (exercise 1's mean/std/correlation,
exercise 2's mean and shift) — never because a number is "roughly one
machine on one day." Every value in this lab is deterministic.

---

## Exercise 1 — mean imputation distorts (`income_spending`)

`income_spending` has `income` missing at 10 of 40 rows, and `spending` is
genuinely, linearly related to `income` (`spending = 0.42 * income +
noise`). Fill the missing `income` values with `income.mean()` and check
three things, before and after:

- **The mean is unchanged** — `income.mean()` before imputation equals
  `income.mean()` after, within `pytest.approx(..., abs=1e-6)`. This is
  the whole reason mean imputation feels safe.
- **The standard deviation strictly shrinks** — assert
  `after_std < before_std`. You have added ten points that sit exactly on
  the mean, which can only pull the spread in.
- **The correlation with `spending` strictly *attenuates*, toward zero —
  it does NOT grow.** This may be the opposite of your first guess. Work
  through *why*: an imputed point's `income` value is, by construction,
  exactly at the column mean, so its deviation from the mean is exactly
  zero. A term with a zero deviation on one axis contributes exactly zero
  to the covariance between `income` and `spending`, no matter what
  `spending` happens to be at that row. It can only ever dilute an
  existing relationship — never strengthen one. This is a mathematical
  fact about the Pearson correlation formula, not a property of this one
  dataset; you can prove it to yourself by writing out the covariance sum
  term by term for a single imputed point.
- Assert `income_spending['income'].isna().sum() == 10` — the exact
  planted count.

## Exercise 2 — `fillna(0)` on a measurement column (`temperature_readings`)

`temperature_readings` has three missing readings **and** one genuine
`0.0` reading already in the data (station C, the last row). `fillna(0)`
makes all four of these identical in the data.

- Assert the mean before and after `fillna(0.0)`, and the exact (negative)
  shift between them. Zero is a value, not an absence — assert the shift
  is not zero.
- Assert that after the fill, the genuine `0.0` reading and the three
  imputed readings are bit-for-bit indistinguishable: nothing in the data
  can tell them apart anymore.

## Exercise 3 — `dropna` with `how`, `thresh`, `subset` (`dropna_frame`)

An 8-row, 4-column frame with a deliberately mixed missingness pattern
across `email`, `phone` and `signup_date`. Assert four different row
counts on the same frame:

- `how='any'` — drops a row missing even one field. The strictest cut.
- `how='all'` — only drops a row missing on *every* field.
- `thresh=2` — keeps rows with at least 2 non-null fields.
- `subset=['email']` — only checks the named column.

Read the docstring in `data.py` for the exact missingness pattern before
you predict the counts.

## Exercise 4 — `ffill` on unsorted data is a real bug (`sensor_timeseries`)

`sensor_timeseries` is written in true chronological order (`day` 1–8)
with two gaps. `shuffle_rows(sensor_timeseries, seed=7)` scrambles the row
*order* without touching `day`.

- `ffill` the shuffled frame **without sorting first**. Re-sort the result
  by `day` only to compare it against the correct answer — the fill
  computation itself already happened on the scrambled order. Assert `day`
  2 and `day` 3 come out wrong.
- Now sort by `day` **before** filling. Assert the full `reading` column
  equals `[10.0, 10.0, 10.0, 13.0, 14.0, 14.0, 16.0, 17.0]` — every gap
  correctly carried forward from its true chronological neighbour.

## Exercise 5 — the missing indicator (`temperature_readings`)

Record `isna()` into a new boolean column **before** you impute anything.
Then impute `reading_c` with its mean. Assert the recorded column still
equals the *original* `isna()` mask exactly, even though
`reading_c.isna()` is now all `False` — the flag is the only place the
evidence survives.

## Exercise 6 — `to_numeric(errors='coerce')` (`coerce_frame`)

`quantity_raw` has three deliberately unparseable strings planted among
seven clean numeric strings. Run
`pd.to_numeric(coerce_frame['quantity_raw'], errors='coerce')` and assert:

- The resulting `NaN` count equals the count of the three planted garbage
  values (`'N/A'`, `'unknown'`, `'--'`) — never coerce a column blind
  without counting what changed.
- The seven clean values survive as floats, in order.

## Exercise 7 — string normalisation (`country_frame`)

Twelve rows, one true country recorded eight different ways
(`'USA'`, `'U.S.A.'`, `' usa '`, `'Usa'`, `'Canada'`, `'canada '`,
`' Canada'`, `'CANADA'`).

- Assert `country_raw.nunique()` is **8** before normalising, and **2**
  after: `.str.strip().str.lower().str.replace('.', '', regex=False)`,
  then map `'usa' -> 'USA'` and `'canada' -> 'Canada'`.
- Assert a raw `groupby('country_raw')` produces **8** groups — visibly
  wrong, since the truth is 2 — and that grouping on the *normalised*
  column produces exactly 2 groups with the correct USA/Canada amount
  totals.

## Exercise 8 — duplicates mean whatever subset you named (`duplicates_frame`)

Row 4 is an **exact** duplicate of row 0 (every column, including the
timestamp — a genuine re-logged entry). Row 5 shares `(customer_id,
item)` with row 1 but has a *different* timestamp — a real second
purchase, not a duplicate log entry, but still a duplicate under a subset
key.

- Assert `duplicated().sum()` and
  `duplicated(subset=['customer_id', 'item']).sum()` give different exact
  counts, with the subset count larger.
- State, with an assertion, which customer(s) each definition flags, and
  say in a comment which definition answers which real question ("was
  this order logged twice?" vs. "did this customer buy this item more
  than once?").

## Exercise 9 — the cleaning contract must hold, and be provably able to fail

`assert_cleaning_contract` (in `contract.py`) checks three post-conditions:
no nulls in named key columns, declared dtypes on named columns, and a row
count inside `[min_rows, max_rows]`. It raises `ContractViolation` naming
the first thing that broke.

- On `clean_customers`, with `key_columns=['customer_id', 'country']`,
  `dtypes={'income': 'float64'}`, `min_rows=3`, `max_rows=10` — the call
  must **not** raise.
- On `contract_violating_customers` (a null `customer_id`) — assert it
  raises `ContractViolation` matching `'customer_id'`.
- Build your own bad frame from `build_clean_customers()` with `income`
  cast to `str` — assert it raises matching `'income'`.
- Build your own bad frame that is `build_clean_customers().iloc[:1]` (one
  row) — assert it raises matching `'row count'`.

A contract that never fails proves nothing; this exercise is only done
once you have shown it can genuinely raise, on three different violations.

---

Prove your suite is not vacuous once you are green: re-break one assertion
on purpose (flip a comparison, change an expected number), confirm the run
exits non-zero with a printed `FAIL`, then restore it and confirm green
again.
