# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-27: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
in this lab's own `.venv` built from `requirements/requirements.txt` --
numpy 2.5.2, scikit-learn 1.9.0, pytest 9.1.1, with scipy 1.18.1,
joblib 1.5.3 and threadpoolctl 3.6.0 pulled in as scikit-learn's own
dependencies.

Unlike Day 144's lab, nothing here is averaged over random replications --
every measurement is a single deterministic computation given a seed, on a
dataset that is either scikit-learn's own bundled `load_diabetes` or
generated on the spot from `numpy.random.default_rng`. That makes most of
this lab's numbers far more exactly reproducible than a lab built on
repeated sampling. What is NOT exact everywhere is the trailing decimals of
anything that runs through LAPACK, because `np.linalg.solve`,
`np.linalg.lstsq`, `np.linalg.eigvalsh` and scikit-learn's own
`LinearRegression` all bottom out in the same class of floating-point
routines whose last few bits can differ across BLAS/LAPACK builds.

## Exact on any machine, for any reason

These are arithmetic or structural facts, not measurements that happened to
come out a certain way. Check 8 of the harness confirms the directional
ones at seeds and constructions the lesson does not quote.

- **`cond(X'X)` equals `cond(X)` squared**, to within numerical precision,
  on any well-conditioned matrix. This is a theorem about singular values,
  not an empirical finding, and it held to ten decimal places on the
  diabetes data and to seven more constructions in harness check 8.
- **The normal-equation and lstsq coefficients explode on the
  near-duplicate column, while sklearn's stay bounded.** The direction --
  not the exact magnitude of the explosion, which is sensitive to the
  0.1e-6-scale noise added to the duplicate column -- holds at every seed
  harness check 8 tries.
- **Gradient descent diverges above the Day 111 stability threshold and
  converges below it.** This is `|1 - eta * a| < 1` applied to a measured
  Hessian eigenvalue; it is arithmetic once the eigenvalue is known.
- **The Hessian eigenvalue ratio is far larger on raw, unscaled features
  than on standardized ones.** The raw diabetes columns are literally
  measured in different units (age in years, sex coded 1 or 2, serum
  measurements in clinical units), so this is closer to a fact about the
  dataset than a coincidence of the run.
- **The closed form uses far fewer operations than gradient descent, by
  formula.** `n*p^2 + p^3` against `2*n*p*iterations` are both arithmetic
  once the shapes and iteration count are fixed.
- **Centring and appending an intercept column agree.** Both are exact
  solutions to the same normal equations, algebraically identical; the
  measured gap is purely floating-point rounding.

## Exact under these pins, and only these

Everything below runs through NumPy's or scikit-learn's LAPACK bindings and
can differ in its trailing digits on a different BLAS build, a different
CPU architecture, or a different NumPy/scikit-learn version, even though the
underlying mathematics is unchanged.

| Value | Section | What it is |
| --- | --- | --- |
| `1.2153e-10`, `1.1990e-12` | 1 | max absolute gap of the normal equations and lstsq from sklearn on diabetes |
| `227.2248`, `51631.1119` | 1b | `cond(X)` and `cond(X'X)`, with an intercept column, on diabetes |
| the five-entry coefficient vectors | 2 | normal-equation, lstsq and sklearn coefficients on the near-duplicate-column dataset, seed 0 |
| `2.4363e+07`, `5.6547e+14`, `0.9527` | 2b | condition numbers and their measured ratio on the same dataset |
| `0.2485`, `3263`, `5277`, `7291` | 3 | the stability threshold and the iteration counts to 3, 6 and 9 decimals |
| `4.8746e-04`, `0.4692` | 3b | the raw-feature stability threshold and the remaining gap after 200,000 iterations |
| `7132` (below threshold), divergence above it | 4 | the exact iteration count to 1e-9 at 80 percent of threshold |
| `54,813`, `64,452,440` | 5 | the two operation counts |
| `48`, `2`, `2` | 6 | check_estimator's passed/failed/skipped counts, and the specific names |
| `1.9554e-11`, `2.8422e-14` | 7 | the centring-versus-column agreement gaps |

## Sampled, and therefore soft even here

- **The near-duplicate-column dataset (section 2) uses `noise_scale=1e-7`
  and `seed=0`.** The magnitude of the exploded coefficients -- around
  ±200,000 here -- depends on exactly how close the duplicate is to its
  twin; a different noise scale gives a different (still enormous)
  magnitude. What is stable across every seed harness check 8 tries is the
  DIRECTION: both closed forms explode, and sklearn does not.
- **The exact iteration counts in section 3 (`3263`, `5277`, `7291`) are a
  property of the specific learning rate chosen (0.2, about 80 percent of
  the threshold) and this specific dataset.** A different learning rate
  fraction or a different dataset gives different counts on the same
  formula; the formula itself -- linear convergence, roughly proportional
  extra iterations for each additional three decimal places -- is the
  transferable fact.
- **`check_estimator`'s two named failures (`check_n_features_in_after_fitting`,
  `check_dtype_object`) are properties of this exact `OLSRegressor`
  implementation and this exact scikit-learn version (1.9.0).** A future
  scikit-learn release could add, remove or rename checks. What is stable:
  the estimator passes the large majority of the suite by inheriting
  `BaseEstimator` and `RegressorMixin`, and the two gaps are both about
  input validation this from-scratch implementation does not perform, not
  about the fitting mathematics.

## Timings

No timing is asserted anywhere in this lab, and `report_measurements.py`
never calls a clock. Section 5 counts multiply-add operations by formula
instead, precisely so the comparison between the closed form and gradient
descent survives a slower or faster machine unchanged. The 200,000-iteration
gradient-descent runs in section 3b take a few seconds here and will take
longer on a slower machine without changing a single assertion.
