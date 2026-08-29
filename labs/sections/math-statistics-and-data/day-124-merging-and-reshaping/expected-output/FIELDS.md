# What in this directory is version-specific to pandas 3.0.5

Captured on macOS, Python 3.14.0, pandas 3.0.5, pyarrow 25.0.1, NumPy
2.5.2, pytest 9.1.1, on 2026-08-19.

## Will differ on another machine, and that is fine

- **pytest's run duration line** (`22 passed in 0.05s` — the count is
  fixed, the seconds are not).
- **`platform darwin`** in `examples-run.txt` and `starter-run.txt` — a
  Linux or Windows run reports its own platform string there instead;
  nothing about the test results depends on it.

## Would differ on an earlier pandas major version, and that is the point

- **Exercise 4's `str_keyed['id']` dtype and the plain-string-key raise.**
  This is the biggest version-specific finding in this lab. On pandas
  3.0.5, a column built from a plain Python `list[str]` infers to
  pandas' own new `str` extension dtype by default (`pandas.StringDtype`,
  printed as `str`), not the historical `object` dtype earlier pandas
  versions would have used. More importantly for this lesson: pandas
  3.0.5's `merge()` explicitly checks for an incompatible key dtype pair
  (a numeric key against a string-like key) **before** joining, and
  raises `ValueError: You are trying to merge on int64 and str columns
  for key 'id'. If you wish to proceed you should use pd.concat` rather
  than silently returning zero rows. Earlier pandas versions (and this
  lab's `str_keyed` fixture, deliberately built as a `pandas.Categorical`
  instead) still reproduce the classic silent failure — a categorical key
  is not caught by that same check, so an int64-vs-categorical merge
  returns 0 rows with no exception and no warning at all. Do not assume
  either behaviour without checking the installed pandas version; this
  lab's exercise 4 tests both cases directly rather than picking one.
- **`validate=`**'s four modes (`'one_to_one'`, `'one_to_many'`,
  `'many_to_one'`, `'many_to_many'`) and `pandas.errors.MergeError` have
  been stable pandas API for a long time; nothing about exercise 2 is new
  to 3.0.5, but it is included here because it is the day's central
  claim and worth confirming directly rather than assuming.
- **`pytest examples starter` in one invocation.** This was tested
  directly in this lab (not merely assumed from the shared authoring
  brief) and does not silently let one directory's `test_merge.py`
  shadow the other's — it aborts collection outright with an `import
  file mismatch` error and pytest exits non-zero before running anything.
  Whether a given pytest version reports a hard collection error or a
  softer silent shadow can depend on pytest's own version and rootdir
  configuration; either failure mode is a reason never to combine the
  two directories in one command, and this lab's README and
  troubleshooting guide describe the error actually observed here rather
  than assuming the softer failure mode.

## Will not differ, because they are exact arithmetic on fixed literals

Every other captured value — the exploded row count in exercise 1 (14,
with 6 from key A and 8 from key B), the `MergeError` raises and passes in
exercise 2, the `indicator=True` counts in exercise 3 (`left_only=1`,
`right_only=1`, `both=3`), the four join-type row counts in exercise 5
(`inner=3`, `left=4`, `right=4`, `outer=5`), the suffix behaviour in
exercise 6, the exact `NaN` placement in exercise 7's two `concat` calls,
the melt/pivot round trip in exercise 8, and the `pivot`/`pivot_table`
contrast in exercise 9 (`85.0`, `91.0`, `70.0`) — are exact arithmetic
over the fixed literal tables in `data.py`, and will reproduce identically
on any machine running pandas 3.0.5 with the same input.
