# What may legitimately differ on your machine

Captured on 2026-08-17, macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
numpy 2.5.2, pytest 9.1.1.

## Exact on any correct implementation

These are exact arithmetic or exact rational/well-defined values and should
be **identical** on any machine, any OS, any NumPy version >= 2:

- The mean, median and mode of the fixed lists in exercise 1.
- The breakdown-point mean shift ($1,104,444.44 exactly, since the inputs
  are fixed integers) and the median shift ($0.00 exactly).
- Every value in the percentile-ambiguity table (exercise 4) — the input
  array and the target percentile are fixed, and `numpy.percentile`'s
  documented conventions are deterministic functions of the input.
- Pearson on the parabola (exactly `0.0`, by the symmetry of the inputs)
  and Spearman on the monotone cubic (exactly `1.0`).
- Every value in Anscombe's quartet table (exercise 6) — the dataset is
  the fixed, published 1973 data, not sampled.
- Every value in the Simpson's-paradox table (exercise 7) — fixed integer
  counts.

## Machine-dependent: seeded but still worth flagging

These depend on `numpy.random.default_rng(seed)`. NumPy's documentation
guarantees bit-for-bit reproducibility of a given `Generator` **algorithm**
across platforms for a fixed seed, so these should also match exactly on
any machine running the same NumPy major version (2.x) — but they are
listed here because they are draws from a random generator, not closed-form
arithmetic, and a future NumPy major version could in principle change the
default bit generator's stream.

- Exercise 3 (Bessel's correction): the measured ratio of the divide-by-n
  estimator to the true variance (this run: `0.8007`, against a predicted
  `0.8000`), and the divide-by-(n-1) estimator's distance from the truth in
  standard errors (this run: `0.17`).
- Exercise 8 (contamination): the clean and contaminated standard
  deviations and MADs, and their multipliers. **This run measured a 15.10x
  inflation in the standard deviation and a 1.00x change in the MAD** from
  3% contamination — reported in the lesson as "roughly 15x" and "barely
  moves" rather than as fixed literals, because a different NumPy version's
  random stream could shift these numbers slightly. The test suite asserts
  the multipliers against fixed floors and ceilings (`> 5.0x` for the
  standard deviation, `< 1.5x` for the MAD), not against these exact
  digits.
- Exercise 9 (standardisation): the measured Pearson correlation before and
  after standardising (this run: `0.9701497165` both times, differing by
  `3.33e-16` — floating-point noise, not a real difference).

## Not run in this environment at all

`scipy.stats` and `pandas.DataFrame.describe()` are **not installed here**.
Every claim about either in the lesson's Tools section is drawn from their
public documentation, not from a run, and is marked as such in the lesson
text.
