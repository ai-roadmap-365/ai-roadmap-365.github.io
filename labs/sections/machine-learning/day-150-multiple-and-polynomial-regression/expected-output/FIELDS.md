# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` --
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

## Exact on any machine, for any reason

`sklearn.linear_model.LinearRegression` solves the normal equations
directly -- there is no iteration, no randomness, and no tolerance to
converge to. Most of this lab's headline numbers are therefore closed-form
arithmetic on a fixed, bundled dataset, not sampled draws.

- **The ten variance inflation factors** (exercise 1). `1 / (1 - R2)` on a
  deterministic auxiliary regression, on the same 442 rows every time.
- **The two correlations, s1-s2 at 0.8967 and s3-s4 at -0.7385** (1b).
  `numpy.corrcoef` on fixed data.
- **The exact-duplicate result** (2, 2b): the original coefficient
  `-1.09`, the two split coefficients `-0.545` each, their sum equal to
  the original to eight decimal places, predictions unchanged to eleven
  decimal places, and R2 unchanged to ten. This is not sampled; it follows
  from the normal equations having no way to distinguish two identical
  columns.
- **The polynomial-equals-normal-equations result** (6). Two different
  solvers -- scikit-learn's `LinearRegression` and a direct
  `numpy.linalg.lstsq` call -- on the identical expanded design matrix
  agree to better than `1e-9`, because they are solving the same linear
  system.
- **R2 never decreasing as predictors are added** (7), and **quadrupling
  by itself never being able to decrease it** -- a property of ordinary
  least squares, not of this dataset.
- **Standardising leaving predictions and R2 unchanged** (8), to floating
  point precision -- an invariance of linear regression under an affine
  rescaling of its inputs, not a measurement.
- **The direction of every instability result.** A duplicated correlated
  predictor destabilises its own coefficients while leaving predictions
  almost untouched; a higher-VIF predictor's coefficient wobbles more
  under bootstrap resampling than a lower-VIF one's; conditioning on the
  other nine predictors can flip a sign. Harness check 8 re-confirms
  several of these at seeds and predictors the lesson does not quote.

## Exact under these pins, and only these

Two things in this lab depend on `numpy.random.default_rng`, whose own
documentation states that `Generator` carries no stream-compatibility
guarantee across NumPy versions: the noise added in exercises 3 and 3b,
and the bootstrap resamples in exercise 4. A different NumPy can
legitimately produce a different stream from the same seed, moving these
values:

| Value | Exercise | What it is |
| --- | --- | --- |
| `0.7592`, `-1.8451`, `-1.0859` at seed 0 | 3 | the noisy duplicate's two coefficients and their sum |
| the seeds-0-9 spread of both coefficients, their sum, and R2 | 3b | ten refits under ten different noise draws |
| every entry of the bootstrap table | 4 | 500 resample-and-refit repetitions per predictor |

What must hold on any NumPy version, because it is the *shape* of the
result rather than a specific draw: both individual coefficients have a
standard deviation well above 4 across ten seeds; their sum's standard
deviation stays under 0.05; the largest single prediction move across all
ten seeds stays under 10; and a high-VIF predictor's bootstrap
coefficient-of-variation exceeds a low-VIF predictor's.

## Sampled, and therefore soft even here

- **The noisy-duplicate spread in exercise 3b is averaged over ten noise
  seeds**, for the reason Days 117-118 established: one draw is an
  anecdote. A single seed produced coefficients anywhere from roughly -7
  to +6 while this lab was being built; the spread, not any one seed's
  pair, is the reportable fact.
- **The bootstrap coefficient-of-variation table in exercise 4** is 500
  resamples per predictor. `age`'s own coefficient of variation (4.70) is
  inflated by its mean sitting near zero rather than reflecting genuine
  instability, which is why the comparison in exercise 4 excludes it and
  uses bmi, bp and sex as the low-VIF group instead.

## Timings

No timing is asserted anywhere in this lab. The heaviest step is the
500-repetition bootstrap in exercise 4, which completes in well under a
second here on 442 rows and at most eleven columns, and will take longer
elsewhere without changing a single assertion, because every assertion is
about a shape or a value.
