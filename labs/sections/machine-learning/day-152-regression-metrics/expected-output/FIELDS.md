# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` --
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy, joblib and
threadpoolctl pulled in as scikit-learn's own dependencies.

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened to
come out a certain way. Check 8 of the harness confirms the directional
ones at seeds the lesson does not quote.

- **Training R2 is non-decreasing as predictors are added.** This is a
  property of ordinary least squares, not an observation about this
  dataset: adding a column can only reduce or leave unchanged the training
  sum of squared residuals, because the old solution is still available to
  the fit. It holds for any noise columns, at any seed.
- **`sqrt(p(1-p)/n)`-style reasoning aside, a constant-mean predictor scores
  R2 essentially exactly zero on fresh data drawn from the same
  distribution.** R2 is defined relative to exactly that predictor, so this
  is what the metric compares against, not an incidental property of the
  diabetes dataset.
- **R2 has no lower bound.** A predictor worse than always guessing the
  mean scores below zero, and there is no floor -- the all-zeros predictor
  used here scores -4.7009, and a still-worse predictor would score lower
  still.
- **RMSE moves more than MAE when a single target is shifted far away**, for
  any dataset and any shift, because RMSE squares the error contributed by
  that one row while MAE does not.
- **MAPE explodes at a zero true value** because scikit-learn floors the
  denominator at machine epsilon rather than raising -- a structural
  choice in the library, not a property of any particular input.
- **MAPE is bounded at 1.0 for the worst possible systematic
  under-prediction (always guessing zero) and unbounded for over-prediction.**
  This follows from the definition of the metric, not from a measurement.
- **Ordinary least squares is invariant to a per-column affine rescaling of
  its inputs.** `load_diabetes(scaled=True)` and `load_diabetes(scaled=
  False)` therefore produce identical predictions, and identical RMSE, MAE
  and R2, once a model is fit on each.
- **`r2_score` is not symmetric in its two arguments.** The denominator is
  the variance of whichever array is passed first, so swapping the
  arguments changes the answer for any pair of non-identical arrays.

## Exact under these pins, and only these

Everything with a specific decimal depends on `load_diabetes`'s fixed
array (itself bundled and version-independent within scikit-learn's data
files) combined with `numpy.random.default_rng` for the handful of places
this lab adds synthetic noise or predictions. **NumPy's own documentation
states that `Generator` carries no stream-compatibility guarantee across
versions**, so seeding makes these reproducible under the pins in
`requirements/requirements.txt` and not necessarily beyond them.

| Value | Exercise | What it is |
| --- | --- | --- |
| the five rows of the noise-column curve | 1, 1b | train R2 and adjusted R2 at 0, 1, 5, 20 and 100 noise columns |
| `0.3594`, `-0.0001`, `-4.7009` | 2, 2b | full-model, constant-mean and bad-predictor test R2 |
| `(2.4801, 1.9833, 28.2569, 5.9448)` | 3 | RMSE and MAE before and after the outlier shift |
| `5.6295e+15` | 4 | MAPE at a zero true value (the exact digits depend on floating-point rounding of the epsilon floor) |
| `(3.3667, 5.0)` | 4b | MAPE and MAE on the near-zero-target rows |
| `(1.0, 10.0)` | 5 | the MAPE asymmetry bound |
| `(1.947, 1.586, 4.4353, 0.8417)` | 6 | the ranking-inversion RMSE and MAE for Models A and B |
| `(56.3929, 45.1206, 0.3594)` | 7 | RMSE, MAE and R2 on raw and on scaled features |
| `0.359409` / `-0.209635` | 8, 8b | r2_score in the correct and the swapped argument order |

## Sampled, and therefore soft even here

- **The exact magnitude of the MAPE-at-zero explosion.** The direction
  (it is enormous) is structural. The precise digit sequence
  `5629499534213120.0` follows from the exact floating-point value of
  `np.finfo(np.float64).eps` and the exact numerator on this input, and is
  reported as-is because it was genuinely observed, but no claim in the
  lesson depends on it being exactly that figure rather than another
  enormous one.
- **The ranking-inversion numbers in exercise 6.** The direction of the
  inversion -- RMSE prefers Model A, MAE prefers Model B -- is checked at
  three further seeds by harness check 8 and holds at all of them. The
  exact decimals are specific to seed 2.
- **The noise-column decimals in exercise 1.** The monotonic climb in
  training R2 is structural (see above); the specific values 0.5554
  through 0.7403 depend on the exact noise columns drawn, which depend on
  the NumPy version.

## Timings

No timing is asserted anywhere in this lab. The heaviest step fits eleven
`LinearRegression` models on at most 331 rows and 110 columns, which
completes in well under a second on the capture machine and will take
longer elsewhere without changing a single assertion, because every
assertion is about a shape or a value.
