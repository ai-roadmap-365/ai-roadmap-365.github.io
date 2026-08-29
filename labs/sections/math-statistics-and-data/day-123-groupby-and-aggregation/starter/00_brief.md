# Day 123 lab — the brief

Nine exercises, in order. Work top to bottom in `test_groupby.py`. Every
table comes from a fixture defined in `conftest.py` (`orders`, `sales`,
`cat_sales`, `weighted`, `large`) — read `data.py` once to see exactly what
each one contains before you start.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `20 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert exact values everywhere except exercise 8's timing ratio, which is
inherently one machine on one day — `pytest.approx` is for that ratio and
for the z-scores in exercise 4, nowhere else.

---

## Exercise 1 — the reconciliation invariant (`orders`)

`orders` has two rows with no `region` at all. `groupby('region')` drops
them by default, silently. In `test_1_dropna_true_undercounts_by_exactly_the_missing_rows`:

- Group by `region`, sum `amount`, sum the per-group sums. That total is
  **less** than `orders['amount'].sum()`.
- Assert the exact gap, and assert the gap equals exactly the sum of
  `amount` on the rows where `region` is missing.

In `test_1_dropna_false_reconciles_exactly`: repeat with `dropna=False`.
Now there is a real `NaN` group carrying the missing rows' total, and the
grouped sum equals the overall total exactly. **This is the habit the
whole day is built on: after any groupby aggregation, check that the parts
reconcile with the whole.**

## Exercise 2 — `count()` versus `size()` (`orders`)

`orders` also has two rows with no `amount`. `size()` counts **rows**;
`count()` counts **non-missing values per column**. Group with
`dropna=False` so the region-missing rows stay in the picture too. Assert
that `size` and `count` disagree on the groups that contain a missing
`amount`, and that `(size - count).sum()` equals
`orders['amount'].isna().sum()` exactly.

## Exercise 3 — `.agg()` four ways (`sales`)

`sales` is clean: four regions, three rows each. Write four tests:

1. A single function: `.agg('sum')`.
2. A list: `.agg(['sum', 'mean', 'count'])` — assert the column names.
3. A per-column dict: `.agg({'amount': 'sum', 'order_id': 'count'})`.
4. Named aggregation: `.agg(total=('amount', 'sum'), avg=('amount', 'mean'), n=('order_id', 'count'))`
   — assert the result columns are **flat**, not a `pandas.MultiIndex`.
   This is the readable modern form.

## Exercise 4 — shapes: `agg` versus `transform` (`sales`)

- `agg` reduces each group to one row: assert the shape has one entry per
  group (4,).
- `transform` returns the **input's shape**: assert its shape matches
  `sales.shape[0]` (12), not the number of groups.
- Use `transform` to attach North's group mean (120.0) to every North row.
- Build a within-group z-score: `(amount - group_mean) / group_std`, both
  computed with `transform`. Assert each region's z-scores average to 0
  (`pytest.approx`, `abs=1e-9`).

## Exercise 5 — `GroupBy.filter` (`orders`)

`filter` keeps or drops **whole groups**, unlike Day 122's row-level
`.query()`/boolean-mask filtering — same word, different operation, worth
naming as such. `orders` grouped by `region` (default `dropna=True`) has
sizes East=3, North=3, South=3, West=1. Filter to groups of size `>= 3`.
Assert West is entirely absent from the survivors, and that the survivors'
row count equals the sum of the surviving groups' own sizes (9).

## Exercise 6 — multi-key grouping (`sales`)

Group `sales` by `['region', 'rep']`. Assert the result's index is a
`pandas.MultiIndex` with `.names == ['region', 'rep']`, and check one
value: `('East', 'Ann')` is 420.0. Repeat with `as_index=False` and assert
the same value comes back in a flat frame instead.

## Exercise 7 — `observed=` (`cat_sales`)

`cat_sales` declares `region` (5 categories) and `rep` (4 categories) as
pandas categoricals, two of which — `Central` and `Deb` — never actually
appear in the 12 rows of data. Group by both keys with `observed=False`:
assert 20 rows (5 x 4, every possible combination, most never observed).
Repeat with `observed=True`: assert 9 rows (only the combinations that are
actually present), and check `('North', 'Ann')` is 2.

## Exercise 8 — performance (`large`, 200,000 rows)

Time `large.groupby('key')['value'].agg('mean')` against
`large.groupby('key')['value'].apply(lambda g: g.mean())`. First assert
both give the same numbers (`np.allclose` after sorting both by index).
Then assert `apply_seconds / builtin_seconds >= 3.0` — a conservative
floor; this machine measured roughly 10-15x, but a slower or busier
machine should still clear 3x easily. Never assert a millisecond figure.

Second test: assert `groupby(sort=True)` and `groupby(sort=False)` give
the same **values** (once both are sorted by index for comparison) — only
the ordering of unsorted work should ever differ, never the numbers.

## Exercise 9 — a weighted mean per group (`weighted`)

Write a `weighted_mean(group)` function using
`np.average(group['value'], weights=group['weight'])`. Apply it per
`region` with `include_groups=False`. Assert North is `approx(17.5)`,
South is `approx(13.0)`, East is `approx(60.0)`.

Then compute the same weighted means **without** `apply`: build a
`value * weight` column, sum both that column and `weight` per group with
`.agg`, then divide. Assert the two routes agree exactly. This is the
honest case where `apply` is the readable choice, and you can still check
it against a faster vectorised route.

---

Prove your suite is not vacuous once you are green: re-break one assertion
on purpose (flip a comparison, change an expected number), confirm the run
exits non-zero with a printed `FAIL`, then restore it and confirm green
again.
