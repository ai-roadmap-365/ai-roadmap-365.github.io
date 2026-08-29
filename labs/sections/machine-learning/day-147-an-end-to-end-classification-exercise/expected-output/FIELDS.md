# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened to
come out a certain way. Check 9 of the harness confirms the directional
ones at seeds this lab does not quote.

- **The three datasets' shapes, class counts and majority baselines** in
  exercise 1. `load_iris`, `load_wine` and `load_breast_cancer` are bundled
  data, not samples — their row and feature counts do not depend on any
  seed. The majority-class baseline at a fixed split is also deterministic
  once the split itself is deterministic.
- **The standard-error formula in the verdict.** `sqrt(p(1-p)/n)` is
  arithmetic, not a measurement.
- **Cross-validation selecting on train rows only, and never on test
  rows.** Structural, by construction of `select_best`.
- **`TestSetTouchedTwice` on a second evaluation, and the counter not
  advancing on a refused attempt.** Branching logic, asserted mechanically
  by check 7 of the harness with five repeated refused attempts.
- **The leaky score never being lower than the honest score, at any
  seed.** The leaky search considers the honest winner among its 36
  candidates and can only replace it with something that scored at least
  as well on the test rows it was allowed to peek at.

## Exact under these pins, and only these

Everything else depends on NumPy's `default_rng` and `RandomState` bit
streams (both are used, indirectly, through scikit-learn's
`random_state=` parameters) and on scikit-learn's estimator internals.
**NumPy's own documentation states that `Generator` carries no
stream-compatibility guarantee across versions**, so seeding makes these
reproducible under the pins in `requirements/requirements.txt` and not
beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| `455` train rows, `114` test rows | 3 | the stratified 80/20 split at seed 0 |
| `0.6316` | 2 | majority-class baseline, test accuracy |
| `('logreg', 1)`, `0.978` | 5 | the winning configuration and its 5-fold CV accuracy |
| `0.9825` | 6 | the one permitted test evaluation |
| `0.0326` | 7 | the predicted selection optimism from Day 144's formula |
| `-0.0001` mean, `0.0149` sd, `0.033` mean predicted, `0.5` fraction positive | 7b | the 20-seed distribution of predicted versus measured optimism |
| `[[40, 2], [0, 72]]`, `2` false negatives, `0` false positives | 8 | the confusion matrix |
| `0.0123` se, `0.0241` half-width, `(0.9584, 1.0066)` | 9 | the verdict interval |
| `0.9825` leaky score at seed 0 | 10 | selecting by peeking at the test set |
| `0.0096` mean gap, `0.0103` sd, `0.0` min, `0.0351` max | 10b | the 20-seed leaky-gap distribution |

## Sampled, and therefore soft even here

- **The predicted-vs-measured optimism comparison in exercise 7b is
  averaged over 20 seeds**, for the reason Day 144 gave for averaging over
  400 replications: one draw of a noisy quantity is an anecdote. At any
  single seed the measured drop can be positive or negative — it was
  negative at the headline seed (−0.0045) and the 20-seed mean is close to
  zero (−0.0001), while the naive prediction is a consistent 0.03-ish
  overestimate at every seed tried.
- **The leaky-gap distribution in exercise 10b is likewise averaged over 20
  seeds.** At any one seed the gap can be exactly zero — a ceiling effect,
  because 114 test rows only support accuracy in steps of about 0.0088,
  and the honest and leaky searches sometimes land on the same
  configuration outright. The structural claim that survives every seed
  is the direction: never negative.
- **The winning configuration itself, `LogisticRegression(C=1)`, is a
  property of seed 0.** At other seeds in the 20-seed sweep the winner is
  sometimes `knn` at a different `k`, always drawn from the same 36
  candidates; the harness does not assert the same winner across seeds
  because Day 145 already established that near-tied configurations trade
  places under resampling.

## Timings

No timing is asserted anywhere in this lab. On the capture machine, one
seed's frame-to-verdict pipeline (baseline, sweep, cross-validate, select,
one test evaluation) completed in roughly 0.32 to 0.38 seconds across three
repeated measurements; the 20-seed comparisons in exercises 7b and 10b,
which each cross-validate all 36 candidates 20 times over, take roughly 7
to 9 seconds apiece, and the full `report_measurements.py` run — which
performs both 20-seed sweeps — completes in well under 30 seconds. All of
this runs on the CPU; no GPU is present, needed, or used.
