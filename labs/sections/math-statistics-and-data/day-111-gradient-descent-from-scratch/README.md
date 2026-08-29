# Day 111 lab — Descent by Hand

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Gradient Descent from Scratch
- **Day number:** 111 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-111-gradient-descent-from-scratch
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-111-gradient-descent-from-scratch` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 109 gave you the gradient — the direction of steepest ascent. Day 110
gave you the chain rule — how to compute it through a composition. Today
you take the step, and discover that the entire loop that trains every
model in this course is one line:

```
x <- x - eta * grad(x)
```

plus a great deal of care about `eta`, the learning rate.

The lab opens with a failure, because that is the fastest way to feel why
the care matters. Run gradient descent on the simplest convex function
there is, `f(x) = 0.5 * x**2`, with a learning rate only slightly above its
own divergence boundary, and the loss climbs on every single step —
smoothly, plausibly, for thousands of iterations — until it overflows to
`inf` and then `nan` on the very next step. Nothing is wrong with the
function, the gradient, or the code. The step size alone turned a solved
problem into a divergent one.

The nine exercises that follow build outward from that failure into the
whole shape of the day:

**The three regimes, with exact boundaries.** For `f(x) = 0.5*a*x**2` the
update is exact algebra, `x <- x*(1 - eta*a)`, so after `n` steps
`x_n = x_0 * (1 - eta*a)**n`. With `a = 5` (so `1/a = 0.2`, `2/a = 0.4`),
four learning rates land in four different outcomes — monotone decrease,
an exact landing on zero in one step, alternating-but-converging, and
divergence — and the per-step contraction ratio measured from a real run
equals `|1 - eta*a|` exactly.

**Conditioning.** On `f(x, y) = 0.5*(x**2 + kappa*y**2)`, whose Hessian has
eigenvalues 1 and `kappa` (Day 106's ratio of eigenvalues, put to work),
the optimal fixed learning rate is `2/(1+kappa)`. An isotropic bowl
(`kappa=1`) solves in exactly one step at that rate; an ill-conditioned
one (`kappa=100`) needs more than ten times the steps a well-conditioned
one does, with no free parameter left to compensate. Momentum — a running
average of the gradient substituted for the raw gradient — needs
noticeably fewer steps than plain descent at the *same* learning rate on
the same bowl, and the lab measures the actual speedup rather than
asserting one.

**Gradient checking**, Day 108's central difference put to work catching
bugs: a deliberately broken analytic gradient, with the sign flipped on
one component, is flagged on exactly that component and no other.

**Non-convexity.** Two starting points on `f(x) = (x**2-1)**2`, one on
each side of the local maximum at `x=0`, converge to two different
minima. Which minimum you find is decided entirely by where you started.

**The stopping-criterion trap.** On a very shallow, genuinely convex bowl,
far from its minimum, one gradient-descent step leaves the loss barely
changed — below a plausible "we must have converged" tolerance — while
the gradient itself remains ten times its own tolerance above zero. "The
loss stopped changing" is not "we converged", and the lab catches the
naive rule firing early rather than merely warning about it.

Every float comparison in this lab has a stated, derived tolerance, kept
in `examples/dataset.py` alongside the arithmetic that justifies it.

## Learning objectives

By the end you will be able to:

- Implement `numeric_gradient` by central differences and `gradient_descent`
  as a loop that returns its whole path, not just the final answer.
- State the three regimes of 1-D gradient descent — monotone, exact,
  oscillating-but-converging — and the exact learning-rate boundaries
  `1/a` and `2/a` that separate them from each other and from divergence.
- Predict and measure the per-step contraction ratio `|1 - eta*a|`.
- Explain why an ill-conditioned Hessian (a large ratio between its
  eigenvalues) forces slow convergence at any single fixed learning rate,
  and connect that directly to Day 106's eigenvalues.
- Implement momentum as an exponentially weighted running average of the
  gradient, and explain it as averaging away an oscillating component
  rather than as an unexplained trick.
- Implement a gradient check from a central difference and use it to
  localise a bug to a specific component of an analytic gradient.
- Explain why initialisation decides the outcome on a non-convex function.
- State two common gradient-descent stopping criteria (`||grad|| < tol`,
  `|delta f| < tol`, a maximum iteration count) and describe a concrete
  case where the loss-based one fails while the gradient-based one does
  not.
- Explain, from a real captured run, what a diverging training run looks
  like numerically — a smoothly increasing loss, then overflow to `inf`,
  then `nan` — and why that is the reason production training loops check
  their own loss for finiteness.

## Prerequisites

- Day 108 — derivatives, the central difference, and the U-shaped error
  curve. The step size used throughout this lab, `h = 1e-6`, sits inside
  the band Day 108 measured.
- Day 109 — partial derivatives and the gradient: the direction this lab
  spends every exercise walking against.
- Day 110 — the chain rule and, more specifically, the sentence "backward
  pass computes gradients, gradient descent uses them" that separates the
  two days cleanly.
- Day 106 — eigenvalues and eigenvectors. The condition number in
  exercises 5 and 6 is literally the ratio of two eigenvalues of a
  Hessian, restated in code.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 71-74 — running `pytest` and reading its output.
- Comfort with a Python function that takes another function as an
  argument (`grad_fn`, `value_fn`); nothing more advanced than that is
  needed.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly
  rather than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest computation in this lab is a
gradient-descent run of a few thousand steps on a two-number point;
nothing here is a benchmark, nothing is timed, and the whole harness
finishes in a fraction of a second. Roughly 60 MB of disk for the virtual
environment, almost all of it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of
anything in this lab. NumPy is distributed under the BSD 3-Clause licence
and pytest under the MIT licence. No account, no key, no signup,
personally or commercially. `requirements/README.md` has the full
breakdown, including exactly how little you lose if you cannot install
anything at all.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-111-gradient-descent-from-scratch
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import numpy; print(numpy.__version__)"
```

Expect `2.5.2`. That is the only time this lab needs the network.

## File structure

```
.
├── README.md                                  this file
├── metadata.yml                                how the lab was actually run, and when
├── requirements/
│   ├── README.md                               why each package is here, its licence, and the no-install path
│   └── requirements.txt                        numpy==2.5.2, pytest==9.1.1
├── starter/                                    your work goes here
│   ├── 00_brief.md                              the nine exercises, in order
│   ├── conftest.py                              makes this directory's modules the ones its tests import
│   ├── dataset.py                               the functions, tolerances and constants -- read it, do not change it
│   ├── descent.py                               nine functions to write
│   └── test_starter.py                          your running score; unattempted work skips
├── examples/                                    the reference, to read after you have tried
│   ├── conftest.py                              the same import guard
│   ├── dataset.py                               the finished data module
│   ├── descent.py                               the finished nine functions
│   ├── 01_the_hook.py                           the opening failure: overflow to inf, then nan
│   ├── 02_regimes_and_contraction.py            exercises 1, 3 and 4
│   ├── 03_ill_conditioning_and_momentum.py      exercises 5 and 6
│   ├── 04_checking_landscapes_and_traps.py      exercises 7, 8 and 9
│   └── test_reference.py                        24 tests over real values and real behaviour
├── tests/
│   └── run_tests.sh                             the bash harness: 50 checks, exits non-zero on any failure
├── expected-output/                             captured from real runs on 2026-08-17
│   ├── FIELDS.md                                what may legitimately differ on your machine
│   ├── 01-the-hook.txt
│   ├── 02-regimes-and-contraction.txt
│   ├── 03-ill-conditioning-and-momentum.txt
│   ├── 04-checking-landscapes-and-traps.txt
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

On an untouched checkout that prints `1 passed, 20 skipped`. A skip means
"not attempted"; a failure means "attempted and wrong", and prints both
your answer and the real one. When every test passes, you are finished.

Afterwards, read the reference — each script prints its working and
asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_the_hook.py
../.venv/bin/python3 02_regimes_and_contraction.py
../.venv/bin/python3 03_ill_conditioning_and_momentum.py
../.venv/bin/python3 04_checking_landscapes_and_traps.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `dataset.py` and
`descent.py` from beside themselves.

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
| `01_the_hook.py` | The opening failure: a learning rate only slightly too large makes the loss climb every step until the run overflows. |
| `02_regimes_and_contraction.py` | `numeric_gradient` checked against two analytic gradients; the four learning rates classified into their regimes; the measured contraction ratio checked against `|1 - eta*a|`. |
| `03_ill_conditioning_and_momentum.py` | Steps-to-tolerance on the ill-conditioned bowl for four condition numbers; momentum against plain descent at the same learning rate. |
| `04_checking_landscapes_and_traps.py` | Gradient checking catching a sign-error bug; two initialisations reaching two different minima; the stopping-criterion trap on a shallow bowl. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 24 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 50-check harness: versions, every script, both suites, thirty-odd individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
50 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `24 passed`, and an untouched
starter with `1 passed, 20 skipped`.

Two blocks worth recognising before you meet them. The four regimes on
`a = 5`:

```
  eta=0.10  monotone   (0 < eta < 1/a)  first 4 steps: [1.0, 0.5, 0.25, 0.125]  ...  classified: monotone
  eta=0.20  exact      (eta = 1/a)  first 4 steps: [1.0, 0.0, 0.0, 0.0]  ...  classified: exact
  eta=0.35  oscillating(1/a < eta < 2/a)  first 4 steps: [1.0, -0.75, 0.5625, -0.4219]  ...  classified: oscillating
  eta=0.45  divergent  (eta > 2/a)  first 4 steps: [1.0, -1.25, 1.5625, -1.9531]  ...  classified: divergent
```

And the conditioning result that the day is built to demonstrate:

```
kappa |     eta = 2/(1+kappa)  | steps
    1 |               1.000000 | 1
    5 |               0.333333 | 27
   20 |               0.095238 | 122
  100 |               0.019802 | 691
```

The isotropic bowl (`kappa=1`) solves in exactly one step at its optimal
learning rate; the ill-conditioned one (`kappa=100`) needs 691 — comfortably
more than ten times as many. `expected-output/FIELDS.md` records exactly
which figures may legitimately differ on your machine and which may not,
and tabulates every tolerance against the error bound it was derived from.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `50 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `24 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `1 passed, 20 skipped`
   on an untouched checkout, and every test passing once you have finished.
4. Each of the four scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 50 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, confirms it is NumPy 2 or later, and
   confirms this interpreter's floats are IEEE-754 doubles with a 53-bit
   significand, since the exact-algebra checks in exercises 2-4 depend on
   that width.
2. **The four reference scripts** — each must exit 0 and print that every
   one of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and
   have collected at least 20 tests, so a collection error cannot pass as
   success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn
   any of those skips into passes, which is a real hazard here because
   both directories contain modules called `dataset` and `descent`.
5. **Roughly thirty individual values** — the exact regime boundaries, the
   classification of all four learning rates, the contraction ratios, the
   non-decreasing step counts across four condition numbers with the
   order-of-magnitude check and the one-step isotropic case, the momentum
   speedup, the gradient-check flags on both the correct and buggy
   gradients, both converged minima, the plateau's gradient-versus-loss
   disagreement, and the hook's overflow behaviour.
6. **A deliberate failure** — the harness re-runs itself with one
   expectation swapped for the belief that a flat loss always means
   convergence, and asserts that the re-run exits non-zero and reports
   exactly one failure. A green suite proves nothing until you have
   watched it go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside
   `.venv`, and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear,
section 7 would then report those as litter — failing you for following
the instructions in this file. Clearing them at the start makes the final
check measure what *this* run left behind.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of
the harness fails if they appear. It deliberately does not look inside
`.venv`, because the bytecode caches shipped with NumPy and pytest are
theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the
starter tests that keep skipping because a `return None` survived below
your code, the classification and contraction-ratio edge cases at the
exact-landing boundary, the momentum update-order mistake, the gradient
check that flags every component instead of one, the two-minima run that
collapses to one basin, the `__pycache__` search that must prune `.venv`,
and the import collision the two `conftest.py` files prevent. All of them
were hit while building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no
files, opens no connection after the one-time install, needs no
credentials and no `sudo`, and all the data is invented. Three points
there are worth carrying away: a learning rate only slightly too large
produces a run that looks like it is training right up until it overflows;
a silently wrong gradient is worse than a crash, and a component-by-
component check is the only real defence; and a stopping rule that only
watches the loss can declare victory on a genuinely convex problem that
has not been solved.

## Extension exercises

1. **Find your own boundary.** The opening hook uses `a = 1` and
   `eta = 2.2`. Pick a different `a` and search for the smallest `eta`
   (to two decimal places) at which the run still diverges within 5,000
   steps, and report how the number of steps to overflow changes as `eta`
   moves away from the boundary `2/a`.
2. **A second momentum experiment.** The lab compares momentum against
   plain descent at the *same* learning rate on `kappa=20`. Sweep `beta`
   over `{0.1, 0.3, 0.5, 0.7, 0.9}` at that same learning rate, plot (or
   just tabulate) steps-to-tolerance against `beta`, and describe the
   shape of the curve in one paragraph.
3. **A third stopping criterion.** Implement a maximum-iteration-count
   check as a third option alongside `||grad|| < tol` and
   `|delta f| < tol`, and construct a case (you may reuse or adapt the
   plateau) where the max-iteration check is the only one of the three
   that behaves sensibly.
4. **Nesterov's variant.** Look up Nesterov accelerated gradient — the
   look-ahead variant of momentum, where the gradient is evaluated at
   `x - lr*beta*v` rather than at `x` — and implement it as a fourth
   function. Compare its step count against plain momentum's on the
   `kappa=20` bowl and report which wins.
5. **Break the gradient checker.** Write a gradient with an error that
   is *not* a sign flip — for example, a coefficient that is off by 10% —
   and confirm your `gradient_check` still flags it at `CHECK_TOL = 1e-4`.
   Then find the largest error (as a fraction of the true value) that
   `gradient_check` fails to catch at that tolerance, and explain why
   tightening the tolerance is not free.

## Navigation

- Previous day: Day 110 — The Chain Rule
- Next day: Day 112 — Visualizing Optimization
- Week 16: Linear Algebra II and Calculus
- Section: Mathematics, Statistics and Data
