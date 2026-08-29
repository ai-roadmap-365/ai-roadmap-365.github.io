# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64, CPU only -- no
GPU is needed or used), Python 3.14.0, in this lab's own `.venv` built
from `requirements/requirements.txt` -- numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, with scipy, joblib and threadpoolctl pulled in as
scikit-learn's own dependencies (this lab imports none of them directly).

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened
to come out a certain way. Check 9 of the harness confirms the
directional ones at seeds this lab does not quote.

- **The dataset's shape, feature names, and target range** in exercise 1.
  `load_diabetes` is bundled data, not a sample drawn at run time -- its
  row and feature counts, and the target's min, max and mean, do not
  depend on any seed.
- **`fetch_california_housing`'s `download_if_missing` default being
  `True`.** A fact about the function's signature, not a measurement.
- **The RMSE, R2 and MAE formulas.** Arithmetic, not measurements.
- **Cross-validation selecting on train rows only, and never on test
  rows.** Structural, by construction of `select_best`.
- **`TestSetTouchedTwice` on a second evaluation, and the counter not
  advancing on a refused attempt.** Branching logic, asserted
  mechanically by check 7 of the harness with five repeated refused
  attempts.
- **The leaky RMSE never being worse (higher) than the honest RMSE, at
  any seed.** The leaky search considers the honestly selected winner
  among its 23 candidates and can only replace it with something that
  scored at least as well on the test rows it was allowed to peek at.

## Exact under these pins, and only these

Everything else depends on NumPy's `default_rng` and `RandomState` bit
streams (used, indirectly, through scikit-learn's `random_state=`
parameters, and directly in `margin_bootstrap_interval`'s own
`default_rng(seed)` call) and on scikit-learn's estimator internals.
**NumPy's own documentation states that `Generator` carries no
stream-compatibility guarantee across versions**, so seeding makes these
reproducible under the pins in `requirements/requirements.txt` and not
beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| `331` train rows, `111` test rows | 3 | the 75/25 split at seed 0 |
| `70.4637` RMSE, `-0.0001` R2 | 2 | the mean-predictor baseline |
| `('lasso', 1)`, `53.8958` | 5 | the winning configuration and its 5-fold CV RMSE |
| `56.5566` RMSE, `0.3557` R2, `45.2846` MAE | 6 | the one permitted test evaluation |
| `[5.5852, 22.3324]`, margin `13.9071` | 7 | the bootstrap interval around the margin over baseline |
| `-3.6262` mean, `56.4402` sd, `0.2386` heteroscedasticity, `-0.1278` curvature | 8 | the residual-vs-fitted diagnostics |
| `0.9901` Q-Q correlation, five named largest residuals | 8b | the normal-probability check and the worst individual mistakes |
| `55.2464`, `57.8601`, `1.0473` | 9 | RMSE on the below- and above-median halves of the test targets, and their ratio |
| `55.5212` leaky RMSE at seed 0 | 10 | selecting by peeking at the test set |
| `0.5279` mean gap, `0.3686` sd, `0.011` min, `1.1451` max | 10b | the 20-seed leaky-gap distribution |
| `105.8797` half-width, `0.9459` coverage | 11 | the prediction interval and its realised coverage |

## Sampled, and therefore soft even here

- **The bootstrap interval on the margin (exercise 7) resamples the 111
  test rows 2000 times with a fixed `default_rng(0)`.** It is
  deterministic under this NumPy version because the algorithm's random
  draws are seeded and reproducible bit-for-bit, but a different NumPy
  version's `Generator` stream is not guaranteed to reproduce the same
  sequence, per NumPy's own documentation. The direction -- the interval
  excludes zero, so the model is distinguishable from baseline -- is the
  claim likely to survive a version change; the exact bounds may not.
- **The predicted-vs-measured leaky-gap distribution in exercise 10b is
  averaged over 20 seeds**, for the reason Day 144 gave for averaging
  over many replications: one draw of a noisy quantity is an anecdote.
  At any single seed the gap's size varies (0.011 to 1.1451 in this
  20-seed sweep); the structural claim that survives every seed is the
  direction -- never negative.
- **The winning configuration itself, `Lasso(alpha=1)`, is a property of
  seed 0.** Several nearby configurations -- `Lasso(alpha=0.3)` at
  53.9863, `Ridge(alpha=10)` at 54.0335, plain OLS at 54.0926 -- score
  within two-tenths of a point of the winner. Day 145's lesson about
  near-tied configurations trading places under resampling applies here
  too; the harness does not assert the same winner would hold at every
  seed.
- **The realised coverage of the prediction interval, 0.9459 at seed 0,
  is itself a sampled quantity on 111 test rows.** A separate 10-seed
  check (not asserted by the harness, reported here for context) gives a
  mean coverage of 0.9558, ranging from 0.9369 to 0.991 -- close to the
  0.95 nominal rate on any single seed, and closer still on average.

## Timings

No timing is asserted anywhere in this lab. On the capture machine, one
seed's frame-to-verdict pipeline (baseline, sweep, cross-validate,
select, one test evaluation, residual diagnostics, prediction interval)
completed in 0.1386 seconds; the 20-seed leaky-gap comparison in exercise
10b, which cross-validates all 23 candidates 20 times over, completed in
2.9559 seconds; the full `report_measurements.py` run, which performs
that 20-seed sweep and the 2000-draw bootstrap, completed in 3.99 seconds
of user CPU time (4.13 seconds wall-clock). All of this runs on the CPU;
no GPU is present, needed, or used. A slower machine will take longer;
nothing here asserts a threshold.
