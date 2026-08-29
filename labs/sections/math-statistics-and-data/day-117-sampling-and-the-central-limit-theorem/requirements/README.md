# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.random.default_rng` for every seeded draw, and vectorised array operations for building sampling distributions of tens of thousands of trials at once. |
| `pytest` | 9.1.1 | MIT | The reference suite (19 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 6 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What is deliberately *not* installed

**`scipy.stats`** does the two heaviest pieces of this lab's work for you:
`scipy.stats.bootstrap` runs exercise 6 in a few lines, with several
confidence-interval methods to choose from, and `scipy.stats.sem` computes
exercise 1's standard error of the mean directly from a sample. Neither is
installed here, and **no output from scipy is reproduced anywhere** in
this lab or its lesson. The lesson's Tools section describes both from
their public documentation.

That is not a limitation to apologise for. The bootstrap you write in
`starter/sampling.py` -- resample with replacement, recompute the
statistic, read the standard error off the spread -- is the exact idea
`scipy.stats.bootstrap` implements. The difference between the two is
engineering: bias-corrected-and-accelerated confidence intervals, batched
vectorisation, and a stable public API. Having written the fifteen-line
version, you will read `scipy.stats.bootstrap`'s documentation differently.

**`pandas`** is also not installed. `DataFrame.sample` does a version of
this lab's population sampling on tabular data, and is described from its
documentation in the lesson's Tools section, not run here.

**`matplotlib`** is not installed either. Every figure this lesson
describes -- the sampling distribution's shape, the Cauchy-versus-
Exponential contrast -- is described in words and numbers rather than
plotted; the two hand-authored SVG diagrams in the lesson carry the visual
argument instead.

## If you cannot install anything at all

You still need NumPy for this lab, unlike some earlier days in this
section: every exercise draws random samples, and the standard library's
`random` module does not offer the same vectorised batch sampling this lab
relies on to draw tens of thousands of trials in a single call without
writing a Python-level loop for each one. If NumPy genuinely cannot be
installed, the *ideas* -- a statistic has a distribution, the standard
error shrinks as `1/sqrt(n)`, bias does not shrink, the bootstrap resamples
with replacement -- can still be worked through by hand on a small dataset
with `random.Random`, but this lab's exercises and tests are not written
against that path.
