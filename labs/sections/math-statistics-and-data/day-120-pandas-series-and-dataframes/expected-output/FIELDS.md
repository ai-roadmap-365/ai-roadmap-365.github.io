# What must match, and what may legitimately differ

Everything in this directory was captured from a real run on the machine
this lab was written on: macOS (Apple Silicon, arm64), Python 3.14.0,
pandas 3.0.5, pyarrow 25.0.1, NumPy 2.5.2, inside this lab's own `.venv`.

## Version-specific to pandas 3.0.5 — would differ on pandas 2.x

These are the whole point of this day, so they are called out individually
rather than buried in a general disclaimer.

- **`pd.Series(['a', 'b']).dtype` reads `str`.** On any pandas 2.x release
  this reads `object`. Both are correct for their version; the lesson and
  this lab are written against 3.0's new default.
- **Chained assignment (`df[mask]['col'] = value`) raises a
  `ChainedAssignmentError` warning and leaves the original frame
  unchanged.** Copy-on-Write is unconditional starting in pandas 3.0. On
  pandas 1.x this same statement sometimes silently worked and sometimes
  silently did not, depending on internal memory layout, with only an
  inconsistent `SettingWithCopyWarning` as a hint. On pandas 2.x with
  Copy-on-Write opted into manually, behaviour matches what this lab shows;
  with it left off (2.x's default), results depend on the same
  unpredictable internal layout 1.x had.
- **Setting `pd.options.mode.copy_on_write` now only emits a deprecation
  warning and does nothing.** On pandas 2.x that same line actually toggled
  the feature. On pandas 4.0 (not yet released as of this writing) the
  option is expected to be removed outright.
- **`.memory_usage(deep=True)` equals `.memory_usage(deep=False)` for a
  `str`-dtype column.** This is new in 3.0: the PyArrow-backed string
  storage has no pointer indirection left for `deep=True` to discover. On
  the legacy `object` dtype (still reachable with `dtype="object"`),
  `deep=True` still reports substantially more bytes than `deep=False`, as
  it always has.
- **`.info()`'s dtype column prints `str` rather than `object`** for a
  string column, following the same 3.0 default.

## Would differ by machine, but not by pandas version

- **The exact ratio in `07_vectorized_vs_apply.py`.** This run measured
  roughly 250x on 200,000 rows on one Apple Silicon Mac on one day. The
  test only asserts the ratio is at least 20x, which is comfortably below
  what any modern machine should measure for this comparison — it is a
  shape assertion, not a timing assertion.
- **`platform.platform()`'s exact string** in `expected-output/test-run.txt`
  (architecture, OS build number).
- **Byte counts from `memory_usage()`** may shift by a small constant
  amount across platforms with different pointer widths or allocator
  padding, though the *relationship* between `str` and `object` columns
  (equal under `deep=True` vs. not) will not.

## Would NOT differ — exact on any correctly-installed pandas 3.0.5

- Every alignment result (which labels become `NaN`, the summed values on
  matching labels).
- The dtype promotion from `int64` to `float64` on `reindex`, and the exact
  precision loss past `2**53`.
- `.loc['b':'d']` versus `.iloc[1:3]` row counts.
- `.describe()`'s count, mean, min, max and Bessel-corrected standard
  deviation on the fixed eight-value column — these are closed-form
  arithmetic on fixed inputs.
- `float('nan') != float('nan')`, and `series == np.nan` being all-`False`
  — both are IEEE 754 facts pandas inherits from NumPy and Python, not
  pandas-version-dependent at all.
