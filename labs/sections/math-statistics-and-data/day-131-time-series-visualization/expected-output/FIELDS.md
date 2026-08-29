# What in these captures is exact, and what may differ

Captured from a real run on 2026-08-20, in this lab's own `.venv`, on
pandas 3.0.5, matplotlib 3.11.1, NumPy 2.5.2, pytest 9.1.1, Python
3.14.0, macOS (arm64).

## Exact everywhere, on any correctly installed copy of these pins

- `examples-run.txt` ends with `17 passed`, `starter-run.txt` ends with
  `17 skipped` — both counts are structural (17 test functions in each
  file) and do not depend on the machine.
- Exercise 1's x-step values (`1.0` for every ordinary day, one step of
  `15.0` across the fourteen-day gap) are arithmetic on a fixed,
  hand-written date range and are exact everywhere.
- Exercise 2's three January aggregates (`16.0`, `496.0`, `31.0`) are
  arithmetic on a fixed literal (`value = day number`, 1..90) and are
  exact everywhere.
- Exercise 3's true period (4 days), sampling interval (5 days) and the
  resulting spurious period (20 days) are deterministic properties of a
  `numpy.cos` construction with no randomness anywhere.
- Exercise 4's centred-window offset (exactly `0` days) is structural.
  The trailing-window offset (`14` days, captured directly) is also
  deterministic given the fixed triangular-bump construction and the
  30-day window, but is asserted with a `10`-`20` day tolerance rather
  than the single captured integer, because a slightly different bump
  shape or window size would still legitimately land inside "roughly
  half the window" without landing on exactly 14.
- Exercise 5's row counts (19 for the missing-row series, 20 for the
  explicit-NaN series) and the exact position of the NaN
  (`MISSING_DAY_POSITION = 10`) are structural.
- Exercise 6's constant-percentage-growth log-difference standard
  deviation was measured at `3.04e-16` (floating-point noise around
  zero, well under the asserted `1e-9` threshold) and the linear-growth
  series' at `9.53e-3` (over the asserted `1e-3` threshold). The 1e-16
  figure is a floating-point-arithmetic artifact of this specific
  computation order and is not asserted on directly; only the "under
  1e-9" / "over 1e-3" thresholds are.
- Exercise 7's structural facts — 2024 has 366 days including Feb 29,
  2025 has 365, Dec 31's ordinal day-of-year is 366 in 2024 and 365 in
  2025 — are calendar facts, exact on any machine.
- Exercise 8's Axes-and-line counts are structural (one Axes and one
  line per column of a fixed 6-column frame).
- Exercise 9's hour counts (23 for 2024-03-10, 25 for 2024-11-03, 24 for
  an ordinary day) are determined by the `America/New_York` timezone's
  published DST transition rules for 2024 and are exact wherever the
  installed tz database matches the IANA release these rules come from
  (see "Version-specific" below).
- `17 checks, 0 failure(s)` and exit 0 from `tests/run_tests.sh`.

## Version-specific, checked directly rather than assumed

- Exercise 9's specific transition dates (2024-03-10 for spring forward,
  2024-11-03 for fall back) are properties of the `America/New_York`
  zone's 2024 DST rules as published in the IANA tz database installed
  on this machine, via Python's `zoneinfo` (no separate `tzdata` package
  was needed here — macOS ships a system tz database and pandas 3.0.5
  found it automatically). A machine with an older tz database release
  would still show a spring-forward and a fall-back transition in 2024
  on these same two dates, because the US DST rule itself has been
  stable since 2007; the requirements/README documents `pip install
  tzdata` as a fallback for platforms with no system database at all
  (chiefly a minimal Windows install).
- No `MatplotlibDeprecationWarning` or similar was observed anywhere in
  this lab's captured output on matplotlib 3.11.1 — every plotting call
  used here (`ax.plot`, `plt.subplots`) is long-stable API with no
  deprecated keyword arguments.

## Machine-dependent

- Wall-clock timings inside pytest's own summary lines (`in 0.05s`, `in
  0.01s`) will differ on any other machine and are not asserted on
  anywhere in this lab.
- The `.venv` path embedded in pytest's own `rootdir:` and platform
  banner lines has been sanitized to `<repo>` in these captures; on a
  fresh checkout it will show that checkout's own absolute path instead.

## Nothing in this lab is sampled or non-reproducible

Unlike Day 129's unseeded-bootstrap exercise, every exercise in this lab
is built from a deterministic literal or a deterministic closed-form
signal (a fixed date range, a fixed cosine, a fixed triangular bump, a
fixed compounding-growth formula). Re-running `examples/` on the same
pin set reproduces every asserted number exactly, with no exceptions.
