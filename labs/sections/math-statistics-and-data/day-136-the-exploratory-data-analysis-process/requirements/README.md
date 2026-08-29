# What is installed, why, and what it costs

Three packages, all free and open source, all installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.random.default_rng` for every seeded draw, and vectorised array operations for the forking-paths and stopping-rule simulations. |
| `pandas` | 3.0.5 | BSD 3-Clause | Building the tidy, real DataFrames each exercise looks at (`groupby`-based comparisons, subset filters, the exploration/confirmation split), rather than working on bare arrays. |
| `pytest` | 9.1.1 | MIT | The reference suite (27 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially. The standard library's `math` module
(specifically `math.erf`) supplies every normal-distribution calculation --
no statistical package is needed for that part at all.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection.

## What is deliberately *not* installed

**`statsmodels`** is not installed. Its `statsmodels.stats.multitest`
module implements Bonferroni, Holm and false-discovery-rate corrections in
one call each, and can also report the raw multiplicity a step-down
procedure like Holm needs; this lab's `bonferroni_alpha` is one line,
described further, with `statsmodels`, in the lesson's Tools section. No
output from `statsmodels` is reproduced anywhere in this lab or its
lesson -- it is described from its public documentation only.

**Jupyter / `nbconvert`** is not installed either. This lab's exploration
loop runs as plain scripts so it stays fully scriptable and testable; the
lesson's Tools section describes Jupyter as the medium most analysts
actually explore in, and names Day 139 as where this course installs and
uses it directly.

**Weights & Biases** (or any hosted experiment tracker) is not installed
and nothing here calls out to a network service beyond the one-time
package install above. The lesson's Tools section describes what it adds
over a plain research log, and states its free-tier terms exactly as its
own documentation states them, with nothing further inferred.

## If you cannot install anything at all

You still need pandas and NumPy for this lab: the holdout split, the
choice-grid scan, and the vectorised forking-paths simulation are all
built on them. If neither can be installed, the ideas -- hold out a
confirmation set before forming a hypothesis, count every comparison you
actually ran, treat "we stopped when we found something" as a warning
sign -- can still be practiced by hand on a small dataset with the
standard library's `random` module, but this lab's exercises and tests
are not written against that path.
