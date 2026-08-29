# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` —
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened
to come out a certain way. Check 8 of the harness confirms the directional
ones at seeds the lesson does not quote.

- **The theoretical standard errors in exercise 6.** `sqrt(p(1-p)/n)` is a
  formula. `0.0505`, `0.0357`, `0.0252`, `0.0160`, `0.0113` and `0.0050`
  are what it evaluates to, on any machine, forever. So are the derived
  `1225` and `4899` row counts.
- **Quadrupling the test set halves the standard error.** The ratio at
  n=200 against n=50 is exactly 0.5, because the formula goes as one over
  root n. Not an observation.
- **`50 of 50` people appearing in both halves of a row-wise split.** With
  twenty rows per person and a random quarter held out, the chance of any
  one person having all twenty rows land on the same side is about two in
  a hundred thousand. This is a near-certainty, not a coincidence, and the
  harness asserts it.
- **The test column staying at chance in exercise 1.** The test scores are
  never selected on, so their expectation is exactly 0.5 for every K. The
  measured values wander within about 0.003 of it; the *absence of a
  trend* is the structural fact.
- **The validation column increasing in K.** The maximum of a larger
  sample of draws from the same distribution is stochastically larger.
  This holds for any distribution and any K.
- **`sqrt(2 ln K)` exceeding the simulated expected maximum** at every K
  tried. The asymptotic is an upper bound that is loose at finite K, and
  the lab asserts the inequality rather than a gap size.
- **`TestSetTouchedTwice` on the second evaluation**, and the counter not
  advancing on a refused attempt. Branching logic.
- **Group leakage inflating the score, and stratification narrowing the
  spread.** The directions, not the sizes. Harness check 8 re-runs both at
  several dataset seeds.
- **The shuffled split beating the chronological one in all 20 temporal
  constructions.** See the honesty note below about the size.

## Exact under these pins, and only these

Everything else depends on NumPy's `default_rng` bit stream and on
scikit-learn's estimator internals. **NumPy's own documentation states
that `Generator` carries no stream-compatibility guarantee across
versions**, so seeding makes these reproducible under the pins in
`requirements/requirements.txt` and not beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| the nine rows of the selection-bias curve | 1 | mean selected-validation and test scores at each K |
| `2.57` standard errors at K=100, and `2.50` simulated | 1c | the measured optimism against the expected maximum |
| `{'mean': 0.0504, 'sd': 0.0265, 'min': 0.0, 'max': 0.16}` | 2 | random-split positive rates |
| `{'mean': 0.05, 'sd': 0.01, 'min': 0.04, 'max': 0.06}` | 2 | stratified-split positive rates |
| `21` of 500 | 2 | random splits whose test half held no positives |
| `0.9760`, `0.4112`, `+0.5648` | 3 | row-wise against group-aware |
| `0.5961`, `0.5233`, `0.5235` | 4 | shuffled, chronological and baseline means |
| `0.0728`, `0.0596`, `0.016`, `0.2557` | 4 | the temporal inflation distribution |
| `{'mean': 0.7519, 'sd': 0.0381, 'min': 0.66, 'max': 0.85}` | 5 | single-holdout spread |
| `{'mean': 0.7546, 'sd': 0.0061, 'min': 0.7375, 'max': 0.77}` | 5 | 5-fold spread |
| `6.2344` | 5 | how much steadier cross-validation is |
| the measured column of the test-size table | 6 | 20000 binomial draws at each n |
| `0.7575` | 7 | the gated test set's one permitted evaluation |

## Sampled, and therefore soft even here

- **The selection-bias curve is averaged over 400 replications** and the
  temporal comparison over 20 constructions, for the reason Days 117-118
  established: one draw of a noisy quantity is an anecdote. A single
  replication of exercise 1 at K=1000 produced anything from +0.02 to
  +0.12 while this lab was being built.
- **The temporal effect in exercise 4 varies by a factor of sixteen across
  constructions** — from +0.016 to +0.2557. This is the honesty call that
  matters most in this lab. The first construction tried gave +0.1428, and
  quoting it alone would have been the forking-paths problem inside a
  lesson against exactly that. The lab reports the mean, the standard
  deviation, the minimum and the maximum, and asserts the one thing that
  held every time: the direction.
- **`0.4112` in exercise 3 is below chance** and is not evidence of
  anti-learning. Twelve or thirteen people land in the group-aware test
  half, each contributing twenty identical labels, so the estimate is
  built from about a dozen independent coin flips. It wanders. The
  structural claim the lab asserts is that it sits below 0.5 while the
  row-wise score sits far above it.
- **`0.0505` and `0.0505` agreeing exactly in exercise 6** is a happy
  rounding, not a guarantee. The lab asserts agreement to within 0.0002,
  which is what 20000 draws supports.

## Timings

No timing is asserted anywhere in this lab. The heaviest steps are the 400
selection replications and the 200 cross-validation repeats, which take a
few seconds here and will take longer elsewhere without changing a single
assertion, because every assertion is about a shape or a value.
