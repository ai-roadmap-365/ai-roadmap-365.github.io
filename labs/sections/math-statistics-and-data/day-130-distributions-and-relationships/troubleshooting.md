# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'seaborn'`

Your `.venv` was never created or activated. Run:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the harness at an existing install:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'scipy'`

Expected, and not a bug in this lab. `scipy` is not installed in this
environment on purpose (see `requirements/README.md`). If you see this
error from pandas' `.corr(method="spearman")`, that confirms exactly
what exercise 8 asks you to work around: compute Spearman's correlation
yourself as the Pearson correlation of `.rank()`-ed columns instead.
`seaborn.kdeplot` does **not** need `scipy` and works fully in this
environment; if you see this error from a `kdeplot` call specifically,
something else is wrong — check your seaborn version.

## A plot window tries to open, or the run hangs

Something imported `matplotlib.pyplot` before `matplotlib.use("Agg")` ran.
Both `conftest.py` files set the backend first, before anything else is
imported — if you add a new test file, import `matplotlib` and call
`matplotlib.use("Agg")` at its very top, before `import matplotlib.pyplot`
or `import seaborn`. The test harness also exports `MPLBACKEND=Agg` as a
second line of defense.

## `pytest examples starter` aborts with `import file mismatch`

Both directories define a module named `test_distributions.py`, and
pytest imports test modules by their dotted name — running them together
is tested directly in this lab's harness (section 4) and reliably aborts
collection before running a single test. Run them as two separate
commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## Exercise 1's mode counts do not match `1` at 5 bins or `2` under `'fd'`

Recompute directly from `bimodal_for_binning()` in `data.py` rather than
hardcoding a number — the sample is generated from a fixed
`numpy.random.default_rng(42)` seed, so it should be identical to this
lab's own capture on any correctly installed NumPy 2.5.2. If your NumPy
version differs, the exact bin edges `histogram_bin_edges` chooses can
shift by one bin at the margins; the mode counts (1, then 2 under
Freedman-Diaconis, then more than 10 at 100 bins) are the values this lab
actually asserts on, not the raw bin-edge array.

## Exercise 5's two five-number summaries do not agree within `0.3`

Both samples in `matched_quartile_pair()` are built deterministically
from a piecewise-linear function evaluated at 240 evenly spaced ranks —
there is no randomness in this exercise's construction at all. If your
result disagrees, confirm you are calling `numpy.percentile(x, [0, 25,
50, 75, 100])` with exactly that percentile list, and not `boxplot`'s own
whisker convention, which uses a different (and, for this exercise,
irrelevant) definition of the whisker ends.

## The `MatplotlibDeprecationWarning` printed during the harness run

None was observed in this lab's own capture on seaborn 0.13.2 /
matplotlib 3.11.1 — `kdeplot` and `ecdfplot` do not exercise the
deprecated code path Day 129's `boxplot` call does. If you see one
anyway on a different version pin, it is a warning, not a failure; every
test still passes.

## Image files left behind after a manual experiment

If you called `fig.savefig(...)` yourself while exploring outside the
test suite, `tests/run_tests.sh`'s cleanliness check (section 6) will
report it. Remove the file and re-run; nothing in `examples/` or
`starter/` writes an image file on its own.
