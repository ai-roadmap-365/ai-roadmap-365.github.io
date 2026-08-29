# What this lab installs, and what it costs you

Two packages, both free, both open source, no account and no key.

| Package | Version pinned here | Licence | Why it is here |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | Vectors, dot products, `linspace`, and the trigonometry used to sweep 360 directions around a circle. The gradient machinery itself is written from scratch; NumPy holds the results. |
| `pytest` | 9.1.1 | MIT | Runs both suites: the reference tests in `examples/` and your running score in `starter/`. |

Both versions are pinned exactly. Section 1 of `tests/run_tests.sh` reads the
installed numpy and compares it against this file rather than trusting it, so a
mismatch is reported rather than discovered later as a puzzling number.

## What NumPy is and is not doing here

It is worth being precise, because NumPy has a function called `gradient` and
this lab has one too.

**NumPy is not computing any derivative in this lab.** Every partial
derivative, every gradient and every directional derivative comes from
`examples/gradients.py`, which evaluates the function at two points and
subtracts. NumPy supplies arrays, `np.dot`, `np.linspace`, `np.cos` and
`np.sqrt`, and holds the answers.

`numpy.gradient` appears once, in script 06, and it is there to be
*distinguished* from ours rather than used. It differences an array of values
already sampled on a grid; ours differences a function it can call at any point
it likes. Section 4 of that script measures the consequence: on a cubic,
NumPy's error is the grid spacing squared, which is fixed by the data you were
given, while ours picks its own step and lands ten orders of magnitude closer.

Two facts about `numpy.gradient` are asserted rather than described, so that a
future release changing either would fail the suite instead of quietly making
this page wrong:

- Interior values on a sampled quadratic come out **exact**, because a central
  difference is algebraically exact for a quadratic at any spacing.
- Boundary values default to a **first-order** one-sided formula, so the corner
  of that same exact quadratic comes out as `(0.5, 1.5)` where `(0, 0)` is
  correct. Passing `edge_order=2` fixes it exactly. That default costs people
  an afternoon reasonably often.

## The network

Installing these two packages is the only thing in this lab that touches the
network. Nothing here opens a socket, reads a URL or needs an API key, and
section 7 of the test harness greps every source file in `examples/` and
`starter/` to prove it.

## If you cannot install anything at all

You can do more of this lab than you might expect, and it would be dishonest to
pretend you can do all of it.

What works on a bare `python3` with only the standard library, if you replace
the handful of `np` calls with `math` and plain lists:

- `partial` and `forward_partial`, which are two evaluations and a subtraction;
- `gradient`, which is a loop over `partial`;
- `magnitude` and `unit`, which need `math.sqrt`;
- every prediction in `starter/answers.py`, which is where most of the thinking
  lives and none of which requires running anything.

What you lose is the sweep of 360 directions, the contour work, and the
comparison with `numpy.gradient` — that is, most of the *evidence*, though not
most of the *reasoning*.

## Disk

Roughly 60 MB for the virtual environment, almost all of it NumPy. `rm -rf
.venv` from the lab directory is a complete undo.
