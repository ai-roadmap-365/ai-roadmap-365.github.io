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

The headline finding in this lab — that a hand-built estimator inheriting
nothing from scikit-learn breaks inside `cross_val_score` with an
`AttributeError` naming `__sklearn_tags__` — is a fact about this specific
version of scikit-learn, not a fact about the library forever. `__sklearn_tags__`
is recent scikit-learn machinery; an older version might fail differently,
or not fail at all, and a much newer one might change the message text
again. Pin the version and the failure — and the fix — reproduce exactly.

`sklearn.utils.all_estimators()`'s census (exercise 7) is also
version-specific: scikit-learn adds and removes estimators between
releases, so the totals of 208 (bare) and 210 (with
`sklearn.experimental.enable_halving_search_cv` imported) belong to 1.9.0
specifically. The *fact that a bare count and an enabled count differ at
all* is not version-specific -- `all_estimators()` has only ever found
what has actually been imported, in every scikit-learn version with
experimental estimators -- but which estimators are gated behind an
experimental import, and how many there are, changes release to release.

What does not depend on the pins: the *shape* of every finding. Fitting
always adds attributes with a trailing underscore; `get_params`/`set_params`
always round-trip; a `Pipeline` step is always refit once per
cross-validation fold; `predict()` is always `argmax(predict_proba())`;
and a hand-built estimator that satisfies `fit`/`predict`/`score`/`get_params`/
`set_params` will always work when called directly, whether or not it
happens to interoperate with every piece of scikit-learn's own machinery.
Harness check 8 re-confirms four of those shapes at seeds and parameters
the lesson never quotes.

`expected-output/FIELDS.md` separates the two categories in full, and it
is worth reading before you conclude that a mismatch is a bug.

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
