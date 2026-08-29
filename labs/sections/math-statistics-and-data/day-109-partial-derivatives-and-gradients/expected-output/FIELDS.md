# What in the captured output may legitimately differ on your machine

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-17, with numpy 2.5.2 and pytest 9.1.1 on CPython 3.14.0,
macOS 26.5.2 on Apple Silicon (arm64). If your run differs in one of the ways
listed here, nothing is wrong. If it differs in any other way, something is.

This lab measures floating-point error, which makes this file more important
than usual: several numbers here are *supposed* to be a little different on a
different machine, and several others are not allowed to move at all.

## Will differ, and does not matter

| What | Where | Why |
| --- | --- | --- |
| The last two or three digits of any numerical gradient | throughout | These are floating-point roundoff. `2.0000000000` on this machine may be `1.9999999998` on yours. Every assertion in this lab uses a stated tolerance for exactly this reason; none compares a derivative with `==`. |
| The worst-error figures, such as `3.961e-10` | `02-the-gradient-vector.txt` section 1, `test-run.txt` section 5 | Roundoff again. The test asserts only that the worst error is inside `GRADIENT_TOL` (1e-8) with at least tenfold headroom, which is a claim about the method rather than about this processor. |
| The contour dot products, such as `6.645e-06` | `04-perpendicular-to-the-contour.txt`, `test-run.txt` section 5 | Same. The asserted claims are that each is under 1e-4 and that they shrink tenfold per tenfold smaller step. |
| The `eps|f|/2h` comparison figures in section 1b | `05-flat-ground-three-ways.txt` | Both the measured error and the predicted bound depend on the exact rounding of your platform's arithmetic. The assertion is that the measured error sits between one hundredth and three times the predicted bound — the ORDER, not the value. |
| The shrink ratios near 10, such as `9.9758` | `04-perpendicular-to-the-contour.txt` section 2 | Asserted only to lie between 9 and 11. |
| Elapsed times, such as `271 passed in 0.19s` | `reference-tests.txt`, `starter-progress.txt`, `test-run.txt` | Wall-clock timing. Nothing in this lab asserts a duration. |
| The `platform` line, e.g. `macOS-26.5.2-arm64-arm-64bit-Mach-O` | `test-run.txt` section 1 | It reports your operating system, release and processor architecture. Linux prints something quite different, and that is expected. |
| The `python` and `pytest` version lines | `test-run.txt` section 1 | Only CPython 3.14.0 and pytest 9.1.1 were run here, so those are the only versions this lab can honestly claim. |
| The pass/skip glyph line, such as `.sssssss...` | `starter-progress.txt` | Its length tracks the number of collected tests. The counted summary underneath is the part to compare. |
| Your own progress score | `starter-progress.txt` | The captured file shows an untouched checkout: `1 passed, 205 skipped`. As you complete exercises, passes replace skips. That is the file changing because you changed, not because anything broke. |

## Must NOT differ

| What | Where | Why it is fixed |
| --- | --- | --- |
| Every *exact* gradient: `(2, 6)`, `(3, -2)`, `(13, 4)`, `(-17, -18, -8)` | throughout | These are differentiated by hand from the definitions in `surfaces.py`. They are algebra, not measurement. |
| `4` and `6` as the two partials of `x^2 + 3y^2` at `(2, 1)` | `01-hold-everything-else-still.txt` | Same. Re-derivable with a pencil in under a minute. |
| `0.0` for `df/dx` of `xy` at `(1, 0)`, and `1.0` for `df/dy` | `01-hold-everything-else-still.txt` section 4 | The point of the section. A single partial being zero says nothing about the point. |
| `72.0` as the winning bearing out of 360 | `03-steepest-ascent.txt`, `test-run.txt` section 5 | The gradient's true bearing is `arctan(6/2) = 71.5651` degrees, and 72 is the nearest whole degree. Both are exact consequences of the definitions. |
| `71.5651`, `26.5651`, `116.5651`, `341.5651`, `296.5651` | `03-steepest-ascent.txt` sections 2 and 3 | Arctangents of ratios of small whole numbers. See the note below about why five of them share a fractional part. |
| `0.4349` as the sampling gap for those five | `03-steepest-ascent.txt` | A consequence of the two lines above and a 1-degree grid. |
| `180.0000` as the separation of steepest ascent and steepest descent | `03-steepest-ascent.txt` section 4 | Geometry, not measurement. |
| `4.000000000000` and `6.000000000000` as the contour levels holding constant | `04-perpendicular-to-the-contour.txt` section 1 | The parametrisations are exact; substituting them into `f` gives the level identically. Any drift beyond 1e-12 means the algebra was changed. |
| `0.000e+00` for the exact-tangent dot products | `04-perpendicular-to-the-contour.txt` section 4 | The terms cancel algebraically: `-2L sin t cos t + 2L sin t cos t`. |
| `0.5` and `1.5` from `numpy.gradient` at the corner | `06-step-size-and-the-u-curve.txt` section 4, `test-run.txt` section 5 | NumPy's default `edge_order=1` applied to an exactly-sampled quadratic. Asserted rather than described, so a future NumPy that changed this default would fail the suite instead of letting this page go stale. |
| `0.2500000000` as `numpy.gradient`'s cubic error, matching the grid spacing squared | `06-step-size-and-the-u-curve.txt` section 4 | `0.5^2`. The h-squared law with h fixed by the sampling. |
| `1e-05` as the best central step and `1e-08` as the best forward step | `06-step-size-and-the-u-curve.txt` section 2, `test-run.txt` section 5 | See the note below — these are the only two entries in this table that could in principle move, and both are asserted. |
| `0.010000000000`, `0.000100000000`, `0.000000999998` as the cubic's error at h = 1e-1, 1e-2, 1e-3 | `06-step-size-and-the-u-curve.txt` section 1 | Exactly `h^2`, derived in the comment at the top of that section. The test asserts agreement to a relative 1e-5. |
| `22.5`, and the residuals `-4, -3, -8, -1` | `07-one-partial-per-parameter.txt` section 1 | Four invented samples and three parameters, all whole numbers. Arithmetic. |
| `6` evaluations for a three-parameter gradient | `07-one-partial-per-parameter.txt` section 5 | Two per parameter, counted by wrapping the loss in a counter. |
| `1.62875000` as the best loss over the eight step sizes tried | `07-one-partial-per-parameter.txt` section 4 | Arithmetic on the numbers above. |
| `98 checks, 0 failure(s).` | `test-run.txt` | The harness runs a fixed number of checks. |
| `271 passed` | `reference-tests.txt` | The reference suite has 271 tests. A different count means tests failed to collect. |
| `1 passed, 205 skipped` on an untouched checkout | `starter-progress.txt` | 206 starter tests, of which one is the environment check. |
| The numpy version line `numpy    2.5.2` | `test-run.txt` section 1 | Pinned in `requirements/requirements.txt`, and section 1 compares the installed version against that file rather than trusting it. |

## The two numbers that look machine-independent and are not quite

**`1e-05` as the best central step, and `1e-08` as the best forward step.**

These are troughs of an error curve that is the sum of a method error and a
roundoff error, and the roundoff half depends on your platform's arithmetic.
Theory puts the central trough near the cube root of machine epsilon
(6.06e-06) and the forward one near its square root (1.49e-08); the lab
measures 1e-05 and 1e-08, which is the nearest power of ten to each.

On a machine with materially different rounding behaviour the measured trough
could land one decade away, and the two tests that assert these exact values
would fail. That is a deliberate choice rather than an oversight. The
alternative — asserting only "somewhere in the middle" — would stop the lab
noticing if the curve changed shape, which is the more interesting failure. If
you hit it, the U-curve table printed immediately above the assertion tells you
straight away whether the shape is intact and only the trough moved, or whether
something is genuinely wrong.

## The coincidence in section 3 of `03-steepest-ascent.txt`

Five of the seven sampling gaps in that table are the identical `0.4349`
degrees, which reads like a bug and is not.

Those five gradients have bearings of 26.5651, 71.5651, 116.5651, 296.5651 and
341.5651 degrees. Every one is an arctangent of a ratio of the same small whole
numbers, and they differ from one another by exact multiples of 45 degrees, so
they all share the fractional part `.5651`. A grid sampled every whole degree
therefore misses each of them by the same 0.4349 degrees. The two rows that
break the pattern — bearings 83.6598 and 326.3099 — have different gaps, and
the script goes on to sample two deliberately untidy points where the gap
changes again.

A related consequence is recorded in the reference suite: sweeping 60
directions and sweeping 360 directions produce *exactly the same gap* at this
particular point, because both grids contain 72. So the test asserts the real
law — that the gap can never exceed half the sampling step — rather than the
plausible-sounding but false claim that a finer sweep always does better.
