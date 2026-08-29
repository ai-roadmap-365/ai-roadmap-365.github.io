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

`StratifiedKFold(shuffle=True, random_state=...)` and every seeded split in
this lab produce results that depend on NumPy's `Generator` bit stream,
which NumPy's own documentation states carries no cross-version
compatibility guarantee. Different pinned versions can legitimately shuffle
the same seed into a different order, and every downstream number — the
winning configuration, its cross-validated score, the test score, the
confusion matrix — would move with it.

What does not depend on the pins: the standard-error formula, which is
arithmetic; the direction of every result — the leaky selection score is
never lower than the honest one, cross-validating selects on train rows
only, a gated test set refuses a second look; and the structural facts,
such as the dataset used here having 569 rows and two classes.
`expected-output/FIELDS.md` separates the two categories in full.

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

All three packages are free and open source — NumPy and scikit-learn under
the BSD 3-Clause licence, pytest under the MIT licence. There is no paid
tier, no account and no API key anywhere in this lab.
