# Troubleshooting

Every problem below was hit while building this lab, not imagined for the
document. Where something was not run here, it says so.

## `ModuleNotFoundError: No module named 'numpy'`

The virtual environment is not installed, or you are running the system
`python3` instead of the lab's. From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. Then run everything through `.venv/bin/python3` and
`.venv/bin/pytest`, not through a bare `python3`.

## `ModuleNotFoundError: No module named 'vectorize'`

You are in the wrong directory. The scripts in `examples/` import `vectorize.py`
and `dataset.py` from beside themselves, so they must be run from inside
`examples/`:

```bash
cd examples
../.venv/bin/python3 01_list_versus_array.py
```

The pytest suites are the other way round — run those from the **lab**
directory, because the paths `examples` and `starter` are relative to it:

```bash
.venv/bin/pytest starter -q
```

## The starter tests pass without me writing anything

They should not, and if they do, something has gone wrong with the import
guard. Both `examples/` and `starter/` contain modules called `vectorize` and
`dataset`, and pytest imports a test file by putting its directory on
`sys.path`. Collecting both at once could therefore let the starter tests import
the finished reference implementation and report unwritten exercises as passing
— a wrong answer with a green tick on it.

`conftest.py` in each directory prevents that by putting its own directory first
and evicting any `vectorize`, `dataset` or `answers` already imported from
elsewhere. If you delete either `conftest.py`, this breaks. Section 4 of
`tests/run_tests.sh` checks it is still working by running both suites together
and asserting the skip count has not changed.

## `ValueError: The truth value of an array with more than one element is ambiguous`

This is the day's headline error and it has three separate causes.

**You used `and` or `or` between two masks.** Use `&` and `|`:

```python
(a > 30) & (a < 70)      # right
(a > 30) and (a < 70)    # raises
```

`and` is a control-flow keyword, not an operator, so NumPy cannot redefine it.
Python asks the left operand "are you true?", and an array of twenty answers
cannot say.

**You left the parentheses off.** `&` binds tighter than `<`, so
`a > 30 & a < 70` parses as `a > (30 & a) < 70` — a bitwise-and followed by a
chained comparison, which calls `bool()` on an array. Same error, entirely
different cause. Always bracket each comparison.

**You put an array in an `if`.** `if a > 5:` cannot work. Decide which question
you are actually asking and use `.any()` or `.all()`, which is exactly what the
error message suggests.

## My filter for missing values finds nothing

You wrote `a == np.nan`. It returns all `False`, including for the element that
*is* nan, because IEEE-754 says nan compares unequal to everything including
itself. Use `np.isnan(a)`. Section 2 of
`examples/07_nan_and_when_not_to_vectorise.py` shows both side by side.

## I changed one array and a different one changed too

You have a view. A slice, a transpose, a reshape and `ravel()` all hand back a
new way of reading the *same bytes*, so writing through one writes through to
the other. This is the hardest NumPy bug to find because the code that breaks is
nowhere near the code that caused it.

Two habits fix it. Check with `np.shares_memory(a, b)` when you are unsure, and
call `.copy()` when you intend to own the result. Section 4 of
`examples/06_axes_views_and_ranking.py` lists which operations do which.

Note the near-identical pair: `ravel()` returns a view when it can, `flatten()`
always copies.

## My int8 arithmetic gives negative numbers

It overflowed. An int8 holds -128 to 127, and 127 + 1 wraps to -128 with no
exception and — on numpy 2.5.2, measured — no warning either. Adding a plain
Python `1` does not rescue it: since NumPy 2 the scalar takes the array's dtype,
so the result stays int8 and still wraps.

Fix it by asking for the width you meant, with `.astype(np.int16)` before the
arithmetic. Check `a.dtype` first whenever a number looks impossible.

## My results changed between runs

You used `numpy.random.seed(...)` or an unseeded generator. `numpy.random.seed`
sets one global generator that every library in the process shares, so a call
you did not write can move your sequence. Use
`rng = np.random.default_rng(104)` and pass `rng` around. Every number in this
lab is stable for exactly that reason.

## `axis=0` gave me the wrong number of results

The rule is: **the axis you name is the one that disappears.** A `(3, 4)` array
summed with `axis=0` gives 4 numbers, not 3. If you are reading it as "which
axis do I want to keep", you will be off by exactly one every time.

If you then need to divide the original array by the result, add
`keepdims=True` so the shape stays open and broadcasting lines up.

## `ValueError: operands could not be broadcast together`

Two arrays whose shapes cannot be reconciled. Print both shapes before the line
that failed — `print(a.shape, b.shape)` — because the shapes are almost always
the whole story. `np.newaxis` or `reshape(-1, 1)` is usually what is missing.

## The speedup on my machine is much smaller than the captured one

That is expected and it is not a failure. The captured run measured 106x to
134x on Apple Silicon with numpy 2.5.2. The tests assert only that the ratio is
above 20, deliberately, because a test that asserted a millisecond figure would
fail on someone else's laptop and teach you that the suite is unreliable rather
than that your laptop is different. `expected-output/FIELDS.md` says which
numbers are allowed to move.

If your ratio is below 20, check that you are timing the loop over a *list* and
the vectorised version over an *array*. Looping over an ndarray with a Python
`for` is slower than looping over a list, because every element has to be boxed
into a Python object on the way out — which would flatter the comparison in the
wrong direction.

## `x ** 0.5` and `np.sqrt` give me different numbers

They are different operations, and this is the honest finding the lab keeps
rather than tidying away. IEEE-754 requires square root to be correctly rounded
and both `math.sqrt` and `np.sqrt` use the hardware instruction that obeys that.
`pow(x, 0.5)` is a general power routine with no such guarantee, and here it
differs on about one value in seven hundred, always by one unit in the last
place. Use `math.sqrt` in the loop if you want the two to match exactly.

## The `test_1_3_and_1_4_agree_exactly` test fails but `test_1_3` passes

Almost certainly the same thing: your `roots_loop` uses `x ** 0.5`. Change it to
`math.sqrt(x)`.

## `__pycache__` or `.pytest_cache` appeared

Run the cleanup from the lab directory:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

The lab's own commands leave neither behind — `PYTHONDONTWRITEBYTECODE=1` is
exported by the harness and `-p no:cacheprovider` is passed to pytest. Section 7
of the harness fails if either appears outside `.venv`. It deliberately does not
look inside `.venv`, because the bytecode caches shipped with NumPy and pytest
are theirs and not yours.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or Git Bash with
`.venv\Scripts\python.exe` in place of `.venv/bin/python3`. The bash harness
needs a bash; PowerShell will not run it.

## Linux

Not run here either. The commands are identical and nothing in this lab touches
a macOS-specific interface, but no claim is made about output that was not
captured. The `platform` line will differ, and so will every timing.
