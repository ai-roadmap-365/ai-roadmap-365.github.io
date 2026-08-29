# What in these captures is exact, and what may differ

Captured from a real run on 2026-08-20, in this lab's own `.venv`, on
matplotlib 3.11.1, seaborn 0.13.2, pandas 3.0.5, NumPy 2.5.2, pytest
9.1.1, Python 3.14.0, macOS (arm64). scipy is not installed on this
machine, which is why every interval in this lab is a hand-written
percentile bootstrap rather than a call into `scipy.stats`.

Four files sit here:

| File | What it is |
| --- | --- |
| `test-run.txt` | The full `bash tests/run_tests.sh` output |
| `examples-run.txt` | `pytest examples -q` |
| `starter-run.txt` | `pytest starter -q` on an untouched checkout |
| `report-sample.md` | The Markdown the generator actually produced, captured verbatim |

`report-sample.md` links to `figures/*.png` that are **not** in this
directory. That is deliberate: the harness asserts no image file exists
anywhere inside the lab, because the lab renders into a temporary
directory and deletes it. Render it yourself to see the figures.

## Exact everywhere, on any correct install

- `test-run.txt` ends with `42 checks, 0 failure(s)` and exit 0.
  `examples-run.txt` ends with `9 passed`; `starter-run.txt` ends with
  `9 skipped`. All three counts are structural — 9 test functions per
  file, 42 `check` calls in the harness — and do not depend on the
  machine.
- **12 candidate figures, 5 survivors, 7 discarded.** These are
  hand-authored in `analysis.candidate_figures()`, not sampled. The
  survival rate is 41.7%.
- **8 of 192 rows (4.2%) have no revenue, and 100% of them are partner
  rows.** `MISSING_RATE * 192` rounds to 8, and `data.monthly_sales`
  draws the blanked rows only from partner positions, so the 100% is by
  construction and exact.
- The partner channel's median region-month is **45%** of the direct
  median. `PARTNER_SHARE` is 0.45 and the multiplicative noise is
  symmetric around 1.0, so this holds to the printed precision.
- `East month 18 as a multiple of the region median` carries **no
  interval**, and the report says why: one observation has no sampling
  interval. That branch of `Estimate` is exercised by the real report,
  not only by a test.
- The accessibility check reports **exactly four** problems on
  `analysis.draw_inaccessible`: an unlabelled x axis, an unlabelled y
  axis, `#ff0000` and `#008000`. Both colours are literal matplotlib
  named colours, so the hex values are fixed.

## Deterministic given the seed, and exact on this NumPy

Everything below comes from `numpy.random.default_rng(133)` in
`data.monthly_sales`, or from a bootstrap seeded at 133. `default_rng`'s
bit generator is part of NumPy's stable public API, so these should
reproduce identically on any NumPy 2.x; only the values on NumPy 2.5.2
were directly verified here.

| Quantity | Captured value |
| --- | --- |
| Data fingerprint (sha256, first 12) | `2ba806a5cbf5` |
| Share of rows with missing revenue | 4.2% (95% interval 1.6% to 7.3%) |
| Median partner region-month revenue | 16468 USD (95% interval 15826 to 17001) |
| Fitted slope, revenue per extra order | 174 USD |
| R-squared of the straight-line fit | 97.4% |
| Mean revenue per order | 180.1 USD (95% interval 178.4 to 181.8) |
| Region change across month 13 | North +12.5%, South +1.7%, East +47.5%, West -8.6% |
| East change with month 18 removed | +8.0% |
| West change, 95% bootstrap interval | -11.6% to -5.1% |
| West change on the perturbed frame | -54.3% |
| East month 18, as a multiple of the region median | 3.3x (neighbouring months 1.05x) |

## Measured on this machine only

- **Figure PNG bytes are byte-identical across two runs.** Exercise 6 and
  harness check `figure_bytes_identical_same_machine` both assert this,
  and both compare **two runs on the same machine within one test
  session** — which is where the guarantee actually holds. PNG bytes from
  matplotlib depend on the font files installed and on the FreeType build
  that rasterises them, so two different machines can legitimately produce
  different bytes from identical code. Nothing here promises cross-machine
  byte-identity for images, and you should not build a pipeline that
  depends on it.
- **Markdown byte-identity is the stronger claim**, and it is the one the
  lesson leans on. The rendered Markdown contains no clock reading, no
  hostname and no unseeded random number — provenance is a hash of the
  input data, not a note about the run — so two runs over the same input
  produce the same bytes. Harness check
  `no_clock_reading_in_output` asserts the absence directly.

## Honesty notes from this run

**One. The claim heuristic is crude in both directions, and the lab
asserts both.** `report.carries_claim` passes
`"revenue doubled in every region"` on data where revenue halved, because
it cannot read the data. It also *refuses*
`"revenue tripled in all four regions"`, which is a perfectly good claim
written with a word that is not on `CLAIM_WORDS`. The first limit was
expected; the second was found by writing the test and watching it fail,
and it is kept rather than patched away by adding "tripled" to the list,
because the false negative is the more instructive half. What the check
actually buys is narrow and worth having: it makes the **absence** of a
claim impossible to ship by accident. It is not, and cannot be, a judge
of whether a claim is true.

**Two. Six observations per side is a thin bootstrap, and the report says
so.** The West's -8.6% is a comparison of two six-month windows, and its
interval (-11.6% to -5.1%) is correspondingly wide. That width is
reported in the document and named in the report's own caveats rather
than being quietly dropped, which is the whole point of exercise 5.

**Three. The step change is real in this data because it was put there.**
`data.py` scales the West by `WEST_PRICING_FACTOR` from month 13. The
report states plainly in its caveats that this is observational data and
that an association in time is not a causal claim — the generated
document argues honestly about data whose truth we happen to know, which
is the only way to check that the argument is honest.

**Four. The East's +47.5% is one month.** The generated report quotes the
figure and then immediately gives the number with the single month-18
observation removed (+8.0%), computed from the same frame. Quoting the
inflated figure alone would have been exactly the Day 132 failure this
week is about, so `analyse_segments` computes both.

**Five. pandas' Styler could not be run here, and the brief was wrong
about that.** The day brief this lab was written from said pandas Styler
was installed and could be used. Measured directly on this machine:

```
>>> df.style
AttributeError: The '.style' accessor requires jinja2
```

pandas 3.0.5 is installed, but `.style` is an optional accessor that
imports jinja2 to render its templates, and jinja2 is not in this
environment. So the lesson describes Styler from the pandas documentation
and says plainly that no Styler output is reproduced. Nothing in this lab
uses it.

**Six. Nothing else in this lab is attributed to a tool that is not
installed either.** Jupyter, nbconvert, Quarto and scipy are all absent
from this machine — `jupyter` and `quarto` are not on PATH and
`import nbconvert`, `import nbformat`, `import IPython` and
`import scipy` all fail. Every one of them is described in the lesson
from public documentation only, and no output is reproduced from any of
them anywhere in this lab or its lesson.
