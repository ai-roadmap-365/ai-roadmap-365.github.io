# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.percentile` under nine interpolation conventions (exercise 4), and the `numpy.random.Generator` built by `default_rng(seed)` used for the Bessel-correction simulation (exercise 3) and the contamination sample (exercise 8). |
| `pytest` | 9.1.1 | MIT | The reference suite and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 5 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What most of this lab does not need NumPy for at all

Exercises 1, 2, 5, 6, 7 and 9 use only the standard library —
`statistics`, `collections.Counter`, and plain arithmetic. Only exercise 4
(the percentile conventions) genuinely needs `numpy.percentile`'s
`method=` argument, which the standard library has no equivalent for.
Exercises 3 and 8 need `numpy.random.Generator` for fast, reproducible
simulation, though Python's own `random.Random(seed)` could stand in at
the cost of a slower Python-level loop instead of a vectorised call —
`troubleshooting.md` shows the substitution.

## What is deliberately *not* installed

`pandas` and `scipy.stats` are **not installed in this environment, and no
output from either is reproduced anywhere** in this lab or its lesson.
`pandas.DataFrame.describe()` and `scipy.stats` are both described from
their public documentation in the lesson's Tools section, and both are
explicitly marked as not run here.

That is not a limitation to apologise for. Every statistic this lab
computes is either exact arithmetic from the standard library, an explicit
call to a named NumPy convention, or a simulation you run yourself with
`numpy.random.Generator` — nothing here depends on `pandas` or `scipy` to
be correct.
