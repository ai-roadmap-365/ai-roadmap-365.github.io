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
`../expected-output/FIELDS.md`. The Q-Q normal-probability check is built
from scratch inside `regression_lib.py` specifically so this lab does not
need scipy.

## Why the versions are pinned exactly

`KFold(shuffle=True, random_state=...)`, `train_test_split`, and the
bootstrap resampling in `margin_bootstrap_interval` all depend on NumPy's
`Generator` bit stream, which NumPy's own documentation states carries no
cross-version compatibility guarantee. Different pinned versions can
legitimately shuffle the same seed into a different order, and every
downstream number -- the winning configuration, its cross-validated RMSE,
the test score, every residual diagnostic -- would move with it.

What does not depend on the pins: the RMSE and R2 formulas, which are
arithmetic; the direction of every structural result -- the leaky
selection score is never worse than the honest one, cross-validation
selects on train rows only, a gated test set refuses a second look; and
structural facts, such as the dataset used here having 442 rows and 10
features. `expected-output/FIELDS.md` separates the two categories in
full.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: the
dataset is bundled inside scikit-learn itself, and nothing else is
downloaded.

## Free and open-source status

All three packages are free and open source -- NumPy and scikit-learn
under the BSD 3-Clause licence, pytest under the MIT licence. There is no
paid tier, no account and no API key anywhere in this lab.
