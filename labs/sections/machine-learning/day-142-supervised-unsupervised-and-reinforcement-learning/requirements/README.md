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

Most of the numbers in this lab come from a seeded
`numpy.random.default_rng`. NumPy's documentation is explicit that
`Generator` makes no promise of stream compatibility between versions, so
a different NumPy can legitimately produce a different stream from the
same seed and every sampled figure would move. Pinning is what makes
"assert this equals 0.708" an honest assertion rather than a trap.

The structural results do not depend on the pins at all —
`expected-output/FIELDS.md` separates the two categories explicitly, and
it is worth reading before you conclude that a mismatch is a bug.

## Installing

From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The install step needs the network. Everything after it is offline: iris
ships inside the installed scikit-learn package, and every other dataset
in this lab is generated on the spot from a seeded generator.

## Free and open-source status

All three packages are free and open source — NumPy and scikit-learn
under the BSD 3-Clause licence, pytest under the MIT licence. There is no
paid tier, no account and no API key anywhere in this lab.
