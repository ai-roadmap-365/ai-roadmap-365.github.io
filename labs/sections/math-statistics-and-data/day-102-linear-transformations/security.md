# Security notes — Day 102 lab

## What this lab does

It computes and it prints. Six reference scripts, two test suites and a bash
harness, all working on matrices with four entries each. There is no server, no
client, no database, no file written outside this directory, and no data that
belongs to anybody.

## What it does not do

| Concern | Status here |
| --- | --- |
| Network access | Only the one-time `pip install`. No lab source opens a socket, reads a URL or contacts a service, and section 7 of `tests/run_tests.sh` greps `examples/` and `starter/` for the patterns that would show otherwise. |
| Credentials | None. No API key, no token, no password, no account. `requires_api_key: false` in `metadata.yml`. |
| Elevated privileges | None. Nothing in this lab needs `sudo`, and you should not give it any. |
| Files written | The virtual environment in `.venv/`, and nothing else. The scripts write no output files; the captured text in `expected-output/` was redirected there by hand when the lab was built. |
| Personal data | None. Every number is invented: a made-up matrix, a unit square, an L-shaped flag, and one pseudo-random stack seeded with 102 so it is identical on every machine. |
| Code execution from data | None. Nothing is `eval`-ed, nothing is deserialised, no file is read as code. |

## Deleting everything

```bash
rm -rf .venv
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
git checkout -- starter/
```

That is a complete undo. The lab leaves no trace elsewhere on your machine.

## Installing packages, briefly

The single network operation is `pip install -r requirements/requirements.txt`,
which fetches numpy and pytest from the Python Package Index. Two habits worth
keeping, and they are general rather than specific to this lab:

- **Install into a virtual environment, not the system Python.** Everything in
  this lab does. A lab-local `.venv/` cannot break anything else you have, and
  `rm -rf .venv` undoes it completely.
- **Pin versions and read the file before running it.** `requirements.txt` here
  is two lines with exact versions, and section 1 of the harness verifies that
  what is installed matches what is written. An unpinned requirement is a
  request to install whatever exists at the moment you run it.

## The one thing worth carrying away

This lab has no security surface of its own, so the transferable point is about
the mathematics rather than the code, and it is this: **a transformation with
determinant zero destroys information, and no amount of downstream processing
recovers it.**

That sounds abstract until you notice how often it is the property you actually
want, and how often it is the property that bites.

When you *want* it: a hash, a redaction, a one-way projection. If two different
inputs must be indistinguishable afterwards, you need a step from which they
cannot be told apart — and a rank-deficient transformation is one honest way to
say that in linear terms.

When it bites: a pipeline that reduces dimensions somewhere in the middle
cannot be inverted after that point, so "we can always reconstruct the original
from the embedding" is a claim to check rather than assume. Sometimes it is
false in the reassuring direction — the reduction really did destroy the
identifying detail. Sometimes it is false in the alarming direction: the
transformation had full rank after all, the reduction was lossless, and what
looked like anonymisation was a reversible relabelling. Section 5 of
`05_determinant_inverse_rank.py` shows both cases in two lines each: compute
the determinant, and count the dimensions that survive.

The lab's `rank` function and `numpy.linalg.matrix_rank` answer that question
directly, and they are worth reaching for before anyone claims a step is
irreversible.
