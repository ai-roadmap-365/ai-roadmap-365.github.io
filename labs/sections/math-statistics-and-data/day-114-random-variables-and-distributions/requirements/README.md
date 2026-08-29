# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | The `numpy.random.Generator` built by `default_rng(seed)`, used for every simulation and every sampler in exercises 3, 7, 8 and 9. |
| `pytest` | 9.1.1 | MIT | The reference suite (69 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 7 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## If you cannot install anything at all

Exercises 1, 2, 4, 5, 6, 9 and 10 need only `fractions` and `math` from the
standard library and do not touch NumPy at all. Only exercises 3, 7 and 8
need `numpy.random.Generator`. If NumPy is unavailable, Python's own
`random` module can stand in for a uniform draw:

```python
import random

def sample_exponential_scratch_stdlib(rate: float, rng: random.Random, size: int) -> list[float]:
    import math
    return [-math.log(rng.random()) / rate for _ in range(size)]
```

It is slower -- a Python-level loop instead of a vectorised NumPy call --
but it is the same statistics. What you lose is `pytest`, so no running
score and no skip-versus-fail distinction; you would read the numbers back
yourself instead.

## What is deliberately *not* installed

`scipy.stats` does this job too -- its `rv_continuous` and `rv_discrete`
base classes are the shape every named distribution in this lesson's table
would map onto, with `.pmf()`/`.pdf()`, `.cdf()`, `.mean()`, `.var()` and
`.rvs()` methods -- and it is **not installed in this environment, and no
output from it is reproduced anywhere** in this lab or its lesson. The
lesson's Tools section describes it from its documentation and marks it as
not run here.

`pandas` and `matplotlib` are also not installed and are not needed for
anything in this lab; every table here is small enough to enumerate and
print directly, and every plot the lesson describes is described in prose
rather than rendered.

That is not a limitation to apologise for. Every exact claim this lab makes
is computed with `fractions.Fraction` over a finite enumerated space, and
every sampled claim is drawn from the standard library and NumPy's random
module and checked against a derived tolerance -- nothing here depends on
a statistics package to be correct.
