# What must match, and what may legitimately differ

Everything in this directory was captured from a real run on the machine
this lab was written on: macOS (Apple Silicon, arm64), Python 3.14.0,
pandas 3.0.5, pyarrow 25.0.1, NumPy 2.5.2, inside this lab's own `.venv`.

## Version-specific to pandas 3.0.5 — would differ on pandas 2.x

These are called out individually rather than buried in a general
disclaimer, because exercise 5 is built directly on the difference.

- **`.str.contains()` on a missing entry in a pandas-3.0 `str`-dtype
  column returns a plain `False`, and the resulting mask's own dtype is
  `bool` with no missing values in it at all.** This is new in 3.0. On
  any pandas release before 3.0, a plain list of Python strings defaulted
  to `object` dtype, and `.str.contains()` on that dtype's missing entries
  returns `None`, reproducing the trap this exercise demonstrates on
  `object` dtype specifically, by default, with no need to force the
  dtype at all.
- **`.str.contains()` on a missing entry in an `object`-dtype column
  still returns `None`, and filtering with that mask still raises
  `ValueError: Cannot mask with non-boolean array containing NA / NaN
  values`.** This part is unchanged by the 3.0 release; `object` dtype is
  reachable on any pandas version with `dtype="object"`, and this lab
  demonstrates the trap against it deliberately, on top of showing that
  the pandas-3.0 default no longer needs the same care.
- **`na=False` fixes both cases identically.** This has not changed
  across pandas versions and is the one fact in exercise 5 that is not
  version-specific.

Every other exercise in this lab (1–4, 6–9) tests behaviour that is not
tied to the pandas 3.0 release specifically — index alignment, the
`and`/`&` distinction, operator precedence, `.query()`, `.isin()`,
`.nlargest()`/`.nsmallest()`, and `.drop_duplicates()` have worked
identically since well before 3.0 and are expected to reproduce on any
reasonably current pandas 2.x install too, though this lab was only
verified against 3.0.5.

## Would differ by machine, but not by pandas version

- **`platform.platform()`'s exact string** in `test-run.txt` (architecture,
  OS build number).
- **The exact `UserWarning: Boolean Series key will be reindexed to match
  DataFrame index` line's file path** in `04-mask-alignment.txt` — the
  path is where this lab happens to sit on disk. It has been sanitized to
  `<repo>/...` in the captured file here; on your machine the real
  absolute path will appear instead. The warning text and line number
  after the colon are stable.

## Would NOT differ — exact on any correctly-installed pandas 3.0.5

- The partition-invariant counts: 3 high, 3 low, 2 missing, 8 total, and
  the exact index labels in each group.
- Which comparisons raise `ValueError` (`and`, `or`, the unparenthesised
  precedence trap) and the exact wording of that error message — it comes
  from NumPy/pandas' `__bool__` implementation, not from anything this
  lab computed.
- The mask-alignment result: which row labels a reordered mask selects
  when applied to the original frame, and which (wrong) rows the same
  booleans select when applied positionally via `.to_numpy()`.
- `.query()` and the equivalent mask selecting the identical rows, for
  both a single and a compound condition.
- `.isin()` matching a chain of `==`/`|` exactly, and `.isin([])`
  returning zero rows.
- `.nlargest(2, keep='all')` returning 3 rows on the fixed tied-score
  table, versus `.sort_values().head(2)` returning exactly 2.
- `.drop_duplicates()`'s row counts and surviving index labels for each
  `subset` choice on the fixed six-row orders table.
- `.filter(items=[0, 1, 2])` matching zero columns and keeping every row,
  demonstrating that `.filter()` never touches row selection.
