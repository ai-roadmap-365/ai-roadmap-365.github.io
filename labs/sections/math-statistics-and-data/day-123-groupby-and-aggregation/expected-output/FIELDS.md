# What in this directory is version-specific to pandas 3.0.5

Captured on macOS, Python 3.14.0, pandas 3.0.5, pyarrow 25.0.1, NumPy
2.5.2, pytest 9.1.1, on 2026-08-19.

## Will differ on another machine, and that is fine

- **Exercise 8's timing numbers** (`apply_seconds`, `builtin_seconds`, the
  measured ratio). This machine measured roughly 10-15x; the lab asserts
  only `ratio >= 3.0`, a conservative floor, never a millisecond figure.
  A different machine, a busier machine, or a different pandas build's
  internal C paths can all shift the exact ratio while leaving the
  asserted floor easily clear.
- **pytest's run duration line** (`20 passed in 0.06s` — the count is
  fixed, the seconds are not).
- **`platform darwin`** in `examples-run.txt` and `starter-run.txt` — a
  Linux or Windows run reports its own platform string there instead;
  nothing about the test results depends on it.

## Would differ on an earlier pandas major version, and that is the point

- **Named aggregation's output columns being flat** (exercise 3d,
  `test_3_agg_named_aggregation_gives_flat_columns`). Named aggregation
  itself (the `agg(name=(column, func))` syntax) was added in pandas
  0.25 and has produced flat columns since; nothing here is 3.0-specific,
  but it is included because almost every list/dict `.agg()` call
  produces a `pandas.MultiIndex` instead, which is the contrast the test
  exists to make concrete.
- **`include_groups=False`** in exercise 9's `apply` call
  (`weighted.groupby("region").apply(weighted_mean, include_groups=False)`).
  This keyword was added in pandas 2.2 to silence a deprecation warning
  about the grouping columns being included in the group passed to
  `apply`; on pandas older than 2.2 the keyword does not exist and must
  be omitted, and the applied function then receives the `region` column
  too (harmless here, since `weighted_mean` never reads it, but worth
  knowing about before copying this pattern elsewhere).
- **`observed=` defaulting to `False`** for a categorical `groupby` is
  pandas' long-standing behaviour through 2.x; pandas 2.1 announced this
  default would change to `True` in a future major version, and as
  of 3.0.5 it has **not** changed — `observed=False` is still the default
  measured here. Exercise 7 states this explicitly rather than assuming
  either default; do not rely on the default silently flipping on a
  version newer than the one pinned in `requirements/requirements.txt`.

## Will not differ, because they are exact arithmetic on fixed literals

Every other captured value — the reconciliation gap (170.0), the
`size`/`count` disagreement (2), every `.agg()` result in exercise 3, the
`.filter()` survivor count (9), the `MultiIndex` values in exercise 6, the
`observed=` row counts (20 and 9), and the weighted means in exercise 9
(17.5, 13.0, 60.0) — are exact arithmetic over the fixed literal tables in
`data.py`, and will reproduce identically on any machine running pandas
3.0.5 with the same input.
