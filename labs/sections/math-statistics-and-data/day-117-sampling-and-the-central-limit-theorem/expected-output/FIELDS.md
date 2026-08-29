# Which figures are exact, and which will differ on your machine

All nine `.txt` files here were captured from a real run on 2026-08-17
(macOS 26.5.2, Apple Silicon, Python 3.14.0, numpy 2.5.2), through a
real lab-local `.venv` created by the documented setup commands.

## Exact, identical anywhere

- **`08-the-evaluation-margin.txt`** -- every number in this file is
  closed-form arithmetic (`sqrt(p_hat * (1 - p_hat) / n)`), not sampled.
  `1.254` percentage points and `0.24` standard errors will be identical
  bit-for-bit on any correct implementation, anywhere, for the same inputs.
- The **population parameters printed at the top** of files 01, 03 and 05
  (`SKEWED_SCALE = 3.0`, `POP_SIZE = 200,000`) are configuration, not
  measurements, and will read the same everywhere `dataset.py` is
  unmodified -- though the population itself is a random draw from that
  configuration (see below).

## Sampled, and will differ within the stated tolerance

Every other number in every other file was measured from a seeded random
draw and will differ, in its last one or two significant figures, on a
different machine, a different NumPy version, or after any edit to
`dataset.py`'s trial counts. The tolerances in `examples/sampling.py`'s
callers and in `dataset.py` were set from measurements taken across six
different seeds (1, 2, 3, 42, 117, 999) during development, specifically
so that a rerun with a different seed still passes:

| File | What is sampled | Tolerance band checked across 6 seeds |
| --- | --- | --- |
| `01-sampling-distribution.txt` | The sampling distribution's own mean and standard error | measured mean within 3 SE of population mean; measured SE within 3 SE of theoretical SE |
| `02-the-sqrt-n-law.txt` | Four measured standard errors and their pairwise ratios | each successive ratio observed 1.98-2.03; asserted within 0.25 of 2.0 |
| `03-clt-from-a-skewed-population.txt` | Five skewness values, plus the coin and two-spike population skewness | strictly monotone decrease at every seed tested |
| `04-the-cauchy-counterexample.txt` | Four IQR values and their two ratios | Exponential ratio observed 9.7-9.96 (floor: 8.0); Cauchy ratio observed 0.98-1.03 (band: 1/3 to 3) |
| `05-bias-does-not-shrink.txt` | The true population mean, biased pool mean, and four mean-absolute-error values | unbiased ratio observed 9.8-10.3 (floor: 7.0); biased ratio observed 0.99-1.00 (band: 0.4 to 2.5) |
| `06-bootstrap-from-scratch.txt` | sigma_hat, both bootstrap standard errors, and the fresh-sample median SE | mean SE relative error observed under 1.1% (tolerance: 15%); median ratio observed 0.57-1.11 (band: 1/3 to 3) |
| `07-dependence-inflates-se.txt` | The true SE (by replication) and the naive SE (averaged over 500 series) | ratio observed 2.34-2.46 (floor: 1.5) |
| `09-reproducibility.txt` | The first three sample means under two seeds, and the gap between seeds | identical-seed check is exact (bit-for-bit); cross-seed gap observed under 1 SE, asserted under 5 |

The **populations themselves** (`SKEWED_POP`, `COIN_POP`, `TWO_SPIKE_POP` in
`dataset.py`) are generated once, deterministically, from
`numpy.random.default_rng(DATASET_SEED)` with `DATASET_SEED = 117`. They
are therefore identical on any machine running the same NumPy major version
-- NumPy's `Generator` bit-stream algorithm (PCG64) is specified and stable
across platforms for a given NumPy version, but is not guaranteed
byte-identical across NumPy's own major version boundaries if the
underlying bit generator implementation changes.

## Reported, never asserted, in the scripts' own printed output

A few lines in the `.txt` files -- for example the exact bootstrap-median
ratio and the exact per-seed skewness values -- are printed for the reader
to see the shape of the result, but the assertions in the corresponding
script and in `tests/run_tests.sh` check a tolerance band or a monotone
trend, never the literal printed digits. If your own run prints
`ratio = 9.79` where this file shows `9.85`, that is expected behaviour,
not a bug.
