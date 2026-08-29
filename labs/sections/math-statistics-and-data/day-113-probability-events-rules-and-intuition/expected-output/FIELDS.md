# What may legitimately differ on your machine

Captured from a real run on 2026-08-17: macOS 26.5.2 (Apple Silicon, arm64),
Python 3.14.0, numpy 2.5.2, pytest 9.1.1, bash 3.2.57.

## Will not differ

- Every exact-probability figure computed with `fractions.Fraction`:
  `P(sum == 7) = 1/6`, the addition-rule naive sum `1/3` and true union
  `11/36`, de Méré's two exact bets, both independence checks, the mutual
  exclusivity result, the conditioning result, and the urn total `9/20`.
  These are rational arithmetic over a fixed 36-outcome or 20-outcome space
  and are identical on every machine and every Python version that
  implements `Fraction` correctly.
- The count of reference tests collected (93) and the starter suite's
  pass/skip counts on an untouched checkout (3 passed, 43 skipped).
- The check count in the harness (57) and the failure count (0) on a clean
  run.

## Will differ, and by how much

- **The simulated values in `03_de_mere.py`, `08_monte_carlo_error_scaling.py`
  and `09_reproducibility.py`.** These come from `numpy.random.default_rng`,
  and while a *given* seed on a *given* NumPy version produces the same
  sequence everywhere, the exact figures printed in these captured files
  (e.g. `0.515865` for de Méré's bet 1) are not asserted anywhere in the test
  suite — the suite asserts that they land within a stated tolerance of the
  exact value, and that tolerance is what travels, not the figure.
- **Wall-clock timings** are not printed or compared anywhere; the whole
  suite finishes in well under a second and nothing here is a benchmark.
- **`platform` and `exe`** in section 1's output reflect the machine running
  the harness, not this one.

## The two tolerances, and where they come from

| Comparison | Tolerance | Derivation |
| --- | --- | --- |
| A simulated de Méré probability against its exact `Fraction` value | `3 x sqrt(p(1-p) / 200,000)` — about `0.00335` for both bets | Three standard errors of a proportion estimated from 200,000 independent trials. About 99.7% of honest simulation runs land inside this band; the harness runs once and accepts the small chance of landing outside it, same as any single Monte Carlo check would. |
| A reproducibility-seed estimate against the true `1/6` | `4 x sqrt(p(1-p) / 10,000)` — about `0.0149` | Four standard errors at 10,000 trials, a wider margin because this check runs on only two seeds rather than being averaged, and a false failure here would be a distracting false alarm rather than a meaningful one. |

Both are derived from the formula, not chosen by running the suite and
loosening a number until it passed — the arithmetic is written out in
`examples/dataset.py` beside each constant.

## The Monte Carlo error-scaling numbers

`08_monte_carlo_error_scaling.py` reports the *shape* of a trend averaged
over 20 seeds at each of four sample sizes, and only the shape is asserted:
monotonically decreasing error, a decrease of more than 5x from n=100 to
n=100,000, and a shrink factor within 3x of the `sqrt(n)` prediction rather
than anywhere near the `n` prediction. The exact mean-error figures — in the
captured run, `0.023000` at n=100 falling to `0.000977` at n=100,000, a
23.55x shrink against a `sqrt(1000) = 31.62x` prediction — will differ
slightly on another NumPy version or another CPU's random-number stream, but
the shape claims are what the tests check and they are robust across seeds
by construction.
