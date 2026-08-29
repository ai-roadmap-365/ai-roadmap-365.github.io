# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | The `numpy.random.Generator` built by `default_rng(seed)`, used for exercise 3's 2,000,000-person population simulation. |
| `pytest` | 9.1.1 | MIT | The reference suite (71 tests) and your running score in `starter/`. |

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

Exercises 1, 2, 4, 5, 6, 7, 8 and 9 need only `fractions`, `math` and
`collections` from the standard library and do not touch NumPy at all.
Only exercise 3's population simulation needs `numpy.random.Generator`. If
NumPy is unavailable, Python's own `random` module can stand in:

```python
import random

def simulate_population_stdlib(seed: int, n: int, prevalence: float,
                                sensitivity: float, specificity: float):
    rng = random.Random(seed)
    tp = fp = tn = fn = 0
    for _ in range(n):
        sick = rng.random() < prevalence
        if sick:
            tp += rng.random() < sensitivity
            fn += rng.random() >= sensitivity
        else:
            tn += rng.random() < specificity
            fp += rng.random() >= specificity
    return tp, fp, tn, fn
```

It is slower -- a Python-level loop instead of a vectorised NumPy call --
but it is the same statistics. What you lose is `pytest`, so no running
score and no skip-versus-fail distinction; you would read the numbers back
yourself instead.

## What is deliberately *not* installed

`scipy.stats` and PyMC (or Stan) do parts of this lesson's job too, and
considerably more once full posterior inference over continuous parameters
is the goal rather than a single discrete update. They are **not installed
in this environment, and no output from either is reproduced anywhere** in
this lab or its lesson. The lesson's Tools section describes both from
their documentation and marks them as not run here.

`pandas` is also not installed and is not needed for anything in this lab;
every table here is small enough to enumerate and print directly.

That is not a limitation to apologise for. Every posterior this lab
computes is either exact `Fraction` arithmetic or a simulation you can read
end to end in `simulate.py` -- nothing here depends on a statistics package
to be correct.
