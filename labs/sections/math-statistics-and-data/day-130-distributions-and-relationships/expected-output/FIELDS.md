# What in these captures is exact, and what may differ

Captured from a real run on 2026-08-20, in this lab's own `.venv`, on
seaborn 0.13.2, matplotlib 3.11.1, pandas 3.0.5, NumPy 2.5.2, pytest
9.1.1, Python 3.14.0, macOS (arm64). scipy is not installed.

## Exact everywhere on this exact pin set

- `examples-run.txt` ends with `9 passed`, `starter-run.txt` ends with
  `9 skipped` — both counts are structural (9 test functions in each
  file) and do not depend on the machine.
- `test-run.txt` ends with `16 checks, 0 failure(s)` and exit 0.
- Exercise 5's five target control points -- `10.0`, `28.0`, `40.0`,
  `52.0`, `70.0` -- are hand-picked literals in `data.py`
  (`target_five_number_summary`), not sampled, and are exact on any
  correctly installed NumPy.
- Exercise 5's two samples (`matched_quartile_pair`) are built from a
  deterministic piecewise-linear function evaluated at 240 evenly spaced
  ranks with **no randomness at all** — their five-number summaries
  (`[10.21, 28.02, 40.0, 51.98, 69.79]` for the bimodal sample, `[10.17,
  28.06, 40.0, 51.94, 69.83]` for the unimodal one) and their mode counts
  at 15 bins (2 and 1 respectively) are exact on any machine.
- Exercise 6's ECDF median matches `numpy.median` to `1e-9` by
  construction: `ecdf_sample` has an odd length (301), so the median is a
  single real observation and not an average of two, and the assertion
  checks this exactly rather than approximately.
- Exercise 9's max jitter shift (`0.1499...`) is always `<=` the stated
  jitter width (`0.15`) by construction of `numpy.random.uniform`'s
  bounds, on any machine.
- Exercise 2's bin-count disagreement (`sturges=10 scott=14 fd=21`) is
  deterministic given the fixed seed in `skewed_for_bin_rules` and is
  exact on this NumPy version; NumPy's `histogram_bin_edges` formulas
  for these three rules are stable across NumPy versions, so this should
  reproduce identically on other NumPy 2.x releases too, though only the
  seed-42 numbers above were directly verified here.

## Version-specific or sampled, checked directly rather than assumed

- Exercise 1's bimodal sample (`bimodal_for_binning`, means 40 and 54,
  sd 8, seed 42) is a random draw. The specific mode counts reported —
  1 mode at 5 bins, 2 modes under Freedman-Diaconis (13 bins on this
  draw), 23 spurious modes at 100 bins — are exact on NumPy 2.5.2 with
  this seed and are expected to reproduce identically on any correctly
  installed NumPy 2.x, since `default_rng`'s bit generator is part of
  NumPy's stable public API; only the seed-42 draw itself was directly
  verified here.
- Exercise 3's KDE mode counts (2 at `bw_adjust=1.0`, 1 at
  `bw_adjust=3.0`) depend on seaborn's internal bandwidth-selection code
  and are specific to seaborn 0.13.2. seaborn's own KDE implementation
  changed between major versions historically; this exact pair of
  `bw_adjust` values was chosen and verified against seaborn 0.13.2
  specifically.
- Exercise 4's fraction of KDE mass below zero (`0.0954`, about 9.5%)
  depends on both the exponential draw (`positive_for_kde_boundary`,
  seed 9) and seaborn's default bandwidth rule; it is reported here as
  "a real, non-trivial fraction" (the lab's actual assertion threshold is
  a much looser `> 0.03`) rather than as an exact figure to reproduce.
- Exercise 7's overplotting numbers (`6988` distinct pixel positions out
  of `20000` points, `34.94%`; hexbin max bin count `210`) depend on
  exact pixel-transform behaviour of matplotlib's `Agg` backend at a
  specific figure size and DPI (`figsize=(3, 3), dpi=72`). Sub-pixel
  rounding could plausibly shift this by a handful of pixels on a
  different matplotlib build; the lab's actual assertion (`fraction <
  0.5`) is comfortably clear of that margin.
- Exercise 8's numbers (`pearson r=-0.0044`, `spearman r=-0.0226`,
  `R^2=0.9907`) depend on the fixed seed in `quadratic_relationship`
  (seed 5) and are exact on this NumPy version; see the honesty note
  below about what this pair of numbers actually shows.

## An honesty note on exercise 8's Spearman correlation

The day brief that this lab was written from suggested demonstrating "a
strong non-linear relationship with a near-zero correlation" where
"Spearman or a fitted quadratic reveals it." Measured directly: for
`quadratic_relationship`'s sample (`x` uniform on `[-10, 10]`, `y = x**2
+ noise`), Spearman's correlation is **also** near zero (`-0.0226`,
essentially the same magnitude as Pearson's `-0.0044`), because the
parabola is symmetric around `x = 0` and therefore has no monotonic
component for a rank correlation to detect either — a symmetric U-shape
defeats both Pearson and Spearman equally. Only the fitted quadratic
(`R^2 = 0.9907`) or looking directly at the scatter reveals the
relationship. This is reported as measured, because it is a sharper
version of the day's actual argument (plot before computing a
coefficient) rather than a weaker one, and changing the sample to make
Spearman succeed would have hidden a genuinely interesting fact about
rank correlation's own blind spot.
