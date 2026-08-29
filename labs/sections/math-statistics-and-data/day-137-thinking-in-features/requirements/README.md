# Requirements

`requirements.txt` pins the exact versions this lab was written and run
against on 2026-08-20. Everything else it uses — `re`, `math`,
`collections`, `dataclasses` — is in the Python standard library.

Install into a lab-local virtual environment so the pins cannot collide
with anything else on your machine:

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Only that install step needs the network. Everything after it runs
offline: the lab reads no URL, opens no socket, and needs no API key.

## What is deliberately absent

**scikit-learn is not installed, and the harness asserts that it is
not.** That is not an oversight. This lab sits four days before the
course reaches machine learning, so every model in it is written out in
NumPy — a logistic regression trained by gradient descent and a
nearest-centroid classifier — and both are short enough to read. The
lesson describes scikit-learn's `Pipeline` and `ColumnTransformer` from
their published documentation and reproduces no output from either.

If you install scikit-learn into this environment the version check in
section 1 of the harness will fail, and so will the check that asserts
its absence. That is the harness telling the truth about what it ran
against, which is the whole point of the pins.

## Why the pins are exact

Section 1 of `tests/run_tests.sh` compares every installed version
against this file and fails on a mismatch. Every result in this lab is
generated from a seeded `numpy.random.default_rng`, so the numbers are
reproducible to the last decimal — but only against the same generator
stream. Pinning NumPy is what makes "0.6218 against 0.6224" a fact
rather than an anecdote.

pandas is pinned at 3.0.5 because two of its 3.0 behaviours show up in
this lab's code: Copy-on-Write is always on, and the default string
dtype is `str` rather than `object`. The `pd.Series(..., dtype="str")`
calls in `data.py` are explicit for that reason.

## If a pin will not install

Any recent pandas 2.2+ or NumPy 2.x will almost certainly run the lab.
The version check in section 1 will complain; the nine exercises should
still pass, because every assertion is a band rather than an equality —
except exercise 5, which is exact arithmetic and holds anywhere.
`expected-output/FIELDS.md` records exactly which captured values are
version-sensitive and which are exact everywhere.
