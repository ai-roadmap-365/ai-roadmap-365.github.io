# Day 108 lab — Watch the Slope Settle

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Derivatives: Rates of Change
- **Day number:** 108 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-108-derivatives-rates-of-change
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-108-derivatives-rates-of-change` when the site is running.
<!-- generated-links:end -->

## Purpose

This is the first calculus in the course, and it is built out of one idea you
already have: a rate of change is a difference divided by the interval it
happened over.

A car covers 144 metres in 6 seconds, so its average speed is 24 metres per
second. Ask instead how fast it was going *at* t = 3 and the arithmetic refuses
— rise zero over run zero is not a number. The derivative is the machine that
gets round that refusal: instead of asking for the rate over no interval, ask
for the rate over intervals that get smaller and smaller, and watch whether the
answers settle. In this lab you compute that sequence with real numbers and
watch it settle, which is the limit met as an observation rather than as a
definition.

Around that spine, four things the reading rarely gives you:

**Two rules, and the reason one is far better.** The forward difference is the
definition stopped early; the central difference straddles the point instead.
At the same step size on `e**x`, the central rule is over two hundred thousand
times more accurate here for one extra function call, and you measure that
rather than being told it.

**The measurement that contradicts the obvious intuition.** A smaller step
should give a better answer. It does, and then it stops: below about 1e-8 the
subtraction destroys the digits its two values had in common and the error
climbs again. You measure the error across 27 step sizes from 1e-1 down to
1e-14 and the curve comes out U-shaped, with the bottom nowhere near zero. At
h = 1e-300 the answer is exactly `0.0`, with no warning at all.

**What a zero derivative does and does not tell you.** It is zero at the bottom
of a valley, at the top of a hill, and on a flat step that is neither. The lab
asserts all three, then shows the second derivative separating the first two and
failing on the third — and asserts the failure, because `x**3` at 0 and `x**4`
at 0 give identical readings and are a step and a genuine minimum respectively.

**A case where the method confidently answers a question with no answer.** `|x|`
has no derivative at zero. The central difference returns `0.0` anyway. So does
ReLU's, at 0.5 — the average of two slopes that disagree, and neither of the
two values a framework could defensibly pick. That corner is inside every neural network you will
train, which is why it is here rather than in a footnote.

Every float comparison in the lab has a tolerance, and every tolerance is
derived in `examples/dataset.py` from the two error terms that actually govern a
difference quotient, with the arithmetic written out beside it. None was reached
by running a test and enlarging the number until it went green.

## Learning objectives

By the end you will be able to:

- Compute an average rate of change as rise over run, and say what it does and
  does not describe.
- Explain why the rate over an interval of zero width has no answer, and what
  the derivative does about it.
- Compute the sequence of secant slopes over shrinking intervals and recognise
  it settling on the derivative.
- Say what a tangent line is — the line the secants approach — and write its
  equation.
- Apply the constant, power, constant-multiple and sum rules, and know the
  derivatives of `e**x` and `ln(x)` as facts.
- Say what makes `e` special, and measure the slope of `b**x` at 0 to see it.
- Implement the forward, backward and central differences from scratch.
- Explain why the central rule's error falls like `h**2` where the forward
  rule's falls like `h`, and verify both by halving the step.
- Measure the error across a wide range of `h`, find the bottom of the U, and
  explain both sides of it.
- Choose a sensible `h` for float64, and say why 1e-12 is not a careful choice.
- Implement the second difference and use its sign to tell a minimum from a
  maximum.
- Say what a zero derivative does not tell you, and name the case the second
  derivative cannot decide either.
- Recognise where a derivative fails to exist, and detect it with values you
  have already computed.
- Say why derivatives are the object worth having when training a model.

## Prerequisites

- Day 70 — floating point. Half of this lab is a consequence of it.
- Day 102 — linear transformations, where ReLU first appeared. Today it is the
  corner rather than the transformation.
- Day 104 — NumPy arrays. Used lightly here: `np.gradient` as the library
  alternative, and `np.finfo` to check the epsilon.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 071–074 — running pytest and reading its output.
- **No calculus.** None is assumed and none is skipped over. If you have met
  derivatives before and disliked them, the order here is deliberately the
  reverse of the usual one: numbers first, notation second, limits described
  only after you have watched one happen.
- School arithmetic and the idea of a graph.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly rather
  than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The lab's largest allocation is a 27-element array.
Nothing here is a benchmark, nothing is timed, and the whole suite finishes in
well under a second. Roughly 60 MB of disk for the virtual environment, almost
all of it NumPy.

## Required software

- `python3` — 3.14.0 here.
- `numpy` 2.5.2 and `pytest` 9.1.1, installed into a lab-local virtual
  environment from `requirements/requirements.txt`.
- `bash` — 3.2.57 here, for the test harness.

## Free and open-source options

Both dependencies are free and open source and there is no paid tier of anything
in this lab. NumPy is distributed under the BSD 3-Clause licence and pytest
under the MIT licence. No account, no key, no signup, personally or
commercially.

If you cannot install anything at all, you can still do most of this lab, which
is unusual. Every one of the ten functions in `starter/derivatives.py` needs
`math` and nothing else, and so do the shrinking-interval sequence, the whole
U-shaped error measurement, the stationary-point classification and both corner
cases. What you lose is the two `np.gradient` comparisons, the epsilon
cross-check, and pytest — so you would read the numbers yourself rather than get
a score. `requirements/README.md` states that cost plainly.

Three other tools do this job and none of them is installed here, so no output
from them is reproduced anywhere in this lab or its lesson: SymPy differentiates
formulas symbolically, and JAX and PyTorch do automatic differentiation, which
is neither symbolic nor numerical. The lesson's Alternatives section describes
all three from their documentation and says so.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-108-derivatives-rates-of-change
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
│   ├── README.md                              why each package is here, and its licence
│   └── requirements.txt                       numpy==2.5.2, pytest==9.1.1
├── starter/                                   your work goes here
│   ├── 00_brief.md                            the seven exercises, in order
│   ├── conftest.py                            makes this directory's derivatives.py the one its tests import
│   ├── dataset.py                             the functions, step sizes and derived tolerances — read it, do not change it
│   ├── derivatives.py                         exercise 1 — ten functions to write
│   ├── answers.py                             exercises 2 to 7 — forty-two predictions
│   └── test_starter.py                        your running score; unattempted work skips
├── examples/                                  the reference, to read after you have tried
│   ├── conftest.py                            the same import guard
│   ├── dataset.py                             the data, and every tolerance with its derivation
│   ├── derivatives.py                         the finished module
│   ├── 01_average_rate_of_change.py           rise over run, and the question 0/0 refuses
│   ├── 02_shrinking_intervals.py              the sequence settling; secants approaching a tangent
│   ├── 03_rules_checked_numerically.py        six rules, each checked against a measurement
│   ├── 04_forward_and_central.py              two rules, h against h squared, and np.gradient
│   ├── 05_the_u_shaped_error.py               27 step sizes, and why smaller stops helping
│   ├── 06_zero_derivative_and_curvature.py    flat points, and telling them apart
│   ├── 07_where_the_derivative_fails.py       corners, ReLU, and confident nonsense
│   └── test_reference.py                      178 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                           the bash harness: 97 checks, exits non-zero on any failure
├── expected-output/                           captured from real runs on 2026-08-17
│   ├── FIELDS.md                              what may legitimately differ on your machine
│   ├── 01-average-rate-of-change.txt
│   ├── 02-shrinking-intervals.txt
│   ├── 03-rules-checked-numerically.txt
│   ├── 04-forward-and-central.txt
│   ├── 05-the-u-shaped-error.txt
│   ├── 06-zero-derivative-and-curvature.txt
│   ├── 07-where-the-derivative-fails.txt
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

On an untouched checkout that prints `1 passed, 99 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `100 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_average_rate_of_change.py
../.venv/bin/python3 02_shrinking_intervals.py
../.venv/bin/python3 03_rules_checked_numerically.py
../.venv/bin/python3 04_forward_and_central.py
../.venv/bin/python3 05_the_u_shaped_error.py
../.venv/bin/python3 06_zero_derivative_and_curvature.py
../.venv/bin/python3 07_where_the_derivative_fails.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `derivatives.py` and
`dataset.py` from beside themselves.

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
| `01_average_rate_of_change.py` | A car timed once a second. Rise over run over the whole trip, then over each second separately, then the refusal when the interval has no width — and the observation that the settled answer at t = 3 must sit between the averages either side of it. |
| `02_shrinking_intervals.py` | The same question over intervals of 1, 0.5, 0.1, 0.01, 0.001 and 0.0001, then the algebra showing the slope over [3, 3+h] is exactly 6 + h, then the floating-point version showing it is not quite, then secants pivoting into the tangent y = 6x − 9. |
| `03_rules_checked_numerically.py` | The three notations defined at first use, then six rules stated and each checked against a measurement, then the slope of `b**x` at 0 for five bases — 0.693, 0.916, 1.000, 1.099, 2.303 — which is what makes `e` special, shown rather than asserted. |
| `04_forward_and_central.py` | Forward, backward and central on a parabola where the first two are exactly 6 ± h and the third is exactly 6; then on `e**x` where the error columns fall by 10 and by 100 per decade; then the Taylor expansion that explains why, checked against the measurement to within one percent three times; then `np.gradient`, bit-for-bit identical with a scalar spacing and not with a coordinate array. |
| `05_the_u_shaped_error.py` | The centrepiece. `h = 1e-300` returning exactly 0.0, the two error terms pulling in opposite directions, then 27 step sizes with a sideways log-log bar chart, then the bottom of the U located and compared against the balance prediction, then the real jitter around the minimum. |
| `06_zero_derivative_and_curvature.py` | Four flat points with four indistinguishable slopes, the neighbourhood test your eye does, the second difference derived and measured at 2, 6, −6 and 0, the classification including `undecided`, and the sign of the slope pointing downhill towards a minimum from five different starting points. |
| `07_where_the_derivative_fails.py` | `|x|` at zero: forward +1, backward −1, central 0.0, and no `h` small enough to reveal a limit that is not there. The second difference at 2/h, diverging. Then ReLU, the same corner with one arm flattened, and the one-extra-call check that catches both. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 178 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 97-check harness: versions, every script, both suites, sixty-seven individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
97 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `178 passed`, and an untouched
starter with `1 passed, 99 skipped`.

Four blocks worth recognising before you meet them. The sequence settling:

```
     width h        secant slope     exactly 6 + h?   distance from 6
     1.0000         7.000000000000   True             1.0000
     0.1000         6.100000000000   True             0.1000
     0.0100         6.010000000000   True             0.0100
     0.0010         6.001000000000   True             0.0010
```

The two rules at the same step size, on `e**x` at x = 1:

```
     h            forward error    central error    central is better by
     1e-03        1.359594e-03     4.530467e-07           3001x
     1e-04        1.359186e-04     4.530566e-09          30000x
     1e-05        1.359150e-05     5.858691e-11         231989x
```

The measurement that contradicts the intuition:

```
     forward_difference(exp, 1.0, 1e-300)  ->  0.0
     the right answer is                       2.718281828459045
```

And the corner:

```
     forward   1.0     the slope on the right
     backward  0.0     the slope on the left
     central   0.5     the average of two slopes that disagree
```

`expected-output/FIELDS.md` records exactly which parts of the captured output
may legitimately differ on your machine — elapsed times, the platform line, your
own progress score, and, most interestingly, the exact position of the bottom of
the U — and which parts may not. It also tabulates every tolerance in the lab
against the error bound it was derived from.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `97 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `178 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `100 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the seven scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 97 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, confirms it is NumPy 2 or later, and
   confirms this interpreter's floats are IEEE-754 doubles with a 53-bit
   significand, because the whole U-shaped curve is a consequence of that width.
2. **The seven reference scripts** — each must exit 0 and print that every one
   of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least 150 tests, so a collection error cannot pass as success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any of
   those skips into passes, which is a real hazard here because both directories
   contain modules called `derivatives` and `dataset`.
5. **Sixty-seven individual values** — the car's three average speeds and the
   `ZeroDivisionError`, the four-term settling sequence from both sides, the
   tangent's slope and intercept, all eight rule values, the log of 2 as the
   slope of `2**x` at zero, forward and backward at 6 ± h, the halving and
   quartering of the two error terms, the whole shape of the U with its interior
   minimum and both bad ends, the balance predictions, the `0.0` at h = 1e-300,
   four stationary points and four curvatures, six classifications including
   both `undecided` cases, the five downhill directions, and every corner value
   for `|x|` and ReLU.
6. **A deliberate failure** — the harness re-runs itself with one expectation
   swapped for the belief that ReLU's central difference at zero is 1.0, which
   is what you would get if you assumed a corner simply takes its right-hand
   slope. It asserts that the re-run exits non-zero and reports exactly one
   failure. A green suite proves nothing until you have watched it go red.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside `.venv`,
   and no source file that opens a network connection.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of the
harness fails if they appear. It deliberately does not look inside `.venv`,
because the bytecode caches shipped with NumPy and pytest are theirs, not yours
— and `.venv` itself is the documented setup, not litter, so nothing here treats
it as a stray file.

## Troubleshooting

See `troubleshooting.md`. It covers both wrong-directory import errors, the
central difference divided by `h` instead of `2h` and its second-derivative
twin, a U whose bottom sits somewhere other than the captured one, the huge
error you get from being too careful with `h`, a numerical derivative
disagreeing with a framework at exactly one point, the `undecided` verdict that
is correct, the import collision the two `conftest.py` files prevent, and the
`__pycache__` search that must prune `.venv`. All of them were hit while
building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. Three points there are worth carrying
away: a numerical method that always returns a number will return one where no
answer exists, and a failure mode that looks like a plausible value is a failure
mode you cannot see; catastrophic cancellation is a real bug class that shows up
in variances, timestamps and running balances, not only in derivatives; and a
tolerance widened until a test passes is a tolerance chosen by whatever bug
happened to exist at the time.

## Extension exercises

1. **Find your own crossover.** The lab measures the U on `e**x` at x = 1. Do it
   on `sin(x)` at x = 1 and on `x**5` at x = 2, and see whether the bottom moves.
   Predict the direction first: the rounding term scales with `|f(x)|` and the
   truncation term with `|f'''(x)|`, so a function that is large but gently
   curved should behave differently from one that is small and sharply curved.
2. **A better rule, for free.** The five-point rule
   `(-f(x+2h) + 8f(x+h) - 8f(x-h) + f(x-2h)) / (12h)` has an error proportional
   to `h**4`. Implement it, measure its U, and find its best `h`. Then decide
   whether the two extra function calls were worth it, and at what point they
   stop being.
3. **Richardson extrapolation.** Compute the central difference at `h` and at
   `h/2`, then combine them as `(4*D(h/2) - D(h)) / 3`. That cancels the `h**2`
   error term algebraically. Measure how much better it is, and find where its
   own U bottoms out.
4. **The derivative of a derivative, the long way.** Instead of the collapsed
   second-difference formula, compute `central_difference` of a function that
   itself computes `central_difference`. Compare the two on accuracy and on the
   number of calls to `f`, and work out why the collapsed version wins.
5. **Complex-step differentiation.** For a function that accepts complex
   arguments, `f(x + ih).imag / h` estimates `f'(x)` with **no subtraction at
   all** — so it has no cancellation, and `h = 1e-200` works perfectly. Try it on
   `cmath.exp` and watch the U disappear entirely. Then work out why it cannot be
   used on a function containing `abs` or a comparison.
6. **Make the corner bite.** Write a loop that steps downhill using the sign of
   the central difference, and run it on `|x| - 0.5*x` starting from x = 3. Watch
   what it does when it reaches zero, and decide whether the behaviour you see is
   convergence or a stall.

## Navigation

- Previous day: Day 107 — Norms, Distances, and Similarity Measures
- Next day: Day 109 — Partial Derivatives and Gradients
- Week 16: Linear Algebra II and Calculus
- Section: Mathematics, Statistics and Data
