# Day 124 lab — the brief

Nine exercises, in order. Work top to bottom in `test_merge.py`. Every
table comes from a fixture defined in `conftest.py` (`left_dup`,
`right_dup`, `left_keys`, `right_keys`, `int_keyed`, `str_keyed`,
`price_left`, `price_right`, `wide`, `dup_index_col`) — read `data.py`
once to see exactly what each one contains before you start.

Check yourself at any point:

```bash
.venv/bin/pytest starter -v
```

On an untouched checkout that prints `22 skipped`. A **skip** means "not
attempted". Replace a `pytest.skip(...)` line with real assertions and
delete it — when every skip is gone and the suite is green, you are
finished:

```bash
.venv/bin/pytest starter -q
echo $?
```

Assert exact values everywhere in this lab. Unlike Day 123, nothing here
is timing-dependent.

---

## Exercise 1 — the explosion (`left_dup`, `right_dup`)

`left_dup` has key `A` three times and key `B` twice. `right_dup` has key
`A` twice and key `B` four times. An **inner merge on `cust_id`** is a
per-key Cartesian product: key `A` alone produces `3 * 2 = 6` rows, key
`B` alone produces `2 * 4 = 8` rows. Compute the expected total from each
side's `.value_counts()` — do not hardcode `14`, derive it — and assert
the merged shape matches. Then assert the per-key row counts (6 for `A`,
8 for `B`) directly.

## Exercise 2 — `validate=` (`left_dup`, `right_dup`, `left_keys`, `right_keys`)

`validate='one_to_one'` on `left_dup`/`right_dup` must raise
`pandas.errors.MergeError` — key `A` and key `B` are each duplicated on
both sides, violating "one-to-one" from either direction. The same
`validate='one_to_one'` on `left_keys`/`right_keys` (every key unique on
both sides) must raise nothing and return 3 rows. A third test:
`validate='one_to_many'` on `left_dup`/`right_dup` must **also** raise —
key `A` repeats on the LEFT side (3 times), which violates "one" even
though you asked for "many" on the right.

## Exercise 3 — `indicator=True` (`left_keys`, `right_keys`)

`left_keys` has keys A, B, C, D. `right_keys` has keys B, C, D, E. Outer
merge with `indicator=True`, then read the `_merge` column's
`.value_counts()`: `left_only` should be 1 (key A), `right_only` should be
1 (key E), `both` should be 3 (B, C, D). Assert the reconciliation
explicitly: `left_only + both` equals `left_keys`' row count (4);
`right_only + both` equals `right_keys`' row count (4); all three sum to
the merged row count (5).

## Exercise 4 — the silent dtype-mismatch join (`int_keyed`, `str_keyed`)

`int_keyed['id']` is `int64`. `str_keyed['id']` is a pandas
**Categorical** of the same digits as strings. Inner-merging them on `id`
returns **0 rows** — no exception, no warning. Confirm both dtypes, run
the merge, assert `result.shape[0] == 0`. Then cast `str_keyed['id']` to
`int64` with `.astype({'id': 'int64'})`, merge again, and assert 3 rows
come back with id `1002`'s score equal to `91`.

**A third test, and it matters:** build a fresh frame with a *plain* `str`
`id` column (not categorical) holding the same digits, and merge it
against `int_keyed`. In pandas 3.0.5 this does **not** silently return
zero rows — it **raises `ValueError`**, telling you plainly that you are
merging incompatible key dtypes. Assert that raise. This is the honest
correction: the categorical case above is the one that still slips
through silently; the plain-string case is now caught for you.

## Exercise 5 — the four join types (`left_keys`, `right_keys`)

Same pair of frames as exercise 3. Write four tests asserting the row
count and surviving keys for `how='inner'` (3 rows, B/C/D),
`how='left'` (4 rows, A's `plan` all `NaN`), `how='right'` (4 rows, E's
`region` all `NaN`), and `how='outer'` (5 rows, A through E). A fifth test
builds a `{how: row_count}` dict for all four in one place and asserts it
equals `{'inner': 3, 'left': 4, 'right': 4, 'outer': 5}`.

## Exercise 6 — suffixes, `on`/`left_on`/`right_on`, and `join()` (`price_left`, `price_right`)

Both frames have a `price` column. A plain `merge(on='sku')` produces
`price_x` and `price_y` — assert both exist, `price` does not, and X1's
values are `9.99`/`10.99`. Repeat with `suffixes=('_catalog', '_live')`
and assert those names instead. Third test: rename `price_right`'s `sku`
to `sku_code`, merge once with `on='sku'` (after renaming back, or just
merge `price_left` against the *unrenamed* `price_right` for the `on=`
case and against the *renamed* copy for `left_on`/`right_on`) and confirm
both give the same row count and values. Fourth test: `set_index('sku')`
on both and use `.join(how='inner', lsuffix='_l', rsuffix='_r')`; assert
it matches the equivalent `.merge(on='sku')` result once both are sorted
by index.

## Exercise 7 — `concat` alignment

Build two small frames by hand with partially overlapping columns.
`pd.concat([frame_a, frame_b], axis=0, ignore_index=True)`: assert the
combined shape, and assert **exactly which cells** are `NaN` — the column
missing from `frame_a` is `NaN` on `frame_a`'s rows, and vice versa; the
shared column is never `NaN`. Then build two frames with partially
overlapping **index labels** and `pd.concat([...], axis=1)`: assert the
combined shape and exactly which cells are `NaN` this time.

## Exercise 8 — melt → pivot round trip (`wide`)

`wide` has `student_id`, `math`, `reading`, `science`. `.melt(id_vars=
'student_id', var_name='subject', value_name='score')` gives 9 rows (3
students × 3 subjects). `.pivot(index='student_id', columns='subject',
values='score')` should bring back the original — but you will need to
`.reset_index()`, drop the columns' index name, and reorder the columns
back to `wide`'s original order before `pd.testing.assert_frame_equal`
passes, since `pivot` sorts columns alphabetically.

## Exercise 9 — `pivot` versus `pivot_table` (`dup_index_col`)

`dup_index_col` has two rows for `('Ann', 'math')` — scores 80 and 90.
`.pivot(index='student', columns='subject', values='score')` cannot place
both, and must raise `ValueError`. `.pivot_table(index='student',
columns='subject', values='score', aggfunc='mean')` aggregates them
instead: assert Ann/math is `85.0` (the mean of 80 and 90), Ann/reading is
`91.0`, and Bo/math is `70.0`.

---

Prove your suite is not vacuous once you are green: re-break one assertion
on purpose (flip a comparison, change an expected number), confirm the run
exits non-zero with a printed `FAIL`, then restore it and confirm green
again.
