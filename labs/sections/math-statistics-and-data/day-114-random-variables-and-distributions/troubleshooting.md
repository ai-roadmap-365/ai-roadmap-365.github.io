# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'distributions'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `distributions`, `sampling` and `dataset`
from beside themselves.

```bash
cd examples
../.venv/bin/python3 01_pmf_of_a_sum.py
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

A skip means the function still raises `NotImplementedError`. Look for a
leftover `raise NotImplementedError` below the code you added -- it is easy
to write the body above it and leave the raise in place, so your work never
runs at all.

## `dice_sum_pmf()` fails a test even though the count looks right

Check the return type. Every value must be a `fractions.Fraction`, not a
`float`. `Fraction(1, 6) == 0.16666666666666666` compares `False` for most
fractions because a float cannot represent one exactly, and this lesson's
whole point about exact rational arithmetic depends on that distinction
being real.

## My `pmf[7]` is not exactly six times `pmf[2]`

Both counts should come straight out of the same enumeration over the 36
outcomes of `itertools.product(range(1, 7), range(1, 7))`. If the ratio
comes out wrong, print the raw counts dictionary before converting to
`Fraction` -- the usual mistake is summing `a + b` as strings, or counting
ordered pairs incorrectly (there are 6 pairs that sum to 7 and only 1 that
sums to 2, not the other way round).

## `E[X + Y] != E[X] + E[Y]` in my linearity exercise

Linearity should hold EXACTLY, with no tolerance needed, because both sides
are exact `Fraction` sums over the same 36-outcome equally-weighted space.
If they disagree, check that `X` and `Y` are being evaluated on the SAME
outcome inside `expectation_over`'s `func` argument -- a common mistake is
computing `E[X] + E[Y]` correctly but computing `E[X+Y]` over a
mismatched or re-ordered iterable, so the two sides silently sum over
different pairings.

## `Var[X + Y] == Var[X] + Var[Y]` in my non-additivity exercise

This should be FALSE for the dependent pair used here (X = first die, Y =
sum of both dice). If your two variances come out equal, the most likely
cause is that `covariance_over` returned exactly 0 when it should not have
-- print `Cov(X, Y)` directly; for this pair it is `Fraction(35, 12)`, not
zero, and that non-zero value is exactly what makes the naive sum wrong.

## My Jensen's-inequality gap does not equal the variance

`E[X^2] - (E[X])^2` should equal `Var[X]` exactly, by the two-line algebraic
identity `Var[X] = E[X^2] - (E[X])^2`. If your two numbers differ, check
that both `E[X^2]` and `Var[X]` are computed over the SAME `outcomes` and
`weight` -- a mismatch there (for example, computing one over the die alone
and the other over the two-dice joint space) breaks the identity even
though each side is individually correct for its own space.

## My discrete sampler's empirical frequencies are outside tolerance

First check that `sample_discrete_inverse_cdf` clamps the last cumulative
entry to exactly `1.0` -- floating-point summation of many probabilities
can land at `0.999999999999` instead of 1, which silently drops the
largest value from ever being drawn. If the clamp is in place and the gap
is still outside three standard errors, that is not automatically a bug:
about 0.3% of honest runs will, by construction, land outside a
three-standard-error band. Re-run with a different seed before assuming
the sampler is wrong.

## Two runs with the same seed give different discrete draws

You are calling `numpy.random.seed(n)` somewhere instead of building a
`Generator` with `numpy.random.default_rng(n)`. The legacy `seed()`
function mutates one global state shared across your whole process --
importing a library that seeds it, or calling any other function that also
draws from the global generator, changes what your "same seed" produces
next. Pass the `Generator` object itself into every function that needs
randomness, as `sampling.py` does, and reproducibility stops depending on
what else ran first.

## My exponential sampler produces negative values

`-ln(U) / rate` is only non-negative when `U` is strictly inside `(0, 1)`.
`rng.random()` returns values in `[0.0, 1.0)`, so `U` can legitimately be
exactly `0.0` -- at which point `ln(0)` is `-inf` and the sample becomes
`+inf` (still non-negative, just unbounded), not negative. If you are
seeing actual negative values, check the sign: it must be `-np.log(draws)`,
not `np.log(draws)` or `np.log(-draws)`.

## My max-gap statistic between the two exponential samples is above threshold

Confirm both samples are the same size and drawn with the same rate (`rate
= 2.0` here, so `scale = 1 / rate = 0.5` for NumPy's own `.exponential()`
call, which takes a scale, not a rate). If the sizes and rate are correct
and the gap is still above `dkw_two_sample_threshold`, try a different
seed -- the DKW-derived threshold is generous but not infinite, and a small
fraction of runs will legitimately exceed it by chance.

## My Poisson-as-Binomial-limit gap does not shrink monotonically

Check that `p = lambda / n` is recomputed at every `n` -- `p` must shrink
as `n` grows so that `n * p` stays fixed at `lambda`. If `p` is held fixed
instead of `lambda`, the Binomial distribution does not converge to
anything and the gap will not shrink.

## `numeric_integral` raises `ValueError` when I expected a number

`steps` must be at least 1; the function is written to refuse `steps=0`
rather than divide by zero silently. Pass a large step count (`50_000` or
more) for a numerically accurate integral of the density.

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

You should not actually be able to hit this. The "How to run" section
tells you to run `.venv/bin/pytest starter -q` while you work, and that
command *does* write `starter/__pycache__` and `.pytest_cache` -- it has no
reason not to. The harness clears both at the **start** of its run,
pruning `.venv`, so the check at the end measures what *this* run left
rather than what an earlier command left. If you edit `tests/run_tests.sh`,
keep that block where it is.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `distributions`, `sampling`, `dataset`
and `answers`. Without the `conftest.py` in each directory, collecting
both suites at once would import whichever copy was seen first and reuse
it for the other -- so your unwritten starter exercises would silently
pass against the reference solution. A wrong answer with a green tick on
it is the worst kind of wrong answer.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Everything
in the lab is plain arithmetic, standard-library Python and NumPy, so
nothing in it is platform-specific -- but "should work" and "was run" are
different claims and only the second one is worth making.
