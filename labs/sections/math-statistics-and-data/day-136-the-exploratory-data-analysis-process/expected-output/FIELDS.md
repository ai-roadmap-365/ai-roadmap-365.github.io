# What is exact, what is sampled, and what is machine-dependent

Captured on 2026-08-20 from a real run on the authoring machine (macOS
26.5.2, Apple Silicon, Python 3.14.0, numpy 2.5.2, pandas 3.0.5,
pytest 9.1.1). Every number below came from that run; none is invented.

## Exact everywhere, on any correct implementation

- The analytic family-wise error rates: `1 - 0.95^5 = 0.2262`,
  `1 - 0.95^20 = 0.6415`, `1 - 0.95^40 = 0.8715` (`01-forking-paths.txt`).
- The Bonferroni-corrected per-test alpha for m=20: `0.05/20 = 0.0025`
  (`05-bonferroni-and-its-limit.txt`).
- `bonferroni_alpha(0.05, 20) == 0.0025` and every other pure-arithmetic
  assertion in the reference suite.
- The final line of a passing `run_tests.sh`: `33 checks, 0 failure(s).`

## Sampled -- will differ slightly on another run or another machine

Every one of these is checked against a tolerance derived from a standard
error or a wide, explicitly-reasoned margin, never against a fixed
literal expected to match exactly:

- The simulated forking-paths rates in `01-forking-paths.txt` (e.g.
  "simulated over 2000 families = 0.2355" for k=5) -- checked against the
  exact rate within three standard errors. Re-running with a different
  seed moves this number; it was checked across seeds 1, 7, 42, 118 and
  2026 during development and stayed within 2.14 standard errors in every
  case observed.
- The "winning" comparison identified in `01-forking-paths.txt` and
  `02-plausible-story.txt` (`over_40 x sessions`, p=0.0059, d=0.611) is
  specific to the fixed seed `NARRATIVE_SEED=6` in `dataset.py`. A
  different seed finds a different winning comparison with a different
  effect size; the assertion only requires d >= 0.5, not this exact
  value.
- The two p-values in `03-holdout-rescues-you.txt` (real effect:
  p=6.661e-16 exploration, p=2.056e-12 confirmation; spurious column
  `spurious_8`: p=0.0248 exploration, p=0.9249 confirmation) are specific
  to `HOLDOUT_SEED=1`. Seeds 1 through 199 were swept during development
  (see the honesty note in `metadata.yml`); 157 of those 199 produced the
  same qualitative outcome (real effect survives both halves, best
  spurious column fails confirmation) with different exact p-values each
  time -- seed 1 was picked because it is both the first hit and the
  simplest to state.
- The inflation ratio in `04-choices-are-comparisons.txt` (roughly 4.9x)
  and the false-positive-rate ratio in `08-stopping-rule.txt` (roughly
  8.0x) are measured rates from finite simulations (3000 and 15000
  replicates respectively) and will vary by a few tenths on a re-run with
  a different seed.
- Every `elapsed` or timing figure is not printed by this lab's scripts at
  all; none is asserted on. Runtimes noted in `metadata.yml` narrative
  (for example, "27 passed in 1.83s") are wall-clock and will differ by
  hardware.

## Machine-dependent, described but not asserted on

- The `platform` line in section 1 of `run_tests.sh`'s output
  (`macOS-26.5.2-arm64-arm-64bit-Mach-O` here) will read differently on
  Linux or Windows/WSL; nothing in the harness checks its content, only
  that the versions line above it match `requirements.txt`.
