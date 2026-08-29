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

## `pytest examples starter` aborts with `import file mismatch`

Do not pass both directories to one `pytest` invocation. `starter/` and
`examples/` both define a module named `test_merge.py`, and pytest imports
test modules by their dotted name. In this lab that collision does not
quietly let one directory's tests shadow the other — it aborts collection
outright with an `import file mismatch` error and pytest exits non-zero
before running a single test. Either way, the fix is the same: run them
as two separate commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## Exercise 1's expected row count is not 14

Recompute it from `left_dup['cust_id'].value_counts()` and
`right_dup['cust_id'].value_counts()` rather than hardcoding a number —
key `A` contributes `3 * 2 = 6` and key `B` contributes `2 * 4 = 8`. If
your total does not match, confirm you merged with `how='inner'` and on
`'cust_id'`, not some other column or join type.

## `MergeError` message does not mention "one_to_one" or "one_to_many"

You are reading the right exception, just from a different keyword than
you expected — `validate=` raises `pandas.errors.MergeError` (not
`ValueError`) for every one of its four modes (`'one_to_one'`,
`'one_to_many'`, `'many_to_one'`, `'many_to_many'`). Catch that specific
class, not a bare `Exception`.

## Exercise 4's dtype-mismatch merge does not return zero rows

Confirm `str_keyed['id']` is genuinely a `pandas.Categorical`
(`data.py`'s `build_str_keyed`), not a plain string column — pandas
3.0.5's `merge()` explicitly detects an int64-vs-string/object key
mismatch and **raises `ValueError`** rather than returning nothing; only
the categorical case slips past that check silently. If you built your
own plain-string frame for the third part of exercise 4, that one
**should** raise — that is the point of that test.

## Exercise 6's `on=` and `left_on=`/`right_on=` results do not match

Confirm you renamed only the column used for `left_on=`/`right_on=`
(`'sku'` to `'sku_code'` on the right side), and that you are comparing
the same rows and the same suffix pair between the two calls — a
different `suffixes=` argument between the two merges will produce
differently-named columns even though the values agree.

## Exercise 7's `concat` result has `NaN` in cells you did not expect

Check `axis=`: `axis=0` stacks rows and aligns by **column name** (a
column missing from one frame goes `NaN` on that frame's rows only);
`axis=1` stacks columns and aligns by **index label** (an index label
missing from one frame goes `NaN` in that frame's columns only). Mixing
up which axis you meant is the most common way to get a shape that looks
right with values in the wrong place.

## Exercise 8's round trip does not equal the original

`pivot` sorts its resulting columns alphabetically, which for `wide`'s
columns (`math`, `reading`, `science`) happens to already be alphabetical
order for the *subject* columns but still needs `student_id` reset out of
the index and back into first position, and the pivoted columns' `Index`
carries a `name` (`'subject'`) that `wide`'s own columns do not — drop it
with `.rename_axis(columns=None)` before comparing.

## Exercise 9's `pivot` does not raise

Confirm `dup_index_col` genuinely has two rows sharing the same
`(student, subject)` pair — `('Ann', 'math')` appears twice in `data.py`.
If you built your own test data and it has no duplicate pair, `pivot`
will succeed instead of raising, which is expected and correct given
that input; the assertion is about behaviour on duplicated pairs
specifically.

## `pip install` fails or hangs

You are offline, or a corporate proxy is blocking PyPI. This is the only
network-dependent step in the entire lab. Retry on a connection that can
reach `pypi.org`, or ask whoever manages your network for a mirror.
