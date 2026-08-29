# Expected output — what is stable and what may differ

Captured from a real run on 2026-08-20: macOS 26.5.2 (Apple Silicon,
arm64), Python 3.14.0, matplotlib 3.11.1, seaborn 0.13.2, NumPy 2.5.2,
Pillow 12.3.0, pytest 9.1.1, bash 3.2.57.

Four files here, all captured, none written by hand:

- `test-run.txt` — the full `bash tests/run_tests.sh` output.
- `examples-run.txt` — `pytest examples -v`.
- `starter-run.txt` — `pytest starter -q -rs` on an untouched checkout.
- `measurements.txt` — every number this lab asserts on, printed in one
  place so you can compare your run against the authoring machine's
  without reading test source.

## Exact everywhere — pure arithmetic, no rendering involved

- **The square law, analytically.** `encoded_area_ratio([50, 100],
  "radius")` is `4.0` and `encoded_area_ratio([50, 100], "area")` is
  `2.0`, exactly. These are `pi*r^2` on fixed literals.
- **Every CIE76 distance in section 4 of `measurements.txt`** — 119.7707
  and 7.3136 for the tab10 red/green pair, 115.7010 and 116.5144 for the
  seaborn colourblind pair. The inputs are fixed palette entries and the
  transform is a fixed matrix, so these are deterministic to full double
  precision on any IEEE-754 machine, given the same matplotlib and
  seaborn versions (see the version-specific note below).
- **Every luminance and both rank correlations in section 5** — viridis
  at `+1.0000`, tab10 at `-0.2000`.
- **The comparison counts in section 6** — 19 and 1. These are `n - 1`
  and `1`; they are arithmetic, not a benchmark.
- **Every `choose_chart` recommendation.** The function is a pure
  decision tree over its arguments.
- **`pytest examples` reporting `17 passed`, `pytest starter` reporting
  `17 skipped`, and the harness total `19 checks, 0 failure(s)`.**
- **`pytest examples starter` in ONE invocation failing to collect with
  `import file mismatch`.** Verified directly in this repository, not
  assumed. Every module in this lab — `encoding`, `charts`, `palettes`,
  `render`, `conftest`, `test_charts` — exists under both directories
  with the same name, which is exactly the situation pytest refuses. Run
  the two commands separately; the README documents them that way.

## Stable given the same matplotlib version — rendered, but deterministic

Everything below is a pixel count off a PNG produced by matplotlib's Agg
rasteriser. Agg is a software renderer with no GPU involvement and no
platform-dependent font fallback in these figures, so the same matplotlib
version produces byte-identical images and identical counts. A DIFFERENT
matplotlib version can move them slightly — a changed default line width,
a changed tick length, a changed rasterisation rule for a shape's edge —
which is why `requirements.txt` pins 3.11.1 and the harness checks that
the installed version matches the pin before it asserts anything.

- **Circle pixel areas: 5,156 / 20,368 / 10,262.** The two-percent gap
  against the ideal `pi*r^2` (5,026.5 and 20,106.2) is rasterisation:
  a circle's boundary does not fall on pixel edges, and with antialiasing
  switched off each boundary pixel is either wholly in or wholly out. The
  tests assert the RATIOS (4.0 and 2.0, `rel=0.02`), which survive that
  intact — not the raw counts.
- **Bar chart ink: 172,351 px decorated against 79,107 px plain, and
  data-ink ratios 0.3669 and 0.9344.** The tests allow `rel=0.05` on the
  totals and `abs=0.03` on the ratios, and additionally assert the
  direction and the size of the gap, which no plausible renderer change
  would reverse.
- **Scatter: 6,349 distinct pixels painted for 10,000 points**, with all
  10,000 inside the axes. The tests assert `rel=0.05` on the count and,
  more robustly, that the count is under 75% of the point count.
- **Grey levels: exactly 2 opaque, 9 at alpha 0.05, 244 for hexbin.** The
  `== 2` is asserted exactly and is a property of opaque compositing
  rather than of this renderer: an opaque black mark over an opaque black
  mark is the same black. The other two are asserted as inequalities
  (`>= 5`, `> 50`) precisely because they are not.

## Specific to these library versions

- **`PASS_FAIL_RED` and `PASS_FAIL_GREEN` are matplotlib `tab10`'s
  entries 3 and 2**; `SAFE_BLUE` and `SAFE_ORANGE` are seaborn's
  `colorblind` palette entries 0 and 1. If either library ever changed
  those palettes, every CIE76 number in section 4 would move. They are
  long-standing definitions in both libraries, but they are library data,
  not mathematical constants, which is why both packages are pinned.
- **The deuteranopia matrix is Machado, Oliveira and Fernandes (2009) at
  severity 1.0**, hard-coded in `encoding.py`. A different published
  matrix — Viénot, Brettel and Mollon (1999), say — would give different
  distances with the same qualitative result. The threshold constants in
  the tests (`COLLAPSE_THRESHOLD = 10.0`, `SURVIVAL_THRESHOLD = 25.0`)
  are deliberately loose so the conclusion does not depend on the third
  decimal place of a matrix coefficient.

## Machine-dependent — recorded here so it is never mistaken for universal

- **`platform darwin`, the interpreter path and `rootdir`** in
  `examples-run.txt`, sanitised to `<repo>` in place of the local
  filesystem path. Your run shows your own platform and path.
- **Wall-clock timing** in every pytest summary line (`in 0.31s`, and
  similar). Nothing in this lab asserts on a duration, ever.
- **The temporary directory names** (`d127-render-…`, `d127-scratch.…`)
  are generated per run by `tempfile` and `mktemp`. They appear nowhere
  in any assertion.

## What this lab deliberately does NOT assert

That any chart looks better than any other. Nothing here measures taste.
Everything it asserts is a count, a distance, a ratio or a correlation,
and where the underlying claim is a matter of judgement — where the
table/chart boundary sits, which channel suits which task — the judgement
is written down as a named constant or an in-test comment rather than
smuggled in as a fact.
