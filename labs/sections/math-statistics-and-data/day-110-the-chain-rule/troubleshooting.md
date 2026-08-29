# Troubleshooting

Every entry below was hit while building this lab, or is named by a test that
exists because of it.

## `ModuleNotFoundError: No module named 'chainrule'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `chainrule`, `autodiff`, `network` and
`dataset` from beside themselves.

```bash
cd examples
../.venv/bin/python3 01_gears_and_rates.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test file's
own directory on the import path.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. Everything in this
lab goes through `.venv/bin/python3`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you would rather use an interpreter you already have, the harness accepts
one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## The starter tests all skip and I have written code

A skip means the function still returns `None`. Look for a leftover
`return None` below the code you added — several of the skeletons have the
`return None` on the last line of a long docstring, and it is easy to write the
body above it and leave the `return None` in place, in which case your work is
computed and then discarded.

For the `Value` class the detection is different: an unwritten `__add__`
returns `None`, so the *next* operation raises a `TypeError`, and the suite
treats that as "not attempted" rather than "wrong". If exercise 2b is skipping
after you wrote it, check that `__mul__` returns the new `Value` rather than
falling off the end of the function.

## My engine gives 1.0 where the answer is 2.0, or 3.0 where it is 6.0

You assigned a gradient where you should have accumulated it. Every backward
step must use `+=`:

```python
self.grad += out.grad          # correct
self.grad = out.grad           # silently wrong on any reused value
```

The symptom only appears when a value is used more than once, which is why
`x + x` and `x * x` are the two tests that catch it. On a straight chain with
nothing reused, the assigning version gives the right answer every time — and
then fails on the first real network, where every input feeds every hidden
unit.

This is the same fact as the two-path example in script 04, compressed into one
character.

## My chain rule is out by a factor of three, or of the inner function's value

You evaluated the outer derivative at `x` instead of at `u = inner(x)`. For
`(3x + 1)²` at `x = 2` the correct answer is `2 × 7 × 3 = 42`; evaluating `2u`
at `x` gives `2 × 2 × 3 = 12`.

This is the most durable mistake in the day because the shape of the answer
still looks right — it is a product of two plausible numbers. `chain_rule` in
the starter deliberately takes `inner` as a separate argument so that the
evaluation point has to be written down.

## My central difference is exactly double the right answer

You divided by `h` instead of by `2h`. The central difference spans an interval
of width `2h`, from `x − h` to `x + h`. There is a test named for this, because
the mistake produces a clean factor of two rather than noise, and a clean
factor is easy to mistake for a units problem.

## My gradient for `x1` is `-6.0` and the test wants `-9.375`

You followed one path and stopped. `x1` feeds hidden unit A *and* hidden unit
B, so it reaches the loss twice, and both contributions are real:

```
      through unit A:  -6.00 x  1.00  = -6.000
      through unit B:   6.75 x -0.50  = -3.375
      total:           -6.000 + -3.375 = -9.375
```

This is the single most instructive failure in the lab, which is why the test
that catches it compares against a central difference rather than against a
table: the measurement has no opinion about which path you meant.

## `RecursionError` when the graph gets deep

Your `topological_order` is recursive. A chain of ten thousand operations is an
ordinary size for a computation graph and there is a reference test that builds
exactly that. Rewrite it with an explicit stack of `(node, already_expanded)`
pairs — the approach note in `starter/autodiff.py` spells out the shape.

## The engine and my hand computation disagree in the fifteenth decimal place

On this network they should agree **exactly**, because both perform the same
multiplications in the same order on values that are all exact in float64. If
they differ at all, one of them is doing the arithmetic in a different order —
most often because the hand version computed `2 * (out - target)` while the
engine reached the same place through `diff * diff` and a product rule, or
because a `1 - b*b` was written as `1 - b**2`.

Both are correct mathematics; only one of them matches bit for bit. If you
prefer your ordering, change the assertion in your own copy to use
`ANALYTIC_TOL` and say why. Do not widen `NUMERIC_TOL` — that tolerance is for
a different comparison entirely.

## A numerical gradient disagrees with my engine in the eighth decimal place

That is correct behaviour, not a bug. A central difference has its own error,
which at `h = 1e-5` runs to a few parts in a billion on these functions. The
lab compares that pair with `NUMERIC_TOL` (1e-6) and compares two analytic
routes with `ANALYTIC_TOL` (1e-12), and the million-fold gap between the two
tolerances is deliberate. `expected-output/FIELDS.md` tabulates both with their
derivations.

If you tighten `NUMERIC_TOL` until it fails, you have not found a bug in the
chain rule — you have rediscovered Day 108.

## My stacked-tanh gradient is nowhere near the prediction

Good. That is the finding, and section 6 of script 07 is about it. Forty
stacked `tanh` operations give a gradient around `8.4e-3` where the
constant-factor prediction says `3.1e-13`. Each `tanh` pulls its input towards
zero, where `tanh`'s slope is 1, so the local rates climb back towards 1 as the
stack deepens. The suite asserts the gap rather than the value.

If your number *does* land near `1e-13`, something is multiplying a fixed
constant where it should be re-evaluating a rate at the current value.

## `__pycache__` or `.pytest_cache` appears and section 7 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-path ./.venv -prune` in that command, and note that the harness uses
the same prune. NumPy and pytest ship hundreds of their own `__pycache__`
directories inside the virtual environment; those are theirs, not litter you
created, and a check that searched them would report a failure you cannot fix
and did not cause. `.venv` itself is the documented setup and is never treated
as a stray file.

The lab's own commands leave neither directory behind — the scripts run with
`PYTHONDONTWRITEBYTECODE=1` and the harness's pytest invocations pass
`-p no:cacheprovider`.

You should not actually be able to hit this, and the reason is worth knowing.
The "How to run" section tells you to run `.venv/bin/pytest starter -q` while
you work, and that command *does* write `starter/__pycache__` and
`.pytest_cache` — it has no reason not to. An earlier version of this harness
would then have reported them as litter at the end, failing you for following
the instructions. So the harness now clears both at the **start** of its run,
pruning `.venv`, which makes the check at the end measure what this run left
rather than what you left earlier. If you edit `tests/run_tests.sh`, keep that
block where it is: removing it makes the suite fail for anyone who ran the
documented command first.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `autodiff`, `chainrule`, `dataset` and
`network`. Without the `conftest.py` in each directory, collecting both suites
at once would import whichever copy was seen first and reuse it for the other —
so your unwritten starter exercises would silently pass against the reference
solution. A wrong answer with a green tick on it is the worst kind of wrong
answer.

If you delete or edit either `conftest.py`, section 4 of the harness will
notice: it compares the skip count from `pytest starter` against the skip count
from `pytest` with no arguments and requires them to be identical.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash with
`.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Everything in the
lab is plain arithmetic and standard-library Python, so nothing in it is
platform-specific — but "should work" and "was run" are different claims and
only the second one is worth making.
