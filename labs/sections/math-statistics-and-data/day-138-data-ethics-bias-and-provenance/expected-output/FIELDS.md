# What in the captured output is exact, and what is not

Every file in this directory was captured from a real run of this lab on
2026-08-20, on macOS 26.5.2 (Apple Silicon, arm64), with Python 3.14.0,
NumPy 2.5.2, pandas 3.0.5 and pytest 9.1.1 in a lab-local `.venv` created
by the setup commands in `metadata.yml`. Nothing here was typed by hand or
adjusted afterwards, other than replacing absolute home paths with
`<repo>`.

This lab has an unusually high proportion of **exact** values, because all
of its data is constructed rather than collected. That is the point of
making it synthetic: a number that comes out of a seeded generator is a
property of the code, not of the machine.

## Exact and identical on every machine

These come from `numpy.random.default_rng(seed)`, which is a
counter-based generator with a documented, stable stream, or from
integer-exact arithmetic on a hand-built table. They will be
bit-for-bit identical anywhere NumPy 2.x runs.

| Value | Captured | Why it is exact |
| --- | --- | --- |
| Exercise 1 bias at n = 500 / 5,000 / 50,000 | `5.9459`, `5.9384`, `5.9397` | Seeded draws, fixed replicate count |
| Exercise 1 standard deviations | `0.06025`, `0.01796`, `0.00524` | Same |
| Exercise 1 in-sample RMSE | `1.1671`, `1.1593`, `1.1649` | Same |
| Exercise 2 total variation distance | `0.089583` | Pure arithmetic on fixture counts — no randomness at all |
| Exercise 2 west representation ratio | `0.104167` | Same |
| Exercise 3 proxy correlation | `0.9253` | Seeded draws |
| Exercise 3 group B share by proxy / by target | `0.0400` / `0.2500` | Same |
| Exercise 4 pooled slope, per-group slopes | `1.9785`, `-0.9870`, `-0.9991` | Same |
| Exercise 5 base rates | `0.6600`, `0.3400` | Integer-exact hand-built table, no randomness |
| Exercise 5 all nine fairness gaps | see below | Same |
| Exercise 6 unique row counts | `2723` exact, `13` generalised | Seeded draws |
| Exercise 7 rows suppressed / kept | `794` / `4206` | Same |
| Exercise 8 missing-field list | eight names, in contract order | No randomness |
| Exercise 9 composition shift | `0.2500` | Deterministic label assignment by row index |

### The three fairness metrics from exercise 5, in full

Reported for both groups under all three policies. Every one of these is
exact arithmetic on the integer-exact population in
`ethics.FAIRNESS_CELLS`; none of it is sampled.

| Policy | Selection rate A / B | True-positive rate A / B | Precision A / B |
| --- | --- | --- | --- |
| One threshold at 0.5 | 0.8500 / 0.3500 | 0.9470 / 0.6324 | 0.7353 / 0.6143 |
| Equalise selection rate | 0.6000 / 0.6000 | 0.7424 / 0.8529 | 0.8167 / 0.4833 |
| Equalise true-positive rate | 0.6560 / 0.5400 | 0.8000 / 0.8000 | 0.8049 / 0.5037 |

Gaps: single threshold 0.5000 / 0.3146 / 0.1210; demographic parity
0.0000 / 0.1105 / 0.3333; equal opportunity 0.1160 / 0.0000 / 0.3012.

## Version-specific

- The **version banner** in section 1 of `test-run.txt` prints whatever is
  installed. It will differ if you install different pins, and the harness
  will then fail its first check on purpose rather than proceed quietly.
- `numpy.random.default_rng` streams are stable across NumPy 2.x by
  NumPy's own documented policy, but a **NumPy 1.x** environment predates
  `default_rng`'s current guarantees for some methods. Every numeric value
  in the table above should be treated as pinned to NumPy 2.5.2, which is
  what `requirements/requirements.txt` installs.
- The pytest header line in `starter-run.txt` names the platform, the
  Python version and the pytest and pluggy versions. All four are
  machine-specific.

## Machine-dependent

- **Paths.** `starter-run.txt` shows a `rootdir` and an interpreter path.
  Both were rewritten to `<repo>` on capture; yours will be your own
  checkout.
- **Timings.** `9 passed in 0.18s` is one machine on one day. Nothing in
  the harness asserts on a duration, and nothing should.
- **Ordering of the `key=value` behaviour lines** follows insertion order
  in the behaviour script, which is stable, but the harness looks each
  value up by name rather than by position.

## Not captured here, and why

No output from **Fairlearn** or **AIF360** appears anywhere in this lab or
in the lesson. Neither is installed in this repository's authoring
environment, neither was run, and both are described from their published
documentation only. If you install one yourself, its numbers are yours,
not this lab's.
