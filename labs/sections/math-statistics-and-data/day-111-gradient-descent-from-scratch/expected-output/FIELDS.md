# What may legitimately differ on your machine

Everything captured in this directory came from one real run, on
2026-08-17, through a real lab-local `.venv` built from the documented
setup commands: Python 3.14.0, numpy 2.5.2, pytest 9.1.1, macOS 26.5.2
(Apple Silicon, arm64).

## Will not change

The quadratic exercises (1-4) are exact float64 algebra — one
multiplication per step on values chosen so the arithmetic is exact. The
regime classifications, the second value of the "exact" run (`0.0`), and
the three contraction ratios (`0.5`, `0.75`, `1.25`) are bit-for-bit
reproducible on any IEEE-754 double-precision platform. The same is true
of the two-minima result (`-1.0` and `1.0` to well inside the stated
tolerance) and the gradient-check flags (`[True, False, True]`).

## Will not change in shape, though the exact figures may shift slightly

- **Ill-conditioning step counts** (`1|27|122|691` for kappa in
  `{1, 5, 20, 100}`): these depend only on exact arithmetic on the bowl's
  two eigen-directions, so they should reproduce exactly on any
  IEEE-754-double platform. The suite asserts the *shape* — non-decreasing,
  and kappa=100 needing at least 10x the steps of kappa=1 — not the literal
  numbers, precisely so a future change to `KAPPA_GRAD_TOL` or
  `KAPPA_MAX_ITERS` cannot silently break the test.
- **Momentum step count** (`34` against plain descent's `122`): same
  reasoning. The suite asserts `momentum < plain`, not the specific counts.
- **The overflow step** (`3890` for inf, `3891` for nan, at `eta = 2.2` on
  `a = 1`): this is IEEE-754 double-precision overflow arithmetic and is
  fully determined by the update rule, so it reproduces exactly on any
  platform with 64-bit doubles. It is reported in the harness output, not
  asserted to the literal step count — the assertion is only that nan
  follows inf on the very next step.

## Numeric tolerances, and why each one is sized the way it is

| Comparison | Tolerance | Why |
| --- | --- | --- |
| `numeric_gradient` vs. an analytic gradient | `NUMERIC_TOL = 1e-6` | A central difference at `h = 1e-6` carries truncation error of order `h**2 = 1e-12` and rounding error of order `EPSILON / h ~ 2.2e-10`. Both are far below `1e-6`, leaving comfortable margin. |
| Two analytic routes to the same exact quadratic quantity (a closed-form value against a step-by-step loop) | `EXACT_TOL = 1e-9` | Both routes perform the same floating-point multiplication, so the only source of disagreement is the order operations are carried out in, which for a handful of multiplications stays many orders of magnitude below `1e-9`. |
| Gradient check, correct vs. buggy component | `CHECK_TOL = 1e-4` | Deliberately loose relative to `NUMERIC_TOL`, because the point of exercise 7 is to catch a gross sign error, not to re-derive Day 108's error bound. |

## Platforms this lab was actually run on

macOS only, on this machine, today. Linux is not run here; the commands
are unchanged and nothing in the lab is platform-specific (pure Python and
NumPy arithmetic), but "should work" and "was run" are different claims
and only the second one is made here. Windows is documented in
`troubleshooting.md` as WSL or Git Bash, and is likewise not run here.
