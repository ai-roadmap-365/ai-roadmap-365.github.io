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
pin them; the versions present during capture — scipy 1.18.1, joblib
1.5.3, threadpoolctl 3.6.0 — are recorded in `../expected-output/FIELDS.md`.

## Why the versions are pinned exactly

Every sampled figure in this lab — the outlier-shift movements, the Huber
epsilon sweep on real data, and both efficiency-under-noise comparisons —
comes from `numpy.random.default_rng`, and NumPy's own documentation is
explicit that `Generator` makes no promise of stream compatibility between
versions. A different NumPy can legitimately produce a different stream
from the same seed, and every sampled figure would move.

`HuberRegressor` and `QuantileRegressor` are also estimator internals: the
exact coefficients from an iterative solver can shift in the last few
decimal places across scikit-learn releases even with the seed held fixed,
because the solver's stopping tolerance and default number of iterations
are part of the library, not the seed.

What does not depend on the pins: the mean minimises squared error and the
median minimises absolute error, which is arithmetic; the normal equations
matching `LinearRegression` to many decimal places, which is closed-form
algebra; the constant-versus-varying second differences that distinguish a
smooth loss from a kinked one; and the direction of every comparison —
least squares moves further than Huber and further still than the median
fit when a single point becomes an outlier, and Gaussian errors favour
least squares while heavy-tailed errors favour Huber.
`expected-output/FIELDS.md` separates the two categories in full.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: every
dataset in this lab is generated on the spot from a seeded generator, and
nothing is downloaded.

## Free and open-source status

All three packages are free and open source — NumPy and scikit-learn under
the BSD 3-Clause licence, pytest under the MIT licence. There is no paid
tier, no account and no API key anywhere in this lab.
