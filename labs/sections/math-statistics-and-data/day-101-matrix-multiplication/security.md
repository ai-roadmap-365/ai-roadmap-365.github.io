# Security notes — Day 101 lab

This lab multiplies small integer matrices and times a loop. It is one of the
least dangerous things in the course. The notes below are short because there
is little to say, and they are here rather than absent because "there is
nothing to worry about" is a claim that should still be checked.

## What this lab does to your machine

- **It computes and prints.** No file is created, no database is opened, no
  process is started, no port is bound.
- **It opens no network connection.** Not once, in any script or test. Section
  7 of `tests/run_tests.sh` greps every file under `examples/` and `starter/`
  for `urlopen`, `requests.`, `socket.` and `http`, and fails if any appears.
- **It needs no credentials.** No account, no key, no token, no paid service.
- **It needs no `sudo`.** If any instruction in this lab appears to require
  elevated privileges, that instruction is wrong; stop and re-read it.
- **It writes nothing outside its own directory**, and by the time the harness
  finishes there is nothing left inside it either. Section 7 checks for stray
  `__pycache__` and `.pytest_cache` directories and fails if it finds one.

## The one thing that touches the network

`pip install -r requirements/requirements.txt` downloads two packages from the
Python Package Index. That is the whole network story, it happens once, and
after it you can disconnect for good.

Two habits from Day 43 still apply and are worth restating:

- **Install into a virtual environment, not the system Python.** The commands
  in this lab create `.venv/` inside the lab directory precisely so that a
  mistake here cannot affect anything else on your machine, and so that
  `rm -rf .venv` is a complete undo.
- **Read the package name before you press return.** Typo-squatting on package
  indexes is real: a package named one character away from `numpy` is not
  NumPy. The pinned file spells both names out so you are copying rather than
  typing.

## The one resource this lab can actually exhaust

The timing script is the only part of this lab that can make your machine
uncomfortable, and only if you change it. `matmul_loops` does `m * n * p`
interpreted operations, so the cost grows as the **cube** of the size:

| Size | Multiplications | Roughly |
| --- | --- | --- |
| 120 | 1,728,000 | a moment |
| 200 | 8,000,000 | captured here at about a fifth of a second |
| 1000 | 1,000,000,000 | minutes, and no output until it finishes |
| 5000 | 125,000,000,000 | do not |

Nothing in the lab as shipped goes above 200, and nothing allocates enough
memory to matter — the largest array here is 200 by 200 float64, which is
320 KB. If you raise the size while exploring the extension exercises, raise it
by doubling and watch what happens, rather than jumping to a round number. The
cube is not intuitive until you have been caught by it once.

There is no `try`/`except` that will save you from this, and no exception is
raised; the process simply does not come back. `Ctrl-C` is the remedy.

## Numerical honesty, which is the security-flavoured lesson here

Two facts from this lab are worth carrying into code you actually ship.

**Integer matrix products can overflow silently.** NumPy integer arrays are
fixed-width — `int64` here — and they wrap around rather than raising. Python's
own integers are arbitrary-precision and do not. So the from-scratch
implementation and NumPy genuinely disagree on large values, and NumPy is the
one that is wrong:

```python
big = [[3037000500, 0], [0, 1]]
np.array(big) @ np.array(big)   ->  [[-9223372036709301616, 0], [0, 1]]
matmul_loops(big, big)          ->  [[ 9223372037000250000, 0], [0, 1]]
3037000500 ** 2                 ==    9223372037000250000
```

That was run, not reasoned about. **No warning is raised** — the array simply
contains a large negative number where a large positive one belongs.
`test_numpy_integer_products_overflow_silently` in the reference suite asserts
it, including the absence of a warning, so the claim stays honest if NumPy ever
changes its behaviour.

Every number elsewhere in this lab is far too small for this to happen, and that
is a property of the data chosen rather than a guarantee of the code. If you
feed real data in, check the range first, or use a float dtype — which loses
precision gradually and visibly instead of catastrophically and silently.

**Floating-point addition is not associative.** Section 1 of
`05_cost_and_speed.py` demonstrates it: with `float64` inputs, `(A @ B) @ C` and
`A @ (B @ C)` are equal to within `1e-9` but **not** bit-for-bit identical, even
though they are the same computation in mathematics. The consequence for
anything you write: never compare two float results with `==`, always state a
tolerance, and be suspicious of any test that passes only because two libraries
happened to sum in the same order. Day 70 covered why.

## About the data

Everything in `examples/dataset.py` is invented — the batch, the weights, the
bias, the two geometric transformations and the shapes used in the cost
examples. It represents nothing real and contains nothing personal.

If you replace it with data of your own, be aware that `X` in this lab has
exactly the shape real personal data arrives in: rows are people and columns are
facts about them. The moment you paste that into a lab directory, ordinary care
applies again — do not commit it, do not copy it somewhere it does not belong,
and prefer a small invented sample for anything you are only using to learn.

One further note specific to this day. A trained weight matrix is not
anonymous. `W` is derived from the data it was trained on, and matrix
multiplication is invertible often enough that "we only shipped the weights, not
the data" is a weaker claim than it sounds. That is well beyond today's scope
and is not a reason to worry about anything in this lab, but it is the right
instinct to form now rather than later.
