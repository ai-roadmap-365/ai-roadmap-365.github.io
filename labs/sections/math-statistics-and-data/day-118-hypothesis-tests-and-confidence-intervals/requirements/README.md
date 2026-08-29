# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.random.default_rng` for every seeded draw, and vectorised array operations for building thousands of confidence intervals and permutation shuffles at once. |
| `pytest` | 9.1.1 | MIT | The reference suite (22 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially. The standard library's `math` module
(specifically `math.erf`) supplies every normal-distribution calculation --
no statistical package is needed for that part at all.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 6 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What is deliberately *not* installed

**`scipy.stats`** would replace most of `examples/inference.py` with a
handful of function calls: `scipy.stats.ttest_ind(a, b, equal_var=False)`
runs Welch's t-test in one line, and `scipy.stats.norm.interval` builds a
confidence interval directly. Neither is installed here, and **no output
from scipy is reproduced anywhere** in this lab or its lesson. The lesson's
Tools section describes both from their public documentation.

That is not a limitation to apologise for. `inference.py`'s
`two_sample_z_test` and `confidence_interval_mean` are the exact ideas
`ttest_ind` and `norm.interval` implement, minus the engineering: a t
rather than a normal reference distribution for small samples, several
named alternatives, vectorised batch operation, and a stable public API.
Having written the from-scratch version, `scipy.stats.ttest_ind`'s
documentation reads as an implementation detail rather than a black box.

**`statsmodels`** is also not installed. Its `statsmodels.stats.multitest`
module implements Bonferroni, Holm and false-discovery-rate corrections in
one call each; this lab's Bonferroni correction (`bonferroni_alpha`) is
three lines, described further, with `statsmodels`, in the lesson's Tools
section.

## If you cannot install anything at all

You still need NumPy for this lab: every exercise draws random samples or
shuffles at a scale (thousands of permutations, thousands of simulated
confidence intervals) that the standard library's `random` module was not
designed to batch efficiently. If NumPy genuinely cannot be installed, the
*ideas* -- a p-value is P(data this extreme | null true), a confidence
interval's 95% is a property of the procedure not of any one interval, a
permutation test needs no distributional assumption -- can still be worked
through by hand on a small dataset with `random.Random`, but this lab's
exercises and tests are not written against that path.
