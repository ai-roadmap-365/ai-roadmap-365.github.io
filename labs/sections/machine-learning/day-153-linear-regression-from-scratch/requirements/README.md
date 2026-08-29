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

Every measured pair in this lab is deterministic given a seed -- there is
no repeated random sampling to average over, unlike Day 144's lab -- but
`np.linalg.lstsq`, `np.linalg.solve`, `np.linalg.eigvalsh` and
scikit-learn's own `LinearRegression` all bottom out in LAPACK routines
whose exact floating-point results can differ, in the last few bits, across
NumPy, SciPy and BLAS builds. Nothing here changes direction or order of
magnitude across ordinary machines, but the trailing decimals of numbers
like `1.2153e-10` are a property of this exact software stack, not of
mathematics.

What does not depend on the pins: every structural claim -- lstsq is closer
to sklearn than the normal equations are, `cond(X'X)` equals `cond(X)`
squared, the near-duplicate column makes the normal equations and lstsq
explode while sklearn stays sane, gradient descent diverges above the Day
111 stability threshold and converges below it, and the closed form uses
far fewer operations than gradient descent. `expected-output/FIELDS.md`
separates the two categories in full.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: the
only dataset this lab uses is scikit-learn's bundled `load_diabetes`, which
ships inside the scikit-learn package itself and is never downloaded.

## Free and open-source status

All three packages are free and open source -- NumPy and scikit-learn under
the BSD 3-Clause licence, pytest under the MIT licence. There is no paid
tier, no account and no API key anywhere in this lab.
