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
pin them.

## Why the versions are pinned exactly

Almost every number in this lab comes from `sklearn.datasets.load_diabetes`
(a fixed, bundled dataset -- no download, no randomness in the data itself)
combined with `numpy.random.default_rng` for the handful of exercises that
add synthetic noise or construct toy predictions. NumPy's documentation is
explicit that `Generator` makes no promise of stream compatibility between
versions, so a different NumPy can legitimately produce a different noise
stream from the same seed, and any figure built from it could move by a
little.

What does not depend on the pins: every direction this lab claims --
training R2 climbing as noise columns are added, R2 having no lower bound,
RMSE moving more than MAE under an outlier, MAPE exploding at a zero or
near-zero true value, the RMSE/MAE ranking inversion, and the r2_score
argument-order bug. Harness check 8 re-runs three of those at seeds the
lesson never quotes, precisely so the distinction between "always true" and
"true under these pins" is enforced rather than merely asserted.
`expected-output/FIELDS.md` separates the two categories in full.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: the
diabetes dataset ships inside scikit-learn itself, and every synthetic
example in this lab is generated on the spot from a seeded generator.

## Free and open-source status

All three packages are free and open source -- NumPy and scikit-learn under
the BSD 3-Clause licence, pytest under the MIT licence. There is no paid
tier, no account and no API key anywhere in this lab.
