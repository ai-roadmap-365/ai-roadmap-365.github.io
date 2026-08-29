# What in these captures is exact, and what may differ

Captured from a real run on 2026-08-20, in this lab's own `.venv`, on
seaborn 0.13.2, matplotlib 3.11.1, pandas 3.0.5, NumPy 2.5.2, pytest
9.1.1, Python 3.14.0, macOS (arm64).

## Exact everywhere on this exact pin set

- `examples-run.txt` ends with `16 passed`, `starter-run.txt` ends with
  `16 skipped` — both counts are structural (16 test functions in each
  file) and do not depend on the machine.
- The four group means in exercise 2 — `79.0`, `70.0`, `67.5`, `57.5` —
  are arithmetic on a fixed, hand-written literal table (`team_scores` in
  `data.py`) and are exact on any correctly installed copy of pandas.
- `errorbar='sd'` in exercise 4 is a closed-form statistic (mean +/- one
  sample standard deviation), not a resampling procedure, so its extent
  is identical on any machine and does not depend on any seed.
- The `ValueError` in exercise 5 (asking a wide frame for columns it does
  not have) and the grid-shape numbers in exercise 6 (`(1, 5)` without
  `col_wrap`, `(2, 3)` with `col_wrap=3`) are structural and exact
  everywhere.
- The seven `rcParams` keys reported as changed by `sns.set_theme()` in
  exercise 8, and the exact values `axes.facecolor == "#EAEAF2"` and
  `axes.grid == True`, are seaborn's own fixed default theme and are
  exact on 0.13.2 specifically.
- `ax.patches` count (4, one box per team) and `ax.collections` count (4,
  one stripplot point cloud per team) in exercise 9 are structural.
- `17 checks, 0 failure(s)` and exit 0 from `tests/run_tests.sh`.

## Version-specific, checked directly rather than assumed

- The `MatplotlibDeprecationWarning: vert: bool was deprecated...`
  warning in both `examples-run.txt` and `test-run.txt` comes from
  seaborn 0.13.2's internal `ax.bxp(**boxplot_kws)` call still passing
  the now-deprecated `vert` keyword on matplotlib 3.11. It is a warning,
  not a failure — every test still passes — and is expected to disappear
  once seaborn ships a release built against matplotlib's newer
  `orientation=` argument. It is captured here rather than filtered out,
  because pretending the run was silent would not be honest.
- `sns.set_theme()`'s specific palette (`#EAEAF2`) and which of the seven
  watched `rcParams` keys change are properties of seaborn 0.13.2's
  default theme; an older or newer seaborn release could change the
  palette or the specific key set without changing the underlying claim
  (that `set_theme()` mutates global state and it is reversible).

## Sampled / random by construction, and exactly what "sampled" means here

- **Exercise 3 is the one place this lab expects runs to disagree.**
  `_barplot_errorbar_extents(team_scores)` with no `seed=` argument draws
  from `numpy`'s global random state via seaborn's bootstrap, so the
  precise upper/lower extents printed in any single capture are specific
  to that run's random draws. With only four observations per group, a
  bootstrap resamples from a small, discrete space, so any single PAIR
  of unseeded runs can coincidentally land on identical extents by
  chance — the reference test therefore draws six independent unseeded
  runs and asserts that not all six are identical, which is reliable in
  practice even though any two of the six, taken alone, occasionally
  agree. The *seeded* half of the same exercise (`seed=42` used twice) is
  exact and reproducible on any machine with the same seaborn/NumPy pin,
  because seaborn's `seed=` argument drives the same NumPy `Generator`
  deterministically.
- The specific bootstrap-CI extents shown for `errorbar=('ci', 95)` in
  exercise 4 are seeded (`seed=42`) and therefore exact and reproducible
  on this pin set, but would differ under a different NumPy version's
  random-number implementation even with the same seed value — NumPy
  does not guarantee bit-identical `Generator` output across major
  versions. This lab pins NumPy exactly for that reason.

## Machine-dependent

- Wall-clock timings inside pytest's own summary lines (`in 0.83s`,
  `in 0.03s`) will differ on any other machine and are not asserted on
  anywhere in this lab.
- The `.venv` path embedded in pytest's own `rootdir:` and platform
  banner lines has been sanitized to `<repo>` in these captures; on a
  fresh checkout it will show that checkout's own absolute path instead.
