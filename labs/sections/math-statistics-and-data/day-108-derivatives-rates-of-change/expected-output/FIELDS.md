# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-17, with numpy 2.5.2 and pytest 9.1.1 on CPython 3.14.0,
macOS 26.5.2 on Apple Silicon (arm64), through a real lab-local `.venv` created
by the setup commands in the README. If your run differs in one of the ways
listed here, nothing is wrong. If it differs in any other way, something is.

This lab is unusually reproducible. Almost nothing here is a timing, a random
draw or a platform quirk — it is float64 arithmetic on numbers written out in
`dataset.py`. That makes the short "will differ" list below meaningful rather
than a disclaimer.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| Elapsed times, such as `178 passed in 0.11s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Wall-clock timing on one machine on one day. Nothing in this lab asserts a duration. |
| The `platform` line, for example `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. |
| The pass/skip glyph line, such as `.sssssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `1 passed, 99 skipped`. As you complete exercises, passes replace skips. That is the file changing because you changed, not because anything broke. |
| **The exact position of the bottom of the U** | `05-the-u-shaped-error.txt` section 4, `test-run.txt` section 5 | See the section below. This one is genuinely machine-dependent, and it is the most interesting entry in this file. |
| **Every error value below about 1e-10** | `05-the-u-shaped-error.txt` section 3 lower rows, section 5 | Once rounding error dominates, the digits that survive the subtraction depend on your maths library's exact `exp`. The SHAPE is asserted; these individual numbers are reported. |

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| `24.0`, `28.0`, `20.0` and the six per-second speeds | `01-average-rate-of-change.txt` | Exact arithmetic on 4t². Re-derivable with a pen. |
| `ZeroDivisionError` on a zero-width interval | `01-average-rate-of-change.txt` section 4 | The lab raises it deliberately. A run that returned 0.0 or nan instead would be a different lab. |
| `7.0`, `6.1`, `6.01`, `6.001` | `02-shrinking-intervals.txt` section 2 | The average rate of x² over [3, 3+h] is 2a + h = 6 + h, exactly, as algebra. |
| The last-place gaps of about `7e-15`, `2e-14`, `1e-13` | `02-shrinking-intervals.txt` section 3 | These are float64 rounding on numbers of order 10 and are stable on any IEEE-754 machine doing the same operations in the same order. They may move by a unit in the last place if your build reassociates; the assertion is `< 1e-12`, which has three orders of headroom. |
| `y = 6x - 9` | `02-shrinking-intervals.txt` section 4 | The tangent to y = x² at x = 3. |
| `0.693147181`, `0.916290732`, `1.000000000`, `1.098612289`, `2.302585093` | `03-rules-checked-numerically.txt` section 4 | These are the natural logarithms of 2, 2.5, e, 3 and 10. That the slope of bˣ at 0 is ln(b) is the whole point of the section, and e is the base where it comes out at 1. |
| The eight exact rule values `0, 6, 25.3125, -0.25, 30, 16, e, 0.25` | `03-rules-checked-numerically.txt` section 3 | Each is one application of a rule and is checkable by hand. |
| `6 + h` and `6 - h` forward and backward, and central exactly `6` | `04-forward-and-central.txt` section 2 | Algebra on a quadratic, not a numerical accident. |
| The ratios `1.0000` three times | `04-forward-and-central.txt` section 4 | The measured central error divided by the predicted h²·f‴/6. It matches to four decimal places because the prediction is correct, not because it was fitted. |
| `identical to the last bit True` | `04-forward-and-central.txt` section 5 | `np.gradient(ys, h)` interior IS the central difference, in the same arithmetic. Asserted with `==`. |
| `forward_difference(exp, 1.0, 1e-300)  ->  0.0` | `05-the-u-shaped-error.txt` section 1 | There is no float64 between exp(1) and exp(1 + 1e-300). This is a property of the format, not of the machine. |
| `2.220446049250313e-16` | `05-the-u-shaped-error.txt` section 2 | float64 machine epsilon. A reference test compares it against `np.finfo(np.float64).eps` rather than trusting the literal. |
| Both curves being U-shaped at all | `05-the-u-shaped-error.txt` section 4 | Asserted. If the error on your machine fell monotonically to 1e-14, something would be very wrong. |
| `0.000e+00`, `9.998e-09`, `1.000e-08` at the four stationary points | `06-zero-derivative-and-curvature.txt` section 1 | The central difference's truncation error on a cubic is exactly h²·f‴/6 = h² = 1e-8. Not a coincidence and not tuning. |
| `2.000000`, `-6.000000`, `6.000000`, `0.000000` | `06-zero-derivative-and-curvature.txt` section 3 | The exact second derivatives of the four functions at those points. |
| `minimum`, `maximum`, `undecided`, `not stationary` | `06-zero-derivative-and-curvature.txt` section 4 | The classifications. `undecided` at x³ and at x⁴ is the honest answer and is asserted in both suites. |
| `1.0`, `-1.0`, `0.0` for |x| at zero | `07-where-the-derivative-fails.txt` section 2 | Exact. |x±h| is exactly h for any h, so these are exact integers in float64. |
| `200.0`, `2,000.0`, `200,000.0` | `07-where-the-derivative-fails.txt` section 3 | The second difference at the corner is exactly 2/h. |
| `1.0`, `0.0`, `0.5` for relu at zero | `07-where-the-derivative-fails.txt` section 4 | Exact, and the `0.5` is the point of the section. |
| `97 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| `178 passed` | `reference-tests.txt` | The reference suite has 178 tests. A different count means tests failed to collect. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |

## The number that is genuinely yours: where the bottom of the U sits

The authoring machine measured:

```
     forward:  best h = 1.000e-08   error there = 6.602751e-09
     central:  best h = 3.162e-06   error there = 3.291500e-11
```

**Both of those may move on your machine, and the lab does not assert either.**

What it asserts instead:

- both curves are U-shaped — the minimum is in the interior and both ends are
  more than a hundred times worse;
- the best forward `h` lands somewhere in `1e-9` to `1e-6`;
- the best central `h` lands somewhere in `1e-7` to `1e-4`;
- the best central error beats the best forward error;
- each measured optimum is within a factor of ten of the value you get by
  balancing the truncation and rounding terms — `sqrt(2·EPSILON)` = 2.107e-08
  for the forward rule and `(3·EPSILON)^(1/3)` = 8.733e-06 for the central one.

A factor of ten is the honest expectation and not a hedge. The grid has three
steps per decade, so it cannot resolve better than that in the first place; the
constants in both error terms were dropped when the balance was solved; and
rounding error near the bottom is a random walk rather than a smooth curve — you
can see it jittering in section 5 of the captured file, where the error at
h = 1e-6 is *worse* than at h = 3.16e-6 and at h = 3.16e-7.

If your bottom sits at 1e-5 rather than 3.16e-6, nothing is broken. If it sits
at 1e-14, something is.

## Why almost nothing here is compared with a tolerance you cannot check

Every tolerance in the lab is derived in `examples/dataset.py` from the two
error terms that govern a difference quotient, and the arithmetic is written out
beside each one:

| Tolerance | Value | Derived bound | Headroom |
| --- | --- | --- | --- |
| `CENTRAL_TOL` | 1e-9 | 1.1e-10 | ~9x |
| `FORWARD_TOL` | 1e-4 | 1.4e-5 | ~7x |
| `RULE_TOL` | 1e-8 | 2.25e-9 | ~4x |
| `SECOND_TOL` | 1e-5 | 1.8e-7 | ~50x |
| `STATIONARY_TOL` | 1e-6 | 1.0e-8 | ~100x |
| `EXACT_TOL` | 1e-12 | ~1.4e-13 measured | ~7x |

None was reached by running a test and enlarging the number until it went green,
and a reference test asserts that none of them is loose enough to be
meaningless — `CENTRAL_TOL < 1e-8`, `SECOND_TOL < 1e-4` and so on. A tolerance
large enough to pass anything is not a test.

## Reproducing these files

From the lab directory, after the one-time install:

```bash
cd examples && ../.venv/bin/python3 01_average_rate_of_change.py; cd ..
.venv/bin/pytest examples -q -p no:cacheprovider
.venv/bin/pytest starter -q -p no:cacheprovider
bash tests/run_tests.sh
```

The scripts in `examples/` are run from inside `examples/` because they import
`derivatives.py` and `dataset.py` from beside themselves.
