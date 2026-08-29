# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'descriptive'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `descriptive`, `simulate` and `dataset`
from beside themselves.

```bash
cd examples
../.venv/bin/python3 01_mean_median_mode.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test
file's own directory on the import path.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. Everything here
goes through `.venv/bin/python3`:

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

A skip means the function still raises `NotImplementedError` or still
returns `None`. Look for a leftover `raise NotImplementedError` below the
code you added — it is easy to write the body above it and leave the raise
in place, so your work never actually runs.

## My median moves when I corrupt one salary

It should not, exactly. If `breakdown_point_median` moves at all, check
that you are computing the median of the **corrupted** list, not comparing
against a stale copy, and that you sort before finding the middle element.
The median only depends on the *rank* of the middle value, and the
corrupted value — however extreme — still occupies the same rank position
(the single largest of nine) as the value it replaced.

## My Bessel-correction ratio is not close to `(n-1)/n`

Two usual causes. First, check the divisor: the biased estimator divides
the sum of squared deviations by `n`, the unbiased one by `n - 1` — swap
them and the ratio flips to the reciprocal. Second, check that you are
using the *sample* mean (computed from each sample) inside the squared
deviation, not the *population* mean — using the true population mean would
give an unbiased estimate even when dividing by `n`, and that is a
different (also true, also useful) fact from the one this exercise
measures.

## `percentile_under` gives one number and I expected NumPy's default

You may have called `numpy.percentile()` without `method=`, which silently
uses `'linear'` — the same number this lab calls the default, so this is
usually not actually a bug, just a check that you passed the argument
explicitly. `percentile_under` should always take `method` as a required
argument precisely so the convention is never accidentally implicit.

## My Pearson correlation on the parabola is not exactly `0.0`

It should land within `PARABOLA_PEARSON_TOLERANCE` (`1e-9`) of zero, not
necessarily bit-for-bit `0.0` — the test compares against a tolerance for
exactly this reason. If it is nowhere near zero, check that `PARABOLA_X`
runs symmetrically through zero (`range(-5, 6)`, not `range(0, 11)`); the
cancellation that drives Pearson to zero depends on the x-values being
symmetric around their own mean.

## My Anscombe summaries do not agree across the four sets

Check you are reading `ANSCOMBE_SETS` correctly — each entry is `(x, y)`,
and set IV's `x` values are different from sets I, II and III (`8` repeated
ten times, then one `19`), while its `y` values are unique to it too. A
common copy-paste mistake is reusing set I's `x` for set IV, which changes
the story entirely — set IV's whole point is that its `x` values are
almost all identical.

## My `shape_statistics` values do not separate the sets the way the lesson says

Leverage depends **only on x**, not on y — if you compute it using `y`
anywhere, sets I, II and III (which share the same `x` column) will stop
agreeing with each other, which is itself the tell that something is wrong.
The outlier ratio and sign-change count, by contrast, depend on the
residuals, which need both `x` and `y` and the fitted `slope`/`intercept`.

## My Simpson's-paradox subgroup rates look right but the overall rates are wrong

`combined_rate` must pool the **raw counts** (total successes over total
trials) across subgroups, not average the two subgroup *rates*. Averaging
the rates gives `(100% + 10%) / 2 = 55%` for treatment A, which is not the
same question as "what fraction of all 91 trials succeeded" (`11%`) — and
using the wrong one is exactly the kind of error that would hide the
paradox instead of demonstrating it.

## My contamination multipliers do not look dramatic

Check the outlier values themselves (`CONTAMINATION_OUTLIERS`) are still
`(500.0, 520.0, 480.0)` against a clean sample centred near `100.0` — three
points roughly 80 standard deviations away from the clean mean. If you
reduce the outliers to something closer to the clean distribution, both the
standard deviation and the MAD move less, and the contrast this exercise
depends on shrinks or disappears. That is not a bug; it is the same
mechanism at lower contrast.

## Two runs with the same seed give different results

You are calling `numpy.random.seed(n)` somewhere instead of building a
`Generator` with `numpy.random.default_rng(n)`. The legacy `seed()`
function mutates one global state shared across your whole process —
importing a library that seeds it, or calling any other function that also
draws from the global generator, changes what your "same seed" produces
next. Pass the `Generator` object itself into every function that needs
randomness, as `simulate.py` does, and reproducibility stops depending on
what else ran first.

## `__pycache__` or `.pytest_cache` appears and section 7 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-path ./.venv -prune` in that command, and note that the harness
uses the same prune. NumPy and pytest ship hundreds of their own
`__pycache__` directories inside the virtual environment; those are theirs,
not litter you created. `.venv` itself is the documented setup and is never
treated as a stray file.

You should not actually be able to hit this. The "How to run" section tells
you to run `.venv/bin/pytest starter -q` while you work, and that command
*does* write `starter/__pycache__` and `.pytest_cache` — it has no reason
not to. The harness clears both at the **start** of its run, pruning
`.venv`, so the check at the end measures what *this* run left rather than
what an earlier command left. If you edit `tests/run_tests.sh`, keep that
block where it is.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `dataset`, `descriptive`, `simulate` and
`answers`. Without the `conftest.py` in each directory, collecting both
suites at once would import whichever copy was seen first and reuse it for
the other — so your unwritten starter exercises would silently pass against
the reference solution. A wrong answer with a green tick on it is the worst
kind of wrong answer.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash with
`.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Everything in
the lab is plain arithmetic, standard-library Python and NumPy, so nothing
in it is platform-specific — but "should work" and "was run" are different
claims and only the second one is worth making.
