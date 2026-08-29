# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64, **CPU only**),
Python 3.14.0, in this lab's own `.venv` built from
`requirements/requirements.txt` — numpy 2.5.2, scikit-learn 1.9.0,
pytest 9.1.1, with scipy 1.18.1, joblib 1.5.3 and threadpoolctl 3.6.0
pulled in as scikit-learn's own dependencies.

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened
to come out a certain way. Harness check 8 re-confirms the shape ones at
data seeds the lesson never quotes.

- **`4.0000` — the irreducible floor.** It is the square of the noise
  standard deviation this lab generates with, so it is a property of the
  data-generating process rather than a measurement of anything.
- **A degree-3 model fits the noiseless truth exactly.** The true function
  is a cubic, so the residual is zero to machine precision (`1.256e-29`
  here). A straight line cannot, and is left with `4.174` of pure bias.
  Both hold everywhere.
- **Degree 24 supplies exactly 25 polynomial features.** `1 + 24` terms in
  one variable. This is a count, and it is why 25 training rows is the
  worst case in the data sweep — the system is square there.
- **The training column is monotone in capacity, until the numerics give
  out.** More capacity can never fit the training data worse, in exact
  arithmetic. The 0.0636 wobble past degree 14 is floating point, not
  statistics, and the lab asserts monotonicity through degree 14 and
  asserts that it does *not* hold overall rather than pretending
  otherwise.
- **Training error rises monotonically with the ridge penalty.** A penalty
  can only make the training fit worse. Always true.
- **The three parts sum to the predicted total.** An identity. The lab
  checks it to within 0.0002, because each part is stored already rounded
  to four decimal places and summing rounded parts is not the same as
  rounding the sum.
- **The shape of every result**: bias dominant when the model is rigid,
  variance dominant when it is flexible, test error above training error
  for a flexible model and below it for a rigid one, and a degree-24 model
  overfitting where a degree-4 model does not. Harness check 8 runs three
  extra data seeds and a smaller decomposition sample to confirm each.

## Exact under these pins, and only these

Everything else depends on NumPy's `default_rng` bit stream and on
scikit-learn's solver internals. **NumPy's own documentation states that
`Generator` carries no stream-compatibility guarantee across versions**,
so seeding makes these reproducible under the pins in
`requirements/requirements.txt` and not beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| the ten rows of the capacity sweep | 1 | train and test MSE at each degree |
| `-1.4942`, `-1.4372` | 1c | the negative gaps at degrees 1 and 2 |
| `0.0636` | 1b | the numerical wobble in training error past degree 14 |
| the seven rows of the regularisation sweep | 2 | train and test MSE at each alpha |
| `39588` | 2 | the factor by which the best penalty improves test error |
| the eighteen entries of the data sweep | 3 | test MSE at three capacities and six sizes |
| `0.6227` | 3 | the total range of the underfit column |
| `64631547.2994` | 3c | the peak at the interpolation threshold |
| every bias, variance and total in the decomposition | 4 | over 200 training sets |
| `0.01003` | 4b | the worst relative disagreement between predicted and observed |
| `7.3906`, `2.4744`, `5.4555`, `5.8978`, `7.1435` | 5 | the training-history figures |
| epoch `14` | 5 | where test error bottoms |
| `0.6771`, `3.4234` | 5b | the generalisation gap at epochs 1 and 600 |

## Sampled, and therefore soft even here

- **The decomposition's `observed` column is a Monte Carlo estimate** over
  200 models times 200 query points, against freshly drawn noisy targets.
  Its worst disagreement with the predicted total is 1.003 percent, at
  degree 6, and five of the seven capacities agree to better than a
  quarter of a percent. The lab asserts 1.1 percent rather than something
  tighter for exactly that reason — the disagreement is sampling error in
  the check, not error in the identity.
- **The early-stopping epoch is the softest number in the lab.** The test
  curve after its minimum is not monotone: it rises to 7.1435 around epoch
  84 and partly recovers to 5.8978 by epoch 600. On this run every
  patience from 5 to 50 recovers epoch 14 and so does a naive
  stop-at-first-increase — but that is luck on this run, not a property of
  the rule, and the lab says so in a comment rather than presenting the
  naive rule as safe.
- **Degree 2 having more bias than degree 1** is measured over 200
  training sets and the gap is small (4.3342 against 4.2985). In
  population terms a larger model class cannot have more bias; what is
  measured here is the average over finitely many fits, where the extra
  free parameter degrades the estimate. The lesson states the mechanism
  rather than claiming a theorem.

## Timings

No timing is asserted anywhere in this lab. The heaviest step is the
decomposition, which fits 200 models per capacity across seven capacities.
It runs in a couple of seconds here and will take longer on a slower
machine without changing a single assertion, because every assertion is
about a shape or a value.
