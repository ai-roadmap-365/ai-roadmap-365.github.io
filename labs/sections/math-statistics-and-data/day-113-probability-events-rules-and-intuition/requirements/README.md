# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | The `numpy.random.Generator` built by `default_rng(seed)`, used for every simulation in exercises 3, 8 and 9 — de Méré's two bets, the Monte Carlo error-scaling sweep, and the reproducibility checks. |
| `pytest` | 9.1.1 | MIT | The reference suite (93 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 5 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/` to
prove that nothing else does.

## If you cannot install anything at all

Every exact-probability exercise — 1, 2, 4, 5, 6 and 7 — needs only
`itertools`, `fractions` and `statistics` from the standard library, and
none of them touch NumPy. Only the three simulation exercises (3, 8, 9) need
`numpy.random.Generator`. If NumPy is unavailable, Python's own `random`
module can stand in for the vectorised roll:

```python
import random

def simulate_sum_seven_stdlib(seed: int, trials: int) -> float:
    rng = random.Random(seed)
    hits = sum(
        1 for _ in range(trials)
        if rng.randint(1, 6) + rng.randint(1, 6) == 7
    )
    return hits / trials
```

It is slower — a Python-level loop instead of a vectorised NumPy call — but
it is the same statistics. `troubleshooting.md` shows the substitution for
the other two simulation functions. What you lose is `pytest`, so no running
score and no skip-versus-fail distinction; you would read the numbers back
yourself instead.

## What is deliberately *not* installed

`scipy.stats` does this job too — and considerably more, once random
variables and distributions arrive on Day 114. It is **not installed in this
environment, and no output from it is reproduced anywhere** in this lab or
its lesson. The lesson's Tools section describes it from its documentation
and marks it as not run here.

`pandas` is also not installed and is not needed for anything in this lab;
every table here is small enough to enumerate and print directly.

That is not a limitation to apologise for. Every probability this lab
computes is either counted exactly from an enumerated sample space or
estimated by a simulation you wrote yourself with the standard library and
NumPy's random module — nothing here depends on a statistics package to be
correct.
