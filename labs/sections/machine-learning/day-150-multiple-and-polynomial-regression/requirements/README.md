# Requirements

`requirements.txt` pins the three packages this lab imports directly, at
the exact versions the captured output in `expected-output/` was produced
with:

```
numpy==2.5.2
scikit-learn==1.9.0
pytest==9.1.1
```

Installing scikit-learn also pulls in scipy, joblib and threadpoolctl as
its own dependencies. This lab imports none of them directly and does not
pin them; the versions present during capture are recorded in
`../expected-output/FIELDS.md`.

## Why the versions are pinned exactly

`sklearn.linear_model.LinearRegression` solves the normal equations with a
deterministic least-squares routine, so most of this lab's numbers are
exact arithmetic rather than sampled draws -- but two things do depend on
the pins: `numpy.random.default_rng`, used for the noise columns and the
bootstrap resamples, carries no stream-compatibility guarantee across
NumPy versions, and scikit-learn's own internals (LAPACK routine choice,
convergence tolerances) can shift a coefficient in its last few decimal
places between minor versions.

What does not depend on the pins: every formula (variance inflation as
`1 / (1 - R2)`, the standard-error-free identity that two duplicate
coefficients sum to the original), every structural fact (the exact
duplicate's predictions matching to floating-point precision, the
polynomial fit matching the normal equations), and the direction of every
result -- a duplicated correlated predictor destabilises its coefficients
while leaving predictions almost untouched, high-VIF predictors wobble
more under resampling than low-VIF ones, R2 never decreases when a
predictor is added, and standardising changes coefficients without
changing predictions. Harness check 8 re-runs several of these directions
at seeds and predictors the lesson does not quote.

`expected-output/FIELDS.md` separates the two categories in full, and it
is worth reading before you conclude that a mismatch is a bug.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: the
only dataset this lab uses is `sklearn.datasets.load_diabetes`, which
ships bundled inside the scikit-learn package you just installed --
nothing is downloaded at run time.

## Free and open-source status

All three packages are free and open source -- NumPy and scikit-learn
under the BSD 3-Clause licence, pytest under the MIT licence. There is no
paid tier, no account and no API key anywhere in this lab.
