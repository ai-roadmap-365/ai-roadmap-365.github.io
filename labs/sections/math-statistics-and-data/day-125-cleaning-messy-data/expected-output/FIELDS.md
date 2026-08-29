# What must match, and what may legitimately differ

Every value in `examples-run.txt`, `starter-run.txt` and `test-run.txt` was
captured from a real run on this machine on 2026-08-19, using
`python3 -m venv .venv` and `pip install -r requirements/requirements.txt`
exactly as `README.md` documents.

## Must match on any correctly installed pandas 3.0.5

Every assertion in this lab is over hand-written literal tables or a
seeded `np.random.default_rng`, never a live download and never a
timing. That means:

- **The exact test counts**: `examples/` — 19 passed. `starter/` (untouched)
  — 19 skipped. `tests/run_tests.sh` — 13 checks, 0 failure(s), exit 0.
- **Every numeric assertion** in `examples/test_cleaning.py` — the mean,
  standard deviation and correlation figures in exercise 1, the dropna row
  counts in exercise 3, the ffill values in exercise 4, the coercion count
  in exercise 6, the `nunique()` figures in exercise 7, the duplicate
  counts in exercise 8, and every contract check in exercise 9 — because
  every source table is either a fixed literal or built from a seeded
  generator with a pinned seed. Nothing here should differ between
  machines, operating systems, or pandas 3.0.x patch releases.

## Specific to this exact pandas version (3.0.5)

- `df.dtypes` printing `str` rather than `object` for text columns
  (visible in the contract test's dtype comparisons) is a pandas-3.0
  default, inherited from Day 120's dtype discussion. A pre-3.0 pandas
  would print `object` for the same column and the dtype-equality check in
  exercise 9 would need `"object"` instead of `"str"` as the expected
  value.
- `.str.replace('.', '', regex=False)` and `pandas.Categorical` behaviour
  are stable across recent pandas majors; nothing here is expected to
  differ on 2.x either, but it was only verified on 3.0.5.

## Machine-specific, and why it does not affect this lab

Nothing in this lab asserts a millisecond figure, a file path outside the
lab, or a byte count that would vary with disk block size — the one
common source of machine-specific drift in this course's other labs
(memory-usage ratios, timing ratios) does not appear in Day 125's
exercises at all. Every exercise here checks either an exact literal
value or a `pytest.approx` around a deterministic floating-point
computation.

## Honesty note carried from the lesson

Exercise 1's correlation assertion is intentionally the OPPOSITE direction
from a first guess ("mean imputation inflates correlation"). It strictly
**attenuates** the correlation, never inflates it, for the mathematical
reason given in `starter/00_brief.md` and the lesson's opening section:
an imputed value sits exactly at the column mean, so its deviation from
that mean is exactly zero, and a zero-deviation term can only dilute an
existing covariance, never add to it. This is provable algebraically from
the Pearson correlation formula and was independently confirmed
empirically here across 200 reseeded trials before this lab was written,
none of which produced an increase.
