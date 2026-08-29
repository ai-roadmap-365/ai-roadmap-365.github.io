# Requirements

`requirements.txt` pins the three packages this lab imports directly, at
the exact versions the captured output in `expected-output/` was produced
with:

```
numpy==2.5.2
scikit-learn==1.9.0
pytest==9.1.1
```

Installing scikit-learn also pulls in scipy (1.18.1), joblib (1.5.3) and
threadpoolctl (3.6.0) as its own dependencies during capture. This lab
imports none of them directly and does not pin them.

## Why the versions are pinned exactly

Most of this lab is deterministic given a seed, but a few figures are
averages over many seeded draws from `numpy.random.default_rng` (the
slope-recovery table in exercise 2), and NumPy's own documentation states
that `Generator` makes no promise of stream compatibility between
versions. A different NumPy can legitimately produce a different stream
from the same seed.

What does not depend on the pins: the BMI model itself (`sklearn.datasets.
load_diabetes` ships a fixed array, not a random draw, so its slope,
intercept, R-squared and standard error are exact on any working install
of these three packages); the two structural facts in exercise 1c (a
least-squares line passes through the point of means, and its residuals
sum to zero); the direction of every result — the error shrinks as n
grows, curvature shows up in binned residuals, heteroscedasticity fans the
residual spread, a leverage point moves the slope, and forcing the
intercept to zero costs accuracy.

`expected-output/FIELDS.md` separates the two categories in full.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: the
diabetes dataset ships inside scikit-learn's own package data, and every
other dataset in this lab is generated on the spot from a seeded
generator.

## Free and open-source status

All three packages are free and open source — NumPy and scikit-learn under
the BSD 3-Clause licence, pytest under the MIT licence. There is no paid
tier, no account and no API key anywhere in this lab.
