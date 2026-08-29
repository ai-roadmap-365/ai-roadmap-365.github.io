# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'sampling'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `sampling` and `dataset` from beside
themselves.

```bash
cd examples
../.venv/bin/python3 01_sampling_distribution.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test
file's own directory on the import path.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. Everything in
this lab goes through `.venv/bin/python3`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you would rather use an interpreter you already have, the harness
accepts one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## The starter tests all skip and I have written code

A skip means the function still returns `None`. Every function in
`starter/sampling.py` has `return None` as its last line -- write your body
above it and replace that line with your own `return`, rather than adding
code before an unchanged `return None`.

## My exercise 2 or 5 ratio assertion fails, but only sometimes

These exercises compare a *ratio* of two measured standard errors or
errors, and both quantities carry their own simulation noise. If a ratio
lands just outside the tolerance in `dataset.py`, first check you are
passing `rng` -- the single shared generator -- into every call rather than
creating a fresh `numpy.random.default_rng()` inside your function each
time, which would silently make every call start from the same default
state and correlate results in a way that inflates or deflates the
measured ratio.

## My Cauchy IQR "shrinks" almost as much as the Exponential one

You most likely used the standard deviation instead of the IQR somewhere
in `cauchy_mean_iqr`, or built the Cauchy draws with `rng.standard_normal`
instead of `rng.standard_cauchy`. The whole point of exercise 4 is that the
Cauchy mean's *spread* refuses to shrink; if your measured ratio is
anywhere near the Exponential's ~10x, re-check which NumPy method you
called and which spread function you applied to the result.

## My biased sampler's error shrinks almost as fast as the unbiased one

`biased_pool` is not actually restricting the population. Check that you
compared each value against `numpy.median(population)` with a strict `>`,
and that `sampling_distribution` was called with the *pool*, not the
original population, for the biased measurement. A silent no-op filter --
for example comparing against the wrong array, or using `>=` on a
population with repeated values in a way that includes almost everything
-- produces a "biased" sampler that behaves almost like the unbiased one.

## My bootstrap standard error of the mean does not match `sigma_hat / sqrt(n)`

Check that your `statistic` function operates along `axis=1` on a 2-D
array of shape `(n_boot, len(data))`, not along `axis=0` or over a flat
array -- `bootstrap_replicates` passes the whole batch of resamples at
once, not one resample at a time, and a wrong axis silently computes the
statistic over the wrong dimension without raising an error.

## My AR(1) series does not show the naive/true standard error gap

Check the innovation standard deviation: it must be
`sigma * sqrt(1 - phi**2)`, not `sigma` itself. Using `sigma` directly
makes the series' marginal variance grow without bound as `phi` approaches
1, which changes the comparison in a way that has nothing to do with
dependence.

## `RuntimeWarning: invalid value encountered` from the Cauchy exercise

This is expected on rare draws and does not indicate a bug: the standard
Cauchy distribution has no defined mean or variance, and if you compute a
sample *variance* (rather than the IQR the reference solution uses) on a
large batch of Cauchy draws, an extreme draw can occasionally produce a
value large enough to trigger a NumPy overflow warning during the internal
sum of squares. The lab's own `cauchy_mean_iqr` avoids this entirely by
never computing a variance or standard deviation on Cauchy data.

## `__pycache__` or `.pytest_cache` appears and section 6 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-path ./.venv -prune` in that command, and note that the harness
uses the same prune. NumPy and pytest ship hundreds of their own
`__pycache__` directories inside the virtual environment; those are
theirs, not litter you created, and a check that searched them would
report a failure you cannot fix and did not cause. `.venv` itself is the
documented setup and is never treated as a stray file.

The lab's own commands leave neither directory behind -- the scripts run
with `PYTHONDONTWRITEBYTECODE=1` and the harness's pytest invocations pass
`-p no:cacheprovider`. The harness clears both at the **start** of its run
for the same reason Day 110's did: the README documents
`.venv/bin/pytest starter -q`, which legitimately writes both, and an
earlier version of this style of harness would have then reported them as
litter left by *this* run rather than by that documented command.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `sampling` and `dataset`. Without the
`conftest.py` in each directory, collecting both suites at once would
import whichever copy was seen first and reuse it for the other -- so your
unwritten starter exercises would silently pass against the reference
solution. A wrong answer with a green tick on it is the worst kind of
wrong answer.

If you delete or edit either `conftest.py`, section 4 of the harness will
notice: it compares the skip count from `pytest starter` against the skip
count from `pytest` with no arguments and requires them to be identical.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Nothing in
the lab is platform-specific -- but "should work" and "was run" are
different claims and only the second one is worth making.
