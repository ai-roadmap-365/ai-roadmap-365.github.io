# Day 110 lab — Rates Multiply

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Chain Rule
- **Day number:** 110 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-110-the-chain-rule
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-110-the-chain-rule` when the site is running.
<!-- generated-links:end -->

## Purpose

Two days ago a derivative was a rate of change. Yesterday a gradient was a
collection of them. Today those rates get connected end to end, and the rule
that connects them is the reason a network with a hundred layers can be
trained at all.

The whole idea fits in one sentence with no calculus in it: **if gear A turns
twice for every turn of gear B, and B turns three times for every turn of C,
then A turns six times per turn of C.** The rates multiplied. That is the chain
rule, and everything after it is bookkeeping.

The lab builds outwards from that sentence in six moves, and five of them are
measurements rather than statements.

**The rule, checked against something that has never heard of it.** Six
composed functions — a square of a line, a sine of a square, a Gaussian bump, a
logarithm, the sigmoid and a tanh — differentiated by the chain rule and then
measured with Day 108's central difference. The worst disagreement across all
six was 8.969e-10, which is the measuring instrument's own error and not a
disagreement about the rule.

**Depth costs nothing structural.** Two functions, then three, then five. The
five-stage chain's derivative is `2 × 1 × 10 × 0.1 × 0.2 = 0.4`, and the same
chain collapses by hand to `ln(2x + 3)`, whose derivative at `x = 1` is `2/5`.
Three independent routes to one number.

**The part that must be slowed down for: when paths meet, contributions ADD.**
Build a graph where `x` reaches the output twice, once through `u = x²` and
once through `v = 3x`. The two path products are 24 and 12. The lab asks a
central difference which of 24, 12, 288 and 36 is right, and only 36 survives.
Getting this wrong is the instructive failure of the day, and the lab is built
to catch it in three separate places.

**A reverse-mode autodiff engine, written from scratch and checked
numerically.** About seventy lines: a `Value` that holds a number and a
gradient, remembers its children, and knows how to hand its gradient back to
them; `+`, `×` and `tanh`; and a `backward()` that topologically sorts the
graph and walks it in reverse. Every gradient it produces is checked against a
central difference. This is the core of `torch.autograd` with the engineering
removed, and the single character that makes it correct is the `+=` in each
backward step.

**A two-layer network backpropagated by hand.** Two inputs, two tanh hidden
units, one linear output, a squared-error loss, nine parameters, sixteen
gradients. The parameters were chosen so that **every number in both passes is
exact in float64** — one hidden unit sits at a pre-activation of 0 where tanh
is 0 and its slope is 1, the other at exactly half the natural logarithm of 3
where tanh is exactly 0.5 and its slope is exactly 0.75. You can check the
entire backward pass with a pen. The hand computation and the engine then agree
*bit for bit*, and a central difference agrees with both to about four parts in
a billion.

**Products that collapse and products that blow up.** Fifty factors of 0.9 give
5.15e-3; fifty of 1.1 give 117. Asserted as orders of magnitude, because the
scale is the lesson and the digits are float64 rounding.

And then one measurement that contradicts the story the previous paragraph just
told, which is the best thing in the lab. See "Expected output" below.

Every float comparison here has a stated tolerance and every tolerance is
derived in `examples/dataset.py` from the error terms that actually govern that
comparison, with the arithmetic written out. Two analytic routes are compared
at 1e-12; an analytic route against a measured one at 1e-6. That million-fold
gap is not sloppiness in the second number — it is the honest size of a central
difference's own error, and a lab that used one tolerance for both comparisons
would be lying about one of them.

## Learning objectives

By the end you will be able to:

- State the chain rule as a sentence about rates rather than as a formula, and
  explain the gear train that makes it obvious.
- Compose two functions, evaluate the composition, and say which one runs first.
- Apply the one-variable chain rule, and explain why the outer derivative is
  evaluated at the inner value rather than at `x`.
- Verify a chain-rule result against a central difference, and say why that
  check is meaningful rather than circular.
- Read `dy/dx = dy/du · du/dx`, use the "cancelling" reading as a mnemonic, and
  say precisely why it is not a proof and where it stops working.
- Differentiate a chain of any depth by multiplying its local rates, each
  evaluated at the value that arrives at its stage.
- Explain what a backward pass is carrying at each step, in terms of partial
  products.
- State the multivariable chain rule as a sum over paths, and explain why the
  contributions add rather than multiply or compete.
- Recognise a computation graph, identify every path from an input to the
  output, and compute a gradient as a sum of path products.
- Implement a reverse-mode autodiff engine with `+`, `×` and one non-linearity,
  including a correct topological sort and gradient accumulation.
- Explain why gradients must be accumulated with `+=`, and describe the class
  of bug that assignment produces.
- Implement forward mode with dual numbers, and count the passes each mode
  needs.
- Explain, in terms of cost rather than mechanics, why reverse mode wins when
  there are many parameters and one loss — and what it pays in memory.
- Backpropagate a small network by hand and check every gradient two other ways.
- Demonstrate a vanishing and an exploding product, and state the result as an
  order of magnitude rather than a value.
- Explain why "tanh saturates, therefore gradients vanish" is a claim that has
  to be measured rather than assumed.

## Prerequisites

- Day 108 — derivatives, the central difference, and the U-shaped error curve.
  The step size used here, `h = 1e-5`, sits inside the band Day 108 measured.
- Day 109 — partial derivatives and the gradient. Today's sum over paths is
  what happens when those partials are chained.
- Day 70 — floating point. The vanishing-gradient section is a consequence of
  it, and one of the day's two surprises is pure IEEE-754.
- Day 43 — `python3 -m venv` and installing a package with `pip`.
- Days 71–74 — running pytest and reading its output.
- **No calculus beyond Days 108 and 109.** Nothing is assumed and nothing is
  skipped over.
- Comfort with writing a Python class, including `__init__` and one dunder
  method. Exercise 2 is the first time the course asks you to write operator
  overloads, and the skeleton writes the first one out in full.

## Supported operating systems

- macOS — run and captured here (macOS 26.5.2, Apple Silicon, arm64).
- Linux — the same commands apply unchanged. Not run here.
- Windows — use the Windows Subsystem for Linux and follow the Linux
  instructions, or Git Bash with `.venv\Scripts\python.exe` in place of
  `.venv/bin/python3`. Not run here; `troubleshooting.md` says so plainly
  rather than implying a test that did not happen.

## Hardware requirements

Anything that runs Python. The largest structure this lab builds is a
computation graph of about twenty thousand scalar nodes, which exists for a
fraction of a second inside one test. Nothing here is a benchmark, nothing is
timed, and the whole suite finishes in well under a second. Roughly 60 MB of
disk for the virtual environment, almost all of it NumPy.

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

If you cannot install anything at all you can still do nearly all of this lab.
The autodiff engine — the most valuable artifact here — needs `math` and
nothing else, and so do all fourteen functions in `starter/chainrule.py`, the
whole network, the hand-worked backward pass and every product experiment.
NumPy is used for exactly one thing: reading float64's machine epsilon from
`numpy.finfo` rather than trusting a literal. `requirements/README.md` states
that cost plainly and shows the one-line standard-library substitution.

Four other tools do this job and **none of them is installed here, so no output
from any of them is reproduced anywhere in this lab or its lesson**: PyTorch's
`autograd`, JAX's `grad` and TensorFlow's `GradientTape` all do reverse-mode
automatic differentiation, and SymPy differentiates formulas symbolically,
which is a different thing again. The lesson's Alternatives section describes
all four from their documentation and says so.

## Installation

From the repository root:

```bash
cd labs/sections/math-statistics-and-data/day-110-the-chain-rule
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
│   ├── README.md                              why each package is here, its licence, and the no-install path
│   └── requirements.txt                       numpy==2.5.2, pytest==9.1.1
├── starter/                                   your work goes here
│   ├── 00_brief.md                            the nine exercises, in order
│   ├── conftest.py                            makes this directory's modules the ones its tests import
│   ├── dataset.py                             the functions, chains, network and derived tolerances — read it, do not change it
│   ├── chainrule.py                           exercise 1 — fourteen functions to write
│   ├── autodiff.py                            exercises 2 and 3 — the Value engine, dual numbers, and the pass counters
│   ├── network.py                             exercise 4 — the backward pass by hand, by engine, and numerically
│   ├── answers.py                             exercises 5 to 9 — forty-two predictions
│   └── test_starter.py                        your running score; unattempted work skips
├── examples/                                  the reference, to read after you have tried
│   ├── conftest.py                            the same import guard
│   ├── dataset.py                             the data, and every tolerance with its derivation
│   ├── chainrule.py                           the finished plumbing
│   ├── autodiff.py                            the finished engine, reverse mode and forward mode
│   ├── network.py                             the finished two-layer network
│   ├── 01_gears_and_rates.py                  rates multiply, with no calculus in sight
│   ├── 02_composition_and_the_chain_rule.py   six compositions, each checked against a measurement
│   ├── 03_deeper_chains.py                    two, three and five functions; what a backward pass carries
│   ├── 04_two_paths_add.py                    the sum over paths, and the measurement that settles it
│   ├── 05_the_value_engine.py                 the engine exercised and checked
│   ├── 06_backprop_by_hand.py                 sixteen gradients, three independent ways
│   ├── 07_vanishing_and_exploding.py          collapse, blow-up, cost, and the finding that corrects them
│   └── test_reference.py                      235 tests over real values and real exceptions
├── tests/
│   └── run_tests.sh                           the bash harness: 120 checks, exits non-zero on any failure
├── expected-output/                           captured from real runs on 2026-08-17
│   ├── FIELDS.md                              what may legitimately differ on your machine
│   ├── 01-gears-and-rates.txt
│   ├── 02-composition-and-the-chain-rule.txt
│   ├── 03-deeper-chains.txt
│   ├── 04-two-paths-add.txt
│   ├── 05-the-value-engine.txt
│   ├── 06-backprop-by-hand.txt
│   ├── 07-vanishing-and-exploding.txt
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

On an untouched checkout that prints `2 passed, 163 skipped`. A skip means "not
attempted"; a failure means "attempted and wrong", and prints both your answer
and the real one. When it prints `165 passed`, you are finished.

Afterwards, read the reference — each script prints its working and asserts
every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_gears_and_rates.py
../.venv/bin/python3 02_composition_and_the_chain_rule.py
../.venv/bin/python3 03_deeper_chains.py
../.venv/bin/python3 04_two_paths_add.py
../.venv/bin/python3 05_the_value_engine.py
../.venv/bin/python3 06_backprop_by_hand.py
../.venv/bin/python3 07_vanishing_and_exploding.py
cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
```

Run them from inside `examples/`, because they import `chainrule.py`,
`autodiff.py`, `network.py` and `dataset.py` from beside themselves.

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
| `01_gears_and_rates.py` | Two gears, then a four-stage train, then the same arithmetic with money — and then the notation, with an explicit warning that the "du cancels" reading is a mnemonic and not a proof. |
| `02_composition_and_the_chain_rule.py` | Composition with numbers before any derivative appears; the rate question; the mistake of evaluating the outer derivative at `x` shown as a number rather than a warning; then six compositions each checked against a central difference. Closes on the sigmoid's slope at zero being 0.25 and on why that matters fifty layers later. |
| `03_deeper_chains.py` | Depth two, three and five side by side; the forward pass showing which value arrives where; the product, the collapsed formula and a measurement agreeing; then the running partial products, which are exactly what a backward pass carries. Ends by reporting that multiplying the same five rates forwards and backwards gives different bit patterns, and that the lab compares them with a tolerance rather than `==`. |
| `04_two_paths_add.py` | The centrepiece. One input, two routes, two path products, and four candidate answers put to a central difference — of which only the sum survives. Then why the cancelling mnemonic has nothing to say here. Then the full multivariable case with two inputs and two intermediates, where every gradient is a sum of two products. |
| `05_the_value_engine.py` | The engine from the smallest possible graph upward: a product's two local rates; `x + x` and `x * x`, where the `+=` earns its keep and the power rule falls out of the product rule unasked; the topological order printed node by node with the reason it cannot be skipped; four expressions differentiated by the engine and by measurement; and the tanh identity the engine reproduces without being told it. |
| `06_backprop_by_hand.py` | The network, the exact forward pass, then the backward pass as a table of fourteen local rates with the running gradient beside each. Two gradients get a second look: `d loss/d vA` is exactly zero because it multiplies a dead unit, and `d loss/d x1` is a sum over two paths. Ends with all sixteen gradients three ways and the pass counts each mode needed. |
| `07_vanishing_and_exploding.py` | Fifty factors of 0.9 and of 1.1, traced every ten layers; a harsher table with a "would this move a weight of 1?" column; the same collapse through the real engine; reverse against forward against numerical, counted; what reverse mode pays in memory; and then section 6, which measures a case where sections 1 and 2 are wrong by ten orders of magnitude and explains why. |
| `.venv/bin/pytest examples -q -p no:cacheprovider` | The 235 reference tests. `-p no:cacheprovider` stops pytest writing a `.pytest_cache` directory. |
| `bash tests/run_tests.sh` | The 120-check harness: versions, every script, both suites, ninety individual values, a deliberate self-failure, and a clean-disk check. |

## Expected output

The captured files live in `expected-output/`. The harness ends with:

```
120 checks, 0 failure(s).
```

and exits 0. The reference suite ends with `235 passed`, and an untouched
starter with `2 passed, 163 skipped`.

Four blocks worth recognising before you meet them. The four candidate answers,
put to a measurement:

```
     candidate answer            value      matches the measurement?
     ------------------------------------------------------------
     sum of the paths, 24 + 12   36         YES
     path through u alone        24         no
     path through v alone        12         no
     product of the paths        288        no
```

The engine reproducing the power rule without having heard of it:

```
      x = 3,  y = x x x
      y.data = 9.0,  x.grad = 6.0   <- 2x, the power rule
```

The two gradients in the network that are worth a second look:

```
     d loss / d vA                x a = x 0                      0
     d loss / d x1, through A     d loss/d a_pre x wA1 = -6.000
     d loss / d x1, through B     d loss/d b_pre x wB1 = -3.375
     d loss / d x1, total         -6.000 + -3.375 = -9.375
```

And the measurement that corrects the standard vanishing-gradient story:

```
     depth    gradient at x = 0.9     ratio to the row above
     1        4.869174e-01            -
     40       8.397332e-03            2.636
     160      1.113159e-03            2.771

      0.486917 ** 40 = 3.149274e-13     the prediction
      measured at depth 40 = 8.397332e-03     the measurement
```

Ten orders of magnitude apart. Each `tanh` pulls its input towards zero, where
`tanh`'s slope is 1, so the local rates climb back towards 1 as the stack
deepens and the product decays like a power of the depth rather than
exponentially. A product of constants is the wrong model for a product of rates
that depend on where they are evaluated. The suite asserts the gap, the
monotonic fall, and the contrast case where a genuinely constant factor does
collapse geometrically — but not the value.

`expected-output/FIELDS.md` records exactly which parts of the captured output
may legitimately differ on your machine and which may not, tabulates both
tolerances against the error bounds they were derived from, and explains the
two results that contradict the obvious guess.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` prints `120 checks, 0 failure(s).`
   and `exit=0`.
2. `.venv/bin/pytest examples -q -p no:cacheprovider` prints `235 passed`.
3. `.venv/bin/pytest starter -q -p no:cacheprovider` prints `165 passed` once
   you have finished, and never prints a failure you have not been shown.
4. Each of the seven scripts ends with `every assertion held.`
5. `find . -path ./.venv -prune -o -type d -name '__pycache__' -print` prints
   nothing after a full run.

## Tests

`tests/run_tests.sh` runs 120 checks in seven sections:

1. **Versions** — reads the installed numpy and compares it against
   `requirements/requirements.txt`, confirms it is NumPy 2 or later, and
   confirms this interpreter's floats are IEEE-754 doubles with a 53-bit
   significand, because two of the day's results are consequences of that width.
2. **The seven reference scripts** — each must exit 0 and print that every one
   of its internal assertions held.
3. **The reference pytest suite** — must exit 0, report no failures, and have
   collected at least 200 tests, so a collection error cannot pass as success.
4. **The starter suite** — must exit 0 on an untouched checkout with skips
   rather than failures; and collecting both suites at once must not turn any
   of those skips into passes, which is a real hazard here because both
   directories contain modules called `autodiff`, `chainrule`, `dataset` and
   `network`.
5. **Ninety individual values** — the gear and currency products, both
   composition orders, the correct chain rule and the wrong one, all six
   compositions against both the closed form and a measurement, the sigmoid's
   maximum slope, the five-stage values and rates and three routes to 0.4, the
   two multiplication orders differing by rounding, the two path contributions
   and their sum with all three wrong candidates rejected, the surface and both
   its partials, the engine's product rule and its accumulation, the tanh
   exactness facts, the topological order, a twenty-thousand-node graph, the
   whole network forward and backward three ways, the pass counts for all three
   modes, and every order of magnitude in the collapse and blow-up sections
   including both results that contradict the obvious guess.
6. **A deliberate failure** — the harness re-runs itself with one expectation
   swapped for `-6.0`, which is what you get by following only the first of the
   two paths from `x1` to the loss. It asserts that the re-run exits non-zero
   and reports exactly one failure. A green suite proves nothing until you have
   watched it go red, and this is the day's most instructive mistake to fail on.
7. **A clean disk** — no `__pycache__` and no `.pytest_cache` outside `.venv`,
   and no source file that opens a network connection.

Before section 1, the harness clears any `__pycache__` and `.pytest_cache`
that an **earlier** command left behind, pruning `.venv` as it goes. This
matters more than it sounds. The README above tells you to run
`.venv/bin/pytest starter -q`, and that command legitimately writes
`starter/__pycache__` and `.pytest_cache`. Without the pre-run clear, section 7
would then report those as litter — failing you for following the instructions
in this file. Clearing them at the start makes the final check measure what it
claims to measure: what *this* run left behind.

The harness was confirmed to exit 0 in four configurations: with the real
lab-local `.venv`; with no `.venv` at all and `PYTEST` pointing at an
interpreter elsewhere; with a fake `.venv` present containing nothing but
litter; and — in all three of those — with the README's own
`pytest starter -q` run immediately beforehand, so the tree is already dirty
when the harness starts. With the pre-run clear removed, that last scenario
produces three failures, so the block is load-bearing rather than decorative.
`.venv` is the documented setup, not a stray file, and nothing in the suite
treats it as one or deletes anything inside it.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: resets your work
```

The lab's own commands leave none of the first two behind; section 7 of the
harness fails if they appear. It deliberately does not look inside `.venv`,
because the bytecode caches shipped with NumPy and pytest are theirs, not yours.

## Troubleshooting

See `troubleshooting.md`. It covers wrong-directory import errors, the starter
tests that keep skipping because a `return None` survived below your code, the
`=`-instead-of-`+=` bug and exactly which two tests catch it, the chain rule
evaluated at `x` instead of at `u`, the central difference divided by `h`
instead of `2h`, the `-6.0`-instead-of-`-9.375` single-path gradient, the
`RecursionError` from a recursive topological sort, why the engine and your
hand computation should agree *exactly* while a numerical gradient should not,
the stacked-tanh result that looks wrong and is not, the `__pycache__` search
that must prune `.venv`, and the import collision the two `conftest.py` files
prevent. All of them were hit while building this lab or are named by a test.

## Security notes

See `security.md`. In short: this lab computes and prints. It writes no files,
opens no connection after the one-time install, needs no credentials and no
`sudo`, and all the data is invented. Three points there are worth carrying
away: a gradient that is silently wrong is far more expensive than one that
crashes, and the `+=`-versus-`=` bug is the model case — correct types, correct
shapes, plausible magnitudes, wrong answers, no warning; reverse mode's speed is
paid for in retained activations, which makes input length an availability
concern in anything that differentiates; and a long product leaves the useful
numeric range silently in both directions, underflowing to zero or overflowing
to `inf`, after which one arithmetic operation turns every parameter into `nan`.

## Extension exercises

1. **Add one operation.** Give `Value` an `exp()` method — the derivative of
   `e**x` is `e**x`, so the backward step can reuse the forward value exactly
   as `tanh` does. Then build the sigmoid out of it and check its slope at zero
   against the 0.25 that script 02 measured, using your engine rather than a
   formula.
2. **Add a division, and find where it breaks.** Implement `__truediv__` as
   multiplication by a reciprocal, and give the reciprocal a backward step of
   `-1/u²`. Then differentiate something at `u = 0` and decide what your engine
   should do about it. Day 108's answer — that a method which always returns a
   number will return one where no answer exists — applies here too.
3. **Make the accumulation bug visible.** Change one `+=` to `=` in your own
   copy and run the reference suite. Note which tests fail, which pass, and how
   large the wrong answers are. Then predict, before running it, whether the
   two-layer network's loss would still go down under gradient descent with
   those gradients. Day 111 gives you the loop to find out.
4. **Count the paths.** Write a function that enumerates every distinct path
   from a given leaf to the output of a `Value` graph, and check that the sum of
   the path products equals the gradient your engine computed. On the two-layer
   network there are two paths from `x1`; build a three-layer version and count
   them again. Then work out how many paths a ten-layer network with eight units
   per layer has, and why reverse mode never enumerates them.
5. **Second derivatives, the hard way.** Your engine differentiates a number.
   To differentiate a *gradient* you would need the backward pass itself to be
   built out of `Value` objects. Sketch what would have to change, and then look
   up what `create_graph=True` does in PyTorch's documentation and compare.
   Describe it; do not claim output you did not run.
6. **Find your own vanishing point.** Section 6 measured stacked `tanh`.
   Repeat it for the sigmoid and for `x -> 0.5 * x` interleaved with `tanh`, and
   find the depth at which each gradient first stops moving a weight of 1.0.
   Predict the ordering before you measure, then explain any case where you were
   wrong — the reasoning in section 6 is the tool for that.

## Navigation

- Previous day: Day 109 — Partial Derivatives and Gradients
- Next day: Day 111 — Gradient Descent from Scratch
- Week 16: Linear Algebra II and Calculus
- Section: Mathematics, Statistics and Data
