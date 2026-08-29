# What is exact everywhere, and what may differ on your machine

Every figure in this lab falls into one of two categories. Knowing which is
which tells you whether a different number on your machine means a bug or
just means you ran it.

## Exact everywhere — identical on any correct Python implementation

These are `fractions.Fraction` results, computed by exact rational
arithmetic. They cannot differ between machines, Python versions, or
operating systems, short of an actual bug.

- The opening posterior: `99/1098`, reduced to `11/122` (`~0.09016393...`).
- The natural-frequency table: `TP=99`, `FP=999`, `TN=98901`, `FN=1`,
  `1098` total positives.
- The prevalence-sweep values, including the exact `0.99` at prevalence
  `1/2`.
- The odds-form values: prior odds `1/999`, likelihood ratio `99`,
  posterior odds `11/111`.
- The sequential two-test posterior: `1045/1267` (`~0.82478...`).
- Both correlated-test posteriors: naive `363/400` (`0.9075` exactly),
  correct `2189/13400` (`~0.16336`).
- Every Naive Bayes word count, word probability and document score in
  exercise 8, since the toy corpus and `Fraction`-based arithmetic are
  fixed and exact.
- The underflow result in exercise 9: `500` factors of `0.01` multiplied as
  `float64` are IEEE-754-deterministic and underflow to exactly `0.0` on
  every machine that implements the standard correctly. The sum of logs,
  `-2302.5850929940457`, is likewise IEEE-754-deterministic.

## Sampled — may differ on another machine, another seed, or another NumPy version

- **Exercise 3's simulated posterior.** Captured on this run at
  `n = 2,000,000`, seed `42`: true positives `1,978`, false positives
  `20,069`, empirical posterior `0.089717...`, against an exact value of
  `0.090164...` — a gap of about `0.00045`, comfortably inside the
  3-standard-error tolerance of about `0.00579` at that many positive
  results. NumPy's `default_rng` is reproducible for a *fixed* NumPy
  version and seed, but is not guaranteed bit-identical across major NumPy
  releases; the test asserts the gap is within tolerance, never the exact
  simulated counts.
- No other exercise in this lab depends on simulation. Exercises 1, 2 and
  4 through 9 are exact `Fraction` or IEEE-754-deterministic arithmetic
  throughout.

## A correction this lab made, and is not hiding

An earlier draft of this lab's brief stated that 500 factors of `0.01`
collapse in log space to "about -1151.29". That figure is wrong for 500
factors of `0.01` — the correct value, computed directly and shown in
`09-log-space.txt`, is `-2302.585...` (`500 * ln(0.01)`). `-1151.29` is
what 500 factors of `0.1` produce instead (`500 * ln(0.1)`), or
equivalently 250 factors of `0.01`. Every figure in this lab's code, tests
and lesson uses the measured, correct value for 500 factors of `0.01`, not
the draft figure. `dataset.py`'s `UNDERFLOW_LOG_SUM` constant is computed
by `math.log`, not copied from anywhere.
