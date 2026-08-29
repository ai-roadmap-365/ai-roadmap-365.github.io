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

Every number in this lab comes from `sklearn.linear_model.Ridge`,
`Lasso`, `LassoCV` and `ElasticNet` fitted on `sklearn.datasets.load_diabetes`
and `sklearn.datasets.make_regression`. Coordinate-descent convergence
paths, default solver choices, and exact floating-point results can shift
between scikit-learn releases even when the documented behaviour does not.

What does not depend on the pins: the directions of every result — ridge
never zeroing a coefficient at any alpha tried, lasso zeroing progressively
more, the constraint-region geometry that makes a lasso coefficient land
exactly on zero, the alpha-scale mismatch between `Ridge` and `ElasticNet`,
and the fact that a penalty applied to unscaled features selects a
different set than the same penalty applied to scaled ones.
`expected-output/FIELDS.md` separates the two categories in full.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: the
only dataset downloaded from anywhere is `load_diabetes`, which ships
bundled inside the scikit-learn package itself and is read from local
disk, never fetched over the network at runtime. The synthetic datasets
are generated on the spot with a seeded generator.

## Free and open-source status

All three packages are free and open source — NumPy and scikit-learn under
the BSD 3-Clause licence, pytest under the MIT licence. There is no paid
tier, no account and no API key anywhere in this lab.
