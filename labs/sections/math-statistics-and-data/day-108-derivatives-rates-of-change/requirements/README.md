# What this lab installs, and what it costs you

Two packages, both free, both open source, no account and no key.

| Package | Version pinned here | Licence | Why it is here |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | Two jobs only. `numpy.gradient` is the library alternative your from-scratch central difference is compared against, bit for bit. And `numpy.finfo(numpy.float64).eps` is where the machine epsilon in `dataset.py` is checked against rather than trusted. |
| `pytest` | 9.1.1 | MIT | Runs both suites: the 178 reference tests in `examples/` and your running score in `starter/`. |

Both versions are pinned exactly. Section 1 of `tests/run_tests.sh` reads the
installed numpy and compares it against this file rather than trusting it, so a
mismatch is reported rather than discovered later as a puzzling number.

## Why a version this specific

Less than usual, and it is worth saying so plainly. Almost every number in this
lab comes from `math` and plain float64 arithmetic, and would be identical with
no third-party package at all. NumPy is pinned because two claims depend on it:

- **`np.gradient` with a scalar spacing is bit-for-bit the central difference
  you wrote**, and with an array of coordinates it is not — it takes its general
  unevenly-spaced route and lands a few units in the last place away. Both facts
  are asserted, so a future NumPy that changed either would be reported rather
  than quietly making this lesson wrong.
- **`np.finfo(np.float64).eps` is the value `dataset.EPSILON` claims it is.**
  Every tolerance in the lab is derived from that number, so it is checked
  rather than copied from memory.

The harness also confirms the interpreter's floats are IEEE-754 doubles with a
53-bit significand, because the entire U-shaped error curve is a consequence of
that width.

## The network

Installing these two packages is the only thing in this lab that touches the
network. Nothing here opens a socket, reads a URL or needs an API key, and
section 7 of the test harness greps every source file in `examples/` and
`starter/` to prove it.

## If you cannot install anything at all

You can do most of this lab, which is unusual and is worth taking advantage of.

On a bare `python3` with only the standard library you can write every one of
the ten functions in `starter/derivatives.py`, run the shrinking-interval
sequence, measure the U-shaped error curve across all 27 step sizes, find the
best `h`, classify every stationary point, and reproduce both corner cases. All
of it needs `math` and nothing else.

What you lose: the two `np.gradient` comparisons, the float64 array form of the
error curve, the epsilon cross-check, and the ability to run `pytest`, which
means you would have to call your functions by hand and read the numbers
yourself instead of getting a score.

## Disk

Roughly 60 MB for the virtual environment, almost all of it NumPy. `rm -rf
.venv` from the lab directory is a complete undo.
