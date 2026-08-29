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

Every dataset here comes from a seeded `numpy.random.default_rng`, and
NumPy's documentation is explicit that `Generator` makes no promise of
stream compatibility between versions. A different NumPy can legitimately
produce a different stream from the same seed, and every measured figure
would move.

What does not depend on the pins: the irreducible floor of 4.0000, which
is arithmetic; the count of 25 features at degree 24; the monotonicity of
training error in capacity and in the penalty; the fact that the three
parts of the decomposition sum to the total; and the *shape* of every
result. Harness check 8 re-runs the shape claims at three data seeds the
lesson never quotes, precisely so the distinction is enforced rather than
asserted.

`../expected-output/FIELDS.md` separates the two categories in full, and
it is worth reading before you conclude that a mismatch is a bug.

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
