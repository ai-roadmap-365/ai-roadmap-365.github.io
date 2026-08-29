# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-17, with numpy 2.5.2 and pytest 9.1.1 on CPython 3.14.0,
macOS 26.5.2 on Apple Silicon (arm64), through a real lab-local `.venv` created
by the setup commands in the README. If your run differs in one of the ways
listed here, nothing is wrong. If it differs in any other way, something is.

This lab is unusually reproducible, even by this course's standards. There is
no randomness, no timing, no I/O and no platform-dependent library call in any
of the arithmetic. The two-layer network was built so that **every number in
both its passes is exact in float64** — that is what the bias of half the
natural logarithm of 3 buys — so the "must not differ" table below is long and
the "will differ" table is short.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| Elapsed times, such as `235 passed in 0.15s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Wall-clock timing on one machine on one day. Nothing in this lab asserts a duration. |
| The `platform` line, for example `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. |
| The pass/skip glyph line, such as `.sssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `2 passed, 163 skipped`. As you complete exercises, passes replace skips. That is the file changing because you changed, not because anything broke. |
| The last two or three digits of any **measured** derivative | `02`, `03`, `04`, `05`, `06` captures, `test-run.txt` section 5 | A central difference is an approximation. Its low digits depend on your maths library's `exp`, `sin`, `log` and `tanh`. Every such comparison in the lab uses `NUMERIC_TOL`, and the individual digits are printed for interest rather than asserted. |
| The four "measured on this run" lines | `test-run.txt` sections 5 | These are explicitly labelled as reported rather than asserted. See the section below. |

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| `6.0`, `36.0`, `150.0` for the gear and currency chains | `01-gears-and-rates.txt` | Exact products of exact decimals. Re-derivable with a pen. |
| `1.0` for the empty product | `test-run.txt` section 5 | One is the identity for multiplication. A lab that returned 0.0 here would be a different lab. |
| `49.0` and `13.0` for the two composition orders | `02-composition-and-the-chain-rule.txt` section 1 | `(3·2+1)²` and `3·(2²)+1`. Exact integers. |
| `42.0` correct and `12.0` for the deliberate mistake | `02-composition-and-the-chain-rule.txt` section 2 | The mistake is asserted **as** a mistake, so that no future edit can make it accidentally right. |
| `0.25` for the sigmoid's slope at zero | `02` section 4 | Exact: `(-1/4) × (-1)`. It is also the sigmoid's maximum slope anywhere, which the suite checks at six other points. |
| `2.0` for `tanh(2x + 1)` at `x = -0.5` | `02` section 4 | The inner function is exactly 0 there and `tanh'(0)` is exactly 1, so the answer is exactly `1 × 2`. |
| `1, 2, 5, 25, 5, ln 5` and rates `2, 1, 10, 0.1, 0.2` | `03-deeper-chains.txt` sections 1–2 | Exact arithmetic on the five stages. The `10` is the one to check: it is `2u` evaluated at the value arriving at that stage, which is 5. |
| `0.4` three ways | `03` section 3 | The product of the five local rates, the collapsed formula `2/(2x+3)` at `x = 1`, and a measurement. The first two are exact. |
| `24.0`, `12.0` and `36.0` | `04-two-paths-add.txt` sections 2–3 | The two path contributions and their sum. `36` is also `9x²` at `x = 2`. The suite asserts that neither `24`, nor `12`, nor `288` matches the measurement. |
| `37`, `34`, `26` for the surface | `04` section 5 | `z = (st)² + (s−t)²` at `(2, 3)`, and both partial derivatives. All integers. |
| `2.0` for `x + x` and `6.0` for `x * x` at `x = 3` | `05-the-value-engine.txt` section 2 | The engine accumulating two contributions. `1.0` and `3.0` respectively would mean the gradient was assigned rather than accumulated. |
| `20001` nodes for a ten-thousand-operation chain | `test-run.txt` section 5 | Each `node * 1.0` allocates a Value for the constant as well as one for the product, so ten thousand operations leave twenty thousand nodes plus the original leaf. |
| The whole forward pass: `0.0`, `0.5`, `-0.5`, `2.25` | `06-backprop-by-hand.txt` section 2 | Exact. `tanh(0) = 0` and `tanh(½·ln 3) = 0.5` **exactly** in float64, both asserted by the reference suite rather than assumed. |
| All sixteen network gradients | `06` sections 3–5, `test-run.txt` section 5 | Every one is exact, and the hand computation and the engine agree **bit for bit** — asserted with `==`, not with a tolerance, because they perform the same multiplications in the same order on the same exact values. |
| `0.0` for `d loss / d vA` | `06` section 3 | `vA` multiplies an activation of exactly zero, so nudging it moves the output by exactly nothing. See the note on negative zero below. |
| `-9.375` for `d loss / d x1`, as `-6.0 + -3.375` | `06` section 4 | The day's central fact: `x1` reaches the loss through both hidden units and the two contributions are added. A product-only chain rule reports `-6.0` here and looks entirely reasonable doing it. |
| `1`, `25`, `50` passes for the three modes on 25 inputs | `07-vanishing-and-exploding.txt` section 4 | Structural counts, not measurements. Reverse mode is 1 for any number of inputs. |
| `5.153775e-03` and `1.173909e+02` | `07` section 1 | `0.9⁵⁰` and `1.1⁵⁰`. IEEE-754 arithmetic on exact decimals; identical on any conforming machine. |
| Orders `-3`, `+2`, `-10`, `+8`, `-16`, `-31`, `+15` | `07` sections 1–2 | The exponents, which is what the suite asserts rather than the digits. |
| `0.5⁵⁰ == 4 × EPSILON` and `1.0 + 0.5⁵⁰ != 1.0` | `07` section 2 | A property of the binary format, not of the machine. See the surprise below. |
| `0.25⁵⁰` vanishing when added to 1.0 | `07` section 2 | Also a property of the format. |
| `120 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| `235 passed` | `reference-tests.txt` | The reference suite has 235 tests. A different count means tests failed to collect. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |

## The four numbers that are reported rather than asserted

The harness prints four lines beginning `(measured on this run: …)`. These are
measurements, and the lab deliberately does not assert them to a value. On the
authoring machine they read:

```
  the worst gap between the chain rule and a central difference across the
  six compositions was 8.969e-10

  the hand route reaches d loss / d vA as -0.0, IEEE-754 negative zero,
  which compares equal to 0.0

  the worst gap between the engine and a central difference across all
  sixteen network gradients was 4.463e-09

  40 stacked tanh layers gave a gradient of 8.397332e-03 against a naive
  prediction of 3.149274e-13 from a single-layer slope of 0.486917 --
  larger by a factor of 2.666e+10
```

The first and third may move in their last digits on a different maths library.
What the lab asserts instead is that both are below `NUMERIC_TOL` (1e-6), which
they are by two to three orders of magnitude.

The second is arithmetic trivia and is reported for exactly that reason. The
hand computation reaches that gradient as `-3.0 × 0.0`, and IEEE-754 says the
sign bits multiply, so the result carries a negative sign on a zero. It
compares equal to `0.0`, behaves as zero in every subsequent operation, and the
engine reaches the same gradient by a different route and gets `+0.0`. The
check asserts `gradient == 0.0`, which is the question that matters, and
reports the sign rather than pretending both routes printed the same characters.

The fourth is the lab's most interesting measurement and is discussed below.

## The measurement that corrects the story: stacked tanh does not vanish geometrically

Sections 1 and 2 of `07_vanishing_and_exploding.py` multiply a **constant**
factor fifty times and watch the product collapse. That is the standard
picture of a vanishing gradient, and for a chain of genuinely fixed factors it
is correct — the lab asserts it, and asserts the contrast case where a constant
0.487 really does decay to below 1e-12 in forty steps.

Section 6 then measures what happens when the factor is *not* constant. Stack
forty real `tanh` operations and differentiate the result:

```
     depth    gradient at x = 0.9     ratio to the row above
     1        4.869174e-01            -
     5        1.255802e-01            3.877
     10       5.515820e-02            2.277
     20       2.213240e-02            2.492
     40       8.397332e-03            2.636
     80       3.084811e-03            2.722
     160      1.113159e-03            2.771
```

The naive prediction — take tanh's slope at the input, about 0.487, and raise
it to the fortieth — gives `3.149e-13`. The measurement is `8.397e-03`. That is
**ten orders of magnitude apart**, and it is not a rounding artefact.

The reason is worth more than the number. Each `tanh` pulls its input closer to
zero, and `tanh`'s slope *at* zero is 1. So the deeper the stack goes, the
closer every local rate creeps back towards 1, and the product decays like a
power of the depth rather than exponentially. You can see it in the ratio
column, which settles near 2.8 per doubling of depth rather than growing.

A product of constants is the wrong model for a product of rates that depend on
where they are evaluated. The suite therefore asserts:

- that the stacked-tanh gradient is positive and below 1 at every depth tried;
- that it falls **monotonically** with depth;
- that it beats the constant-factor prediction by more than nine orders of
  magnitude;
- and, as the contrast, that a genuinely constant factor of 0.487 does collapse
  below 1e-12 in the same forty steps.

It does not assert `8.397332e-03`, because that is one function at one point on
one machine.

If your ratio column reads roughly 2.3 to 2.8 and your depth-40 value is
somewhere in the low thousandths, nothing is wrong. If it reads 1e-13, your
engine is multiplying a constant somewhere it should be re-evaluating a rate.

## The other surprise: 0.5 to the fiftieth does *not* vanish

`0.5⁵⁰` is about `8.88e-16` and float64's epsilon is about `2.22e-16`, so the
obvious guess is that adding it to 1.0 loses it. It does not:

```
      0.5 ** 50 = 8.881784e-16,  which is 4 x EPSILON
      1.0 + 8.881784e-16 == 1.0  ->  False
```

Four representable gaps is still four gaps. It takes three more halvings —
`0.5⁵³`, which is exactly half an epsilon — before the addition rounds away to
nothing, and the suite asserts both halves of that.

The row that genuinely vanishes is `0.25⁵⁰`, and `0.25` was not chosen for
drama: it is the **largest** slope the sigmoid ever has, measured in script 02.
A stack of sigmoid layers is multiplying numbers no bigger than that one.

## Why the two tolerances differ by a factor of a million

| Comparison | Tolerance | Why |
| --- | --- | --- |
| Hand computation vs the engine | exact `==` | Same multiplications, same order, same exact values. Anything less than equality here would be hiding a bug. |
| Analytic vs analytic (different order) | `ANALYTIC_TOL` = 1e-12 | float64 multiplication is not associative, so multiplying five local rates forwards and backwards can land on different bit patterns. The gap is a few units in the last place; the lab measures it as under `4 × EPSILON` and asserts that the two are **not** identical as well as that they are close. |
| Analytic vs a central difference | `NUMERIC_TOL` = 1e-6 | A central difference is an approximation with two error terms of its own: truncation `≈ (h²/6)·|f‴|` and rounding `≈ EPSILON·|f|/h`. At `h = 1e-5` and magnitudes up to 250 that bound is about `9.7e-9`, so 1e-6 carries roughly a hundredfold margin. |

The last row is the one people get wrong. Comparing an analytic gradient
against a numerical one at 1e-12 would fail on correct code, and it would fail
for reasons that have nothing to do with the chain rule. Comparing two analytic
routes at 1e-6 would pass on code that had dropped a whole path. Both
tolerances are derived in `examples/dataset.py` with the arithmetic written out,
and a reference test asserts that neither is loose enough to be meaningless.

## Reproducing these files

From the lab directory, after the one-time install:

```bash
cd examples && ../.venv/bin/python3 01_gears_and_rates.py; cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
bash tests/run_tests.sh
```

The scripts in `examples/` are run from inside `examples/` because they import
`chainrule.py`, `autodiff.py`, `network.py` and `dataset.py` from beside
themselves.
