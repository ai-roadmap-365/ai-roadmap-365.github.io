# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened
to come out a certain way.

- **The mean minimises squared error and the median minimises absolute
  error.** These are calculus facts (the derivative of sum-of-squares is
  linear in the candidate and zero at the mean; sum-of-absolute-values is
  minimised where equal counts of points sit on each side). The grid
  search in exercise 1 lands within its own resolution of the closed-form
  answer on any machine, because it is searching the same arithmetic.
- **Squared error's landscape is a parabola and absolute error's is
  piecewise linear**, for any dataset. Exercise 2's specific numbers are
  sampled (see below), but the *structural* fact — constant second
  differences for one, varying second differences for the other — holds
  for any x, y and any slope range.
- **The normal equations match `LinearRegression` to many decimal
  places.** Both solve the identical system `(X^T X) beta = X^T y`; one
  does it by hand with `numpy.linalg.solve` and the other through
  scikit-learn's LAPACK-backed solver. Harness check 8 confirms the
  agreement at three sample sizes the lesson does not quote.
- **OLS moves further than Huber, which moves further than the median
  fit, when a single point becomes an outlier.** This is squaring versus
  not squaring the residual: an 80-unit residual contributes 6,400 to a
  squared-error total and 80 to an absolute-error total, so the direction
  of "least squares reacts hardest" holds for essentially any outlier size
  and any underlying dataset. Harness check 8 re-confirms the ranking at
  five dataset seeds the lesson never quotes.
- **The Huber epsilon sweep is non-decreasing and converges to the OLS
  slope at large epsilon.** Structural: Huber's loss is squared error
  inside its threshold and (scaled) absolute error outside it, so raising
  the threshold can only move the fit toward the pure-squared-error
  answer, never away from it.
- **Gaussian errors favour OLS; heavy-tailed errors favour Huber.** The
  direction, not the exact ratio, is asserted at a different replication
  count (150 instead of 500) in harness check 8, so it is not an artefact
  of the specific replication count quoted in the lesson.

## Exact under these pins, and only these

Every sampled figure in this lab comes from `numpy.random.default_rng` or
from an iterative scikit-learn solver (`HuberRegressor`,
`QuantileRegressor`). **NumPy's own documentation states that `Generator`
carries no stream-compatibility guarantee across versions**, and a
solver's exact output can shift in its last few decimal places between
scikit-learn releases even at a fixed seed, because the stopping tolerance
is part of the library, not the seed. So these are reproducible under the
pins in `requirements/requirements.txt` and not guaranteed beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| grid argmin `23.39975` and `5.00005` | 1 | numerical grid search near the mean and median |
| sd of second differences `0.000000` and `1.9366` | 2 | the loss-landscape curvature measurement |
| normal-equations `slope=2.9779`, `intercept=4.9663` | 3 | on the specific 300-row seeded dataset |
| the outlier-shift table: `3.0465 -> 3.8010`, `2.987 -> 3.0308`, `2.9961 -> 3.0064` | 4, 4b | before/after slopes on the specific 60-row seeded dataset |
| the seven-row Huber epsilon sweep | 5 | slopes at each epsilon on the same contaminated dataset |
| `(2.998, 0.056, 2.9977, 0.0588)` under Gaussian errors | 6 | 500-replication mean and sd of each estimator's slope |
| `(2.9967, 0.0589, 2.9984, 0.0422)` under heavy-tailed errors | 6b | the same, with Student's t (df=3) errors |

## Sampled, and therefore soft even here

- **The outlier-shift and epsilon-sweep numbers are from one dataset
  (seed 1, 60 rows).** A different seed changes the exact decimals but not
  the ranking, which is what harness check 8 verifies across five seeds.
- **The efficiency-under-noise ratios (0.9524 and 1.3957) are averages
  over 500 replications.** A single replication is far noisier — early
  exploration while building this lab saw individual Huber slopes ranging
  from about 2.85 to 3.15 on one dataset alone. The mean and standard
  deviation over many replications is what makes the comparison
  meaningful, per Days 117-118.
- **`2.9977` and `2.9984`, Huber's mean slopes under Gaussian and
  heavy-tailed errors, sit slightly further from the true value of `3.0`
  than OLS's `2.998` does under Gaussian errors.** This is sampling noise
  in the mean of 500 draws, not evidence that Huber is biased; harness
  check 8 asserts both means stay within 0.01 of the truth at a shorter
  replication count too.

## The one honesty call this lab required

`HuberRegressor` and `QuantileRegressor` both had to be verified to exist
and converge in scikit-learn 1.9.0 before anything was built on them —
per the day's instructions, neither was assumed. Both converged without
warning on every dataset used here; `QuantileRegressor` is fit with
`solver="highs"` and `alpha=0.0` to disable the L1 regulariser it applies
by default, so it measures plain, unregularised absolute-error (median)
regression rather than a penalised variant. Penalised losses — ridge,
lasso and their relatives — are Day 151's subject, not this lab's.

## Timings

No timing is asserted anywhere in this lab. The heaviest step is the
1,000 model fits behind exercises 6 and 6b (500 replications, two
estimators each, in two error settings), which takes a few seconds here
and will take longer elsewhere without changing a single assertion,
because every assertion is about a shape or a value.
