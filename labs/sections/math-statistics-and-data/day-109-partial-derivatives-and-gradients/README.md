# Day 109 lab — Which Way Is Uphill?

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Partial Derivatives and Gradients
- **Day number:** 109 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-109-partial-derivatives-and-gradients
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-109-partial-derivatives-and-gradients` when the site is running.
<!-- generated-links:end -->

## Purpose

Yesterday you learned to ask a curve how steep it is. Today the ground has two
directions to walk in, and "how steep is it" stops having one answer.

Stand on a hillside. There is a slope going north and a different slope going
east, and a different one again for every bearing in between. A **partial
derivative** picks one of them: freeze every input but one, which turns a
function of several variables into a function of one, and take yesterday's
derivative of that. Collect one partial per input into a vector and you have
the **gradient** — and the gradient does something none of the individual
partials do. It points straight uphill, and its length is how steep that is.

This lab builds all of it from nothing. `partial` is four lines. `gradient` is
a loop over `partial`. Everything after that is built from those two.

Then it does the part that matters, which is not building them but **checking
them**, because two claims get made about gradients everywhere and demonstrated
almost nowhere:

- **The gradient is the steepest way up.** The lab measures the rate of change
  along 360 bearings, one per degree, each one with a direct central difference
  that never forms a gradient at all — and asserts that the winner is the
  gradient's own bearing, to within the half-degree the sampling allows. It
  also asserts the sharper form: the winning rate divided by the gradient's
  length equals the cosine of the sampling gap, to nine decimal places.

- **The gradient is perpendicular to the contour.** This one is easy to fake:
  rotate the gradient ninety degrees, call that the contour direction, and
  marvel that they are perpendicular. So the lab does not do that. Each contour
  is an exact algebraic curve derived on paper from the function alone, checked
  first to confirm it really does hold `f` constant, and only then dotted with
  the gradient. The answer is not zero — a chord is not a tangent — so the
  evidence is the dot product shrinking tenfold for every tenfold smaller step.

Around that spine: directional derivatives, which are Day 103's dot product
doing real work; the constant gradient of a plane and the outward-pointing
gradient of a bowl; a zero gradient at a minimum, a maximum and a saddle, all
three identical and all three different; Day 108's U-shaped error curve, with
the cubic's truncation error coming out as *exactly* `h^2`; and a
three-parameter model whose gradient is one number per parameter, which is the
whole of Day 111 waiting to happen.

Two findings in this lab were discovered while building it rather than planned,
and both are kept. Section 1b of script 05 exists because an assertion failed at
the point `(1000, -1000)`: a plane's gradient is constant, but the numerical
estimate of it degrades in proportion to the *size of `f`*, and the bound
`eps * |f| / 2h` predicts the damage across seven orders of magnitude. And the
reference suite asserts a law about sampling rather than the plausible-sounding
claim that a finer sweep always finds a better bearing, because at this
particular point a 60-direction sweep and a 360-direction sweep leave *exactly*
the same gap.

## Learning objectives

By the end you will be able to:

- Say what a partial derivative is in one sentence — one input moves, the rest
  are held still — and compute one by hand and numerically.
- Explain why the symbol uses a rounded `d` and what it is announcing.
- Build a gradient as the vector of partials, for a function of any number of
  inputs, and say why it has one component per INPUT rather than one per
  dimension of the graph.
- Read a gradient's two pieces separately: direction is which way is uphill,
  length is how steep.
- Compute a directional derivative two ways — as a dot product with the
  gradient, and by measuring directly along the direction — and use their
  agreement as evidence rather than taking the rule on trust.
- Demonstrate, not assert, that no direction climbs faster than the gradient.
- Demonstrate, not assert, that the gradient is perpendicular to the contour,
  and explain why deriving the contour direction from the gradient would prove
  nothing.
- State what a contour and a level set are, and why every optimisation picture
  in the rest of the course is drawn with them.
- Recognise a stationary point, and say plainly what a zero gradient does not
  tell you: minimum, maximum and saddle are indistinguishable from it.
- Choose a step size deliberately, predict the `h^2` law, and locate the trough
  of the error curve for both a central and a forward difference.
- Say what `numpy.gradient` does, why it is a different job, and what its
  `edge_order` default costs you.
- Count the cost of a numerical gradient — two evaluations per parameter — and
  say precisely why that is not how a model is trained.

## Prerequisites

- Day 108 — derivatives, the central difference, and the U-shaped error curve.
  Today is that, plus the words "and hold everything else still".
- Day 99 — vectors, length and unit vectors. A gradient is a vector.
- Day 103 — the dot product, and its geometric reading as
  `|a| |b| cos(angle)`. That reading is what makes steepest ascent work.
- Day 104 — NumPy arrays, `linspace`, and elementwise arithmetic.
- Day 70 — floating point, which is why one whole section of this lab is about
  what happens when you subtract two nearly equal numbers.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 071–074 — running pytest and reading its output.
- No calculus beyond Day 108. No school calculus is assumed anywhere.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly
  rather than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest array in the lab is a 9 by 9 grid. The
360-direction sweep evaluates a two-input function 720 times, which is
instantaneous. Roughly 60 MB of disk for the virtual environment, almost all of
it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence and
pytest under the MIT licence. No account, no key, no signup, personally or
commercially.

If you cannot install anything at all, more of this lab survives than you might
expect: `partial`, `gradient`, `magnitude` and `unit` are arithmetic and
`math.sqrt`, and every one of the fifty-one predictions in `starter/answers.py`
is meant to be worked out on paper anyway. `requirements/README.md` states
exactly what you lose — the 360-direction sweep, the contour work and the
`numpy.gradient` comparison — rather than implying a workaround exists.

The autodiff libraries this lab talks about in its closing section — JAX,
PyTorch — are **not installed here and no output from them is reproduced
anywhere**. They are described from their documentation, and that description
is marked as a description.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-109-partial-derivatives-and-gradients
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                  this file
├── metadata.yml                               how the lab was actually run, and when
├── requirements/
│   ├── README.md                              why each package is here, its licence, and what NumPy is NOT doing
│   └── requirements.txt                       numpy==2.5.2, pytest==9.1.1
├── starter/                                   your work goes here
│   ├── 00_brief.md                            the eight exercises, in order
│   ├── conftest.py                            makes this directory's gradients.py the one its tests import
│   ├── surfaces.py                            the six surfaces, exact gradients, contours and tolerances — read, do not change
│   ├── gradients.py                           exercise 1 — eight functions to write
│   ├── answers.py                             exercises 2 to 8 — fifty-one predictions
│   └── test_starter.py                        your running score; unattempted work skips
├── examples/                                  the reference, to read after you have tried
│   ├── conftest.py                            the same import guard
│   ├── surfaces.py                            identical to the starter copy
│   ├── gradients.py                           the finished module
│   ├── 01_hold_everything_else_still.py       what a partial derivative is, by hand and numerically
│   ├── 02_the_gradient_vector.py              six surfaces, five points, numerical against exact
│   ├── 03_steepest_ascent.py                  360 bearings, and the one that wins
│   ├── 04_perpendicular_to_the_contour.py     exact contours, and the dot product going to zero
│   ├── 05_flat_ground_three_ways.py           constant gradients, outward gradients, and three zero ones
│   ├── 06_step_size_and_the_u_curve.py        the h^2 law, Day 108's U-curve, and numpy.gradient
│   ├── 07_one_partial_per_parameter.py        a three-parameter model, and the cost of doing this at scale
│   └── test_reference.py                      271 tests over real values and hand-derived gradients
├── tests/
│   └── run_tests.sh                           the bash harness: 98 checks, exits non-zero on any failure
├── expected-output/                           captured from real runs on 2026-08-17
│   ├── FIELDS.md                              what may legitimately differ on your machine
│   ├── 01-hold-everything-else-still.txt
│   ├── 02-the-gradient-vector.txt
│   ├── 03-steepest-ascent.txt
│   ├── 04-perpendicular-to-the-contour.txt
│   ├── 05-flat-ground-three-ways.txt
│   ├── 06-step-size-and-the-u-curve.txt
│   ├── 07-one-partial-per-parameter.txt
│   ├── reference-tests.txt
│   ├── starter-progress.txt
│   └── test-run.txt
├── troubleshooting.md
└── security.md
```

## How to run

Read `starter/00_brief.md` first. Then work, checking yourself as you go:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 205 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `206 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_hold_everything_else_still.py
../.venv/bin/python3 02_the_gradient_vector.py
../.venv/bin/python3 03_steepest_ascent.py
../.venv/bin/python3 04_perpendicular_to_the_contour.py
../.venv/bin/python3 05_flat_ground_three_ways.py
../.venv/bin/python3 06_step_size_and_the_u_curve.py
../.venv/bin/python3 07_one_partial_per_parameter.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `gradients.py` and
`surfaces.py` from beside themselves.

Then the full harness:

```bash
bash tests/run_tests.sh
echo "exit=$?"
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates a virtual environment inside the lab, so nothing here can affect the rest of your machine. `rm -rf .venv` is a complete undo. |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs numpy 2.5.2 and pytest 9.1.1. The one command that uses the network. |
| `.venv/bin/pytest starter -q` | Your running score. Unattempted exercises skip; wrong answers fail with both values printed. |
| `01_hold_everything_else_still.py` | Freezes one variable at a time on `x^2 + 3y^2`, shows the two slices as tables of values, derives both partials by hand, then measures them. Shows why the error is roundoff rather than method error on a quadratic, and closes on `xy`, whose x-slope is zero at `(1, 0)` on a surface that is anything but flat. |
| `02_the_gradient_vector.py` | Thirty numerical gradients against thirty hand-derived exact ones. Then the gradient's two readings — length and bearing — and the point that a gradient has one component per input, not one per dimension of the graph. Ends on three identical zero gradients. |
| `03_steepest_ascent.py` | Directional derivatives computed two ways that must agree; then 360 bearings measured directly, with the winner, the sampling gap, and the check that the winning rate over the magnitude equals the cosine of that gap to nine places. Ends on the steepest descent being exactly 180 degrees round. |
| `04_perpendicular_to_the_contour.py` | Three exactly parametrised contours, each checked to hold `f` constant before use; the chord-with-gradient dot product shrinking tenfold per tenfold smaller step; and then the exact tangent, which dots to exactly zero with no tolerance at all. |
| `05_flat_ground_three_ways.py` | A plane's gradient at five points, identical; then the section where that stops working, with the roundoff bound `eps|f|/2h` tracking the measured error over seven decades. Then the bowl's outward gradient and its zig-zag-causing misalignment, and the minimum, maximum and saddle that share one gradient. |
| `06_step_size_and_the_u_curve.py` | The cubic's error coming out as exactly `h^2`; Day 108's U-curve printed for both a central and a forward difference with the troughs at 1e-5 and 1e-8 against the predicted cube and square roots of machine epsilon; and `numpy.gradient`, including the `edge_order` default that gets an exact quadratic's corner wrong. |
| `07_one_partial_per_parameter.py` | A three-parameter loss worked by hand, its gradient of `(-17, -18, -8)`, one real step against it at eight step sizes, and the arithmetic of why nobody trains a model this way. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 271 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 98-check harness: versions, every script, both suites, sixty-seven individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
98 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `271 passed`, and an untouched
starter with `1 passed, 205 skipped`.

Four blocks worth recognising before you meet them. The two partial
derivatives, derived and then measured:

```
  df/dx:
    point nudged up      (2.00001, 1.00000)   f = 7.000040000100
    point nudged down    (1.99999, 1.00000)   f = 6.999960000100
    difference / (2h)    4.000000000026
    exact, by hand       4.000000000000
    error                2.620e-11
```

The sweep finding the gradient without being told about it:

```
   surface          point   best bearing   gradient bearing       gap     best rate    |gradient|
      bowl     (1.0, 1.0)          72.0d           71.5651d   0.4349d     6.3243731     6.3245553
```

Perpendicularity, as a number that shrinks rather than a number that is small:

```
       bowl      1e-02             -4.7195737669e-03                    
       bowl      1e-03             -4.7310204493e-04              9.9758
       bowl      1e-04             -4.7321678200e-05              9.9976
```

And the truncation error that is not merely bounded but exact:

```
           h       numerical df/dx             error               h^2   relative gap
       1e-01     13.01000000000001    0.010000000000    0.010000000000      1.044e-12
       1e-02     13.00009999999983    0.000100000000    0.000100000000      1.743e-09
```

`expected-output/FIELDS.md` records exactly which parts of the captured output
may legitimately differ on your machine — every roundoff digit, the platform
line, and your own progress score — and which parts may not. It also explains
the two numbers that look machine-independent and are not quite, and the
coincidence that makes five sampling gaps in `03-steepest-ascent.txt` come out
identical.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `98 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `271 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `206 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the seven scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 98 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, and confirms it is NumPy 2 or later.
2. **The seven reference scripts** — each must exit 0 and print that every one
   of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least 250 tests, so a collection error cannot pass as success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any
   of those skips into passes, which is a real hazard here because both
   directories contain modules called `gradients` and `surfaces`.
5. **Sixty-seven individual values** — that a partial evaluates `f` exactly twice
   and moves exactly one coordinate; the thirty gradients against exact ones,
   with the tolerance required to have tenfold headroom rather than scraping
   past; both directional-derivative routes agreeing; the winning bearing and
   its cosine identity; the contours holding `f` constant before they are used;
   the perpendicularity dot products and their tenfold shrink; the plane's
   constant gradient and the point where roundoff destroys it; the three zero
   gradients and the saddle that rises east and falls north; the `h^2` law and
   both troughs; `numpy.gradient`'s exact interior and its first-order corner;
   and the model's loss, gradient and evaluation count.
6. **A deliberate failure** — the harness re-runs itself with one expectation
   swapped for the belief that a bowl's gradient at `(1, 1)` points at 45
   degrees, straight away from the minimum, rather than at 71.5651. It asserts
   that the re-run exits non-zero and reports exactly one failure. A green suite
   proves nothing until you have watched it go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside `.venv`,
   no source file that opens a network connection, and a check on the check:
   that the `.venv` prune is genuinely doing its job, so that NumPy's own
   shipped bytecode can never be reported as mess this lab made.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of the
harness fails if they appear. It deliberately does not look inside `.venv`,
because the bytecode caches shipped with NumPy and pytest are theirs, not
yours — and `.venv` is never treated as a stray file, because the installation
instructions above are what told you to create it.

## Troubleshooting

See `troubleshooting.md`. It covers the wrong-directory import error, the
partial derivative that comes out exactly twice too big, the gradient that
mutated the point it was given, the `ValueError` from normalising a zero
vector, tolerances that fail far from the origin, the sweep that misses by half
a degree and is supposed to, the dot product that is not zero and is supposed
not to be, and `numpy.gradient` disagreeing with your gradient at the edge of a
grid — all found while building this lab rather than imagined for the document.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. Two points there are worth carrying away:
a numerical gradient evaluates whatever function you hand it, twice per input,
so handing it something with side effects runs those side effects `2n` times;
and an error tolerance copied from one context into another is a security-shaped
bug, because a check that always passes is not a check.

## Extension exercises

1. **Find your own trough.** The lab measures the best `h` as 1e-5 for a
   central difference and 1e-8 for a forward one. Sweep `h` in quarter-decade
   steps rather than whole decades and find the minimum more precisely. Then
   predict where it should move if you differentiate a function whose values
   are around a million instead of around ten, and check.
2. **A third-order difference.** The central difference uses `f(x+h)` and
   `f(x-h)`. Look up the five-point stencil, which also uses `f(x+2h)` and
   `f(x-2h)`, implement it, and measure how its error falls with `h`. Then work
   out where its trough sits and why it is not at the same place.
3. **Perpendicular in three dimensions.** The contour of a function of three
   inputs is a surface, not a curve. Take `f(x, y, z) = x^2 + y^2 + z^2`, whose
   level sets are spheres, parametrise one, and check that the gradient is
   perpendicular to two independent directions along it rather than one.
4. **Break the steepest-ascent check honestly.** Modify `sweep_directions` to
   use a forward difference instead of a central one and re-run the sweep at
   `h = 0.1`. The winning bearing will move. Work out whether it moved because
   the calculus changed or because the measurement got worse, and say how you
   could tell those apart from the output alone.
5. **A saddle in more directions.** The lab's saddle disagrees along two axes.
   Build a function of four inputs with a stationary point that goes up in one
   direction and down in three, and convince yourself that as the number of
   inputs grows, requiring *every* direction to agree gets rapidly less likely.
6. **Gradient checking, properly.** Write a function that takes a loss, a point
   and a hand-written analytic gradient, and reports the relative difference
   per component. Then deliberately introduce a sign error into
   `model_loss_gradient` and confirm your checker finds it and names which
   parameter is wrong.

## Navigation

- Previous day: Day 108 — Derivatives and Rates of Change
- Next day: Day 110 — The Chain Rule
- Week 16: Linear Algebra II and Calculus
- Section: Mathematics, Statistics and Data
