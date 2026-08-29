# Which figures are exact, and which will differ on your machine

All nine `.txt` files here were captured from a real run on 2026-08-19
(macOS 26.5.2, Apple Silicon, Python 3.14.0, numpy 2.5.2), through a real
lab-local `.venv` created by the documented setup commands.

## Exact, identical anywhere

- **`01-two-sample-z-test.txt`** -- both cases use fixed, non-random
  arrays, so every z and p value is exact arithmetic and will be
  bit-for-bit identical on any correct implementation.
- **`03-duality.txt`** -- the mismatch count is derived logic (the test
  and the interval are built from the same z), not a sampled quantity;
  it must read `0` on any correct implementation, though the exact
  "rejections" count (461 here) is sampled and will vary.
- **`05-multiple-comparisons.txt`** -- the two exact analytic values,
  `0.6415` and `0.0488`, are closed-form arithmetic
  (`1 - 0.95**20` and `1 - (1 - 0.05/20)**20`) and will be identical
  anywhere.
- **`07-effect-size-vs-n.txt`** -- the population mean, standard
  deviation, absolute effect size and Cohen's d are configuration, not
  measurements, and read the same everywhere `dataset.py` is unmodified.

## Sampled, and will differ within the stated tolerance

Every other number in every other file was measured from a seeded random
draw and will differ, in its last one or two significant figures, on a
different machine, a different NumPy version, or after any edit to
`dataset.py`. The tolerances in `dataset.py` were set from measurements
taken across five different seeds (1, 2, 3, 42, 118) during development,
specifically so that a rerun with a different seed still passes:

| File | What is sampled | Tolerance band checked across 5 seeds |
| --- | --- | --- |
| `02-coverage.txt` | Measured coverage of 10,000 nominal-95% intervals | observed 0.9468-0.9526; asserted within 3 SE (0.0065) of 0.95 |
| `04-permutation-test.txt` | Two z/permutation p-value pairs, and their absolute differences | Case 1 (normal, n=60) difference observed under 0.01; Case 2 (skewed, n=8) difference observed 0.02-0.10 and required to exceed Case 1's |
| `05-multiple-comparisons.txt` (simulated rows) | Simulated family-wise rate, uncorrected and Bonferroni-corrected | uncorrected observed 0.6388-0.6436 (tolerance: 0.015 from 0.6415); corrected observed 0.0479-0.0528 (tolerance: 0.015 from 0.0488) |
| `06-power.txt` | Twelve power values (six n's, six effect sizes) plus a simulated check | theoretical vs simulated power observed to differ by under 0.02 (tolerance: 0.03) at n=100, effect=2.8 |
| `08-peeking.txt` | False-positive rate with and without peeking | with-peeking rate observed 0.1668-0.1888 (required: at least 2x alpha = 0.10); honest fixed-n rate observed within 0.02 of 0.05 |
| `09-bootstrap-vs-normal-ci.txt` | Both intervals' bounds, centers and widths | center difference observed 0.003-0.053 SE (tolerance: 0.6 SE); width ratio observed 0.972-1.023 (tolerance: 20%) |

Populations are generated fresh inside each script from an explicit
`numpy.random.default_rng(seed)` -- there is no shared, pre-generated
population file the way Day 117 used one, because every exercise here
needs its own combination of population shape, sample size and seed.
NumPy's `Generator` bit-stream algorithm (PCG64) is specified and stable
across platforms for a given NumPy version, but is not guaranteed
byte-identical across NumPy's own major version boundaries if the
underlying bit generator implementation changes.

## Reported, never asserted, in the scripts' own printed output

Several lines -- for example the exact "rejections" count in
`03-duality.txt` and the exact per-seed p-values in `04-permutation-
test.txt` -- are printed so the reader can see the shape of the result,
but the assertions in the corresponding script and in `tests/run_tests.sh`
check a tolerance band, an exact zero-mismatch count, or a monotone trend
-- never the literal printed digits of a sampled quantity. If your own run
prints `p = 0.1602` where this file shows a slightly different value, that
is expected behaviour, not a bug.
