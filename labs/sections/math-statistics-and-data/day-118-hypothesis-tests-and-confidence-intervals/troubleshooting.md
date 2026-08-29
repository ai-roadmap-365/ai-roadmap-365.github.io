# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'inference'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `inference` and `dataset` from beside
themselves.

```bash
cd examples
../.venv/bin/python3 01_two_sample_z_test.py
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
`starter/inference.py` has `return None` as its last line -- write your
body above it and replace that line with your own `return`, rather than
adding code before an unchanged `return None`.

## My `z_critical_two_sided` does not match the known constant

`z_critical_two_sided` finds z by bisecting `phi`, so it depends on `phi`
already being correct. Check `phi(0.0) == 0.5` and `phi(1.96)` is close to
`0.975` first. A common mistake is bisecting on the wrong target: you want
the z where `phi(z) == 1 - alpha/2`, not `alpha/2` or `alpha`.

## My two-sample z-test disagrees with the hand computation past a few decimals

Check that you are dividing by `n_a` and `n_b` separately inside the
standard error -- `sqrt(var_a / n_a + var_b / n_b)` -- rather than pooling
the two variances into one shared estimate divided by a combined `n`. The
pooled-variance z-test is a legitimate different test with a different
formula; this lab's `two_sample_z_test` is deliberately the unpooled
version, which is what makes it the large-sample cousin of Welch's t-test
described in the lesson's Tools section.

## My coverage measurement is consistently a point or two below 95%

If you changed `COVERAGE_SAMPLE_N` to something small (under about 100),
this is expected and is itself a real, teachable effect: `confidence_
interval_mean` uses a *normal* critical value, not a *t* critical value,
and at small n the true sampling distribution of the standardized mean has
heavier tails than normal, so a normal-based interval slightly undershoots
its nominal coverage. This lab's exercises use `n=300` specifically so
that gap is small enough to fall inside the 3-standard-error tolerance.

## My permutation test's p-value is exactly 0.0

It should never be able to reach exactly zero. `permutation_test_diff_
means` computes `p = (count_as_extreme + 1) / (n_perm + 1)`, not
`count_as_extreme / n_perm` -- the "+1" in both numerator and denominator
accounts for the observed arrangement itself being one of the possibilities
being counted, and guarantees `p >= 1 / (n_perm + 1)`. If your p-value can
read as `0.0`, you have dropped one or both of the "+1"s.

## My peeking false-positive rate is close to 0.05, not far above it

Check that you are testing the *cumulative* data after every batch (all
observations collected so far), not re-testing only the newest batch of
10 each time. Peeking inflates the false-positive rate specifically
because each look uses more data than the last while sharing information
with every earlier look; testing five independent, non-overlapping
batches of 10 and taking the best p-value is a different (also inflated,
but differently so) procedure than this lab's.

## My power calculation does not match the simulation

`power_two_sample_z` assumes both groups share the same *known* sigma and
the same n. If you changed either sample's generating standard deviation
away from `dataset.POP_STD` without updating the `sigma` argument passed
to `power_two_sample_z`, the closed form and the simulation are answering
different questions and will disagree.

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
earlier version of this style of harness would then have reported them as
litter left by *this* run rather than by that documented command.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `inference` and `dataset`. Without the
`conftest.py` in each directory, collecting both suites at once could
import whichever copy was seen first and reuse it for the other -- so your
unwritten starter exercises would silently pass against the reference
solution. A wrong answer with a green tick on it is the worst kind of
wrong answer.

If you delete or edit either `conftest.py`, section 4 of the harness will
notice: it compares the skip count from `pytest starter -q` against the
skip count from `pytest -q` run with no arguments from the lab directory,
and requires them to be identical. (Explicitly passing both directory
names as two separate arguments on one command line -- `pytest examples
starter` -- is a different invocation than either of those, is not what
this lab documents or tests, and was observed during development to
collide in a way neither of the tested invocations does; stick to the
documented commands.)

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Nothing in
the lab is platform-specific -- but "should work" and "was run" are
different claims and only the second one is worth making.
