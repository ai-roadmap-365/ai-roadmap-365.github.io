# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, pyarrow, NumPy and
  pytest from PyPI into this lab's own `.venv`. Every script and test
  after that runs completely offline.
- Writes only inside its own `.venv` directory (created by you, via
  `python3 -m venv .venv`) and transient `__pycache__` / `.pytest_cache`
  directories that the test harness removes both before and after every
  run.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every table is a small literal built by hand in `data.py` — `left_dup`,
`right_dup`, `left_keys`, `right_keys`, `int_keyed`, `str_keyed`,
`price_left`, `price_right`, `wide` and `dup_index_col` are each a dozen
or fewer rows invented for the exercises. Nothing here is real personal,
financial or otherwise sensitive data, and nothing is downloaded from any
external dataset.

## The design point this day is actually about

`merge()` will silently multiply your row count whenever a join key is
duplicated on both sides — a many-to-many join is a Cartesian product
within each key group, by definition, and pandas raises nothing to warn
you. `validate=` turns a stated cardinality assumption into an enforced
one: pass `validate='one_to_one'` (or `'one_to_many'`) and pandas raises
`MergeError` the instant the assumption is false, instead of silently
returning a frame with the wrong number of rows.

The lab's exercise 4 is the same discipline applied to dtypes. A key read
one way (an `int64` column) and the same values read another way (a
`str` or categorical column) look identical when printed and can fail a
join with zero warning — or, as this run measured on pandas 3.0.5, with
a loud `ValueError` in the plain-string case and continued silence only
in the categorical case. Either way, the fix is the same: check the
dtypes before trusting the join, and prefer `validate=` on every merge
where the row count matters.
