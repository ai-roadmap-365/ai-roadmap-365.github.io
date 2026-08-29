# Day 133 lab — A Report That Argues

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building an EDA Report
- **Day number:** 133 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-133-building-an-eda-report
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-133-building-an-eda-report` when the site is running.
<!-- generated-links:end -->

## Purpose

You build the checks that decide whether an exploratory analysis is fit
to be read, and you wire them into a report generator that **refuses** to
produce a report that fails them.

The generator in `report.py` takes a dataset and a list of candidate
figures, and writes a Markdown report with each figure embedded beside
its caption and its claim. It will not let you add a figure that has no
stated question. It will not accept a caption that is a label rather than
a claim. It renders the conclusion before the evidence, keeps the
discarded candidates as one-line null results, and produces byte-identical
Markdown on two runs over the same input.

Twelve candidate figures go into `analysis.candidate_figures()`. Five come
out. That ratio is the lesson: exploration is wide and private, a report
is narrow and public, and most of the charts you make should not survive
into the second one.

Nine numbered exercises, all headless via the `Agg` backend, all writing
into temporary directories that are deleted when the test finishes.

## Learning objectives

By the end of this lab you will be able to:

- Enforce, in code, that every figure in a report answers a stated
  question, and explain why a figure whose question you cannot state does
  not belong in the report.
- Distinguish a descriptive caption from a caption that carries a claim,
  implement the distinction as a check, and state honestly what such a
  check can and cannot detect.
- Generate a report whose prose numbers are interpolated from computed
  values, and prove that changing one input value changes the sentence.
- Detect an orphan figure — an image on disk the text never refers to.
- Require that every reported estimate carries a 95% interval or an
  explicit note saying why none is available, and catch a bare point
  estimate.
- Prove that two runs over the same input produce byte-identical Markdown,
  and say precisely what that guarantee does and does not cover for the
  figure files.
- Assert the reader's ordering: conclusion first, evidence beneath it,
  caveats and provenance where they can be found.
- Apply a "so what" filter to a set of candidate figures, measure the
  survival rate, and keep the discarded ones as null results.
- Turn a colourblind-safe palette and labelled axes into a build check
  that fails a red-against-green chart.

## Prerequisites

- Day 126 — the reproducible cleaning pipeline, whose idempotence this
  lab applies to prose rather than to data.
- Day 127 — chart choice and the perceptual ranking.
- Day 128 — matplotlib's Figure/Axes/Artist object model. The
  accessibility check here reads colours straight off the artists.
- Days 117 and 118 — sampling, standard error and intervals. Every
  interval in this lab is a percentile bootstrap.
- Day 132 — chart honesty, which this lab turns into a check that runs.
- Comfort with `pytest`, and a working `python3` on your PATH.

## Supported operating systems

- **macOS** (Intel or Apple Silicon) — the machine this lab was written
  and run on: macOS 26.5.2, arm64.
- **Linux** — any distribution with Python 3.11 or newer. Every command
  below is identical.
- **Windows** — use WSL2 and follow the Linux path. Native PowerShell
  works too if you substitute `.venv\Scripts\python.exe` for
  `.venv/bin/python3` and run the harness under Git Bash; the harness is
  a bash script and will not run in `cmd.exe`.

## Hardware requirements

Nothing special. The dataset is 192 rows and every figure is 600 by 350
pixels. The full harness runs in a few seconds on a laptop and needs well
under 500 MB of memory. No GPU, no display, no network after install.

## Required software

- Python 3.11 or newer (3.14.0 here).
- The pins in `requirements/requirements.txt`: matplotlib 3.11.1,
  seaborn 0.13.2, pandas 3.0.5, NumPy 2.5.2, pytest 9.1.1.
- `bash` for the test harness (3.2 or newer; macOS's system bash is fine).

Everything else the lab uses — `hashlib`, `re`, `shutil`, `tempfile`,
`dataclasses`, `pathlib` — is standard library.

## Free and open-source options

Every tool in this lab is free and open source, and there is no paid tier
anywhere in it. matplotlib and NumPy are BSD-licensed, seaborn and pandas
BSD-3-Clause, pytest MIT. Python itself is under the PSF licence.

The report generator writes plain Markdown on purpose. Markdown renders
in every code host, every static-site generator, every wiki and every
text editor, and it diffs line by line in Git, so a report that changed
its conclusion shows you which sentence changed. The commercial and
semi-commercial alternatives in this space — hosted notebook services,
BI dashboards with a report export — are discussed in the lesson; none of
them is needed here, and none is used.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-133-building-an-eda-report
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import matplotlib, pandas; print(matplotlib.__version__, pandas.__version__)"
```

That last line should print `3.11.1 3.0.5`. The `pip install` is the only
step that touches the network.

## File structure

```
day-133-building-an-eda-report/
├── README.md                 this file
├── metadata.yml              lab metadata and the literal result of the real run
├── security.md               what this lab does to your machine
├── troubleshooting.md        the failures you are most likely to hit
├── requirements/
│   ├── README.md             why the pins are exact
│   └── requirements.txt      matplotlib, seaborn, pandas, NumPy, pytest
├── starter/                  your work
│   ├── 00_brief.md           the nine exercises, explained
│   ├── conftest.py           Agg backend, fixtures, temporary directories
│   ├── data.py               the dataset, deterministic under default_rng(133)
│   ├── report.py             the report generator and its six checks
│   ├── analysis.py           twelve candidate figures; five survive
│   └── test_report.py        nine exercises, each currently a pytest.skip
├── examples/                 the reference answers — read after you try
│   ├── conftest.py           identical to starter/conftest.py
│   ├── data.py               identical to starter/data.py
│   ├── report.py             identical to starter/report.py
│   ├── analysis.py           identical to starter/analysis.py
│   └── test_report.py        the nine exercises, solved
├── tests/
│   └── run_tests.sh          the bash harness: 42 checks
└── expected-output/
    ├── FIELDS.md             what is exact, what may differ, and why
    ├── report-sample.md      the Markdown the generator really produced
    ├── examples-run.txt      pytest examples -q
    ├── starter-run.txt       pytest starter -q
    └── test-run.txt          bash tests/run_tests.sh
```

## How to run

Read `starter/00_brief.md` first, then `starter/report.py`. Then:

```bash
# your work, from the lab directory
.venv/bin/pytest starter -v

# the reference answers, once you have tried
.venv/bin/pytest examples -q

# everything, including the proof that the suite can fail
bash tests/run_tests.sh
```

**Run `pytest starter` and `pytest examples` as two separate commands.**
Both directories contain a module named `test_report.py`, and pytest
collects test modules by dotted name; a single `pytest examples starter`
aborts collection with an `import file mismatch`. Section 5 of the
harness runs that combined form on purpose and asserts it fails, so the
warning in this README is checked rather than merely stated.

## What the commands do

| Command | What happens |
| --- | --- |
| `.venv/bin/pytest starter -v` | Runs your nine exercises. On an untouched checkout all nine skip, and each skip message tells you what to assert |
| `.venv/bin/pytest examples -q` | Runs the reference answers. Should print `9 passed` |
| `bash tests/run_tests.sh` | The full harness: version pins, the generator's own rules driven directly from Python, both suites, the collision check, the fail-then-restore proof, and the cleanliness checks |
| `.venv/bin/python -c "import data, analysis; ..."` | Renders the report yourself — see "Extension exercises" |

Section 2 of the harness is the interesting one. It does not read source
code: it builds reports, renders them into temporary directories, and
reads the documents back to check that the generator really refuses what
it claims to refuse.

## Expected output

The final section of a green run:

```
7. Offline, and nothing left behind
  ok: no URLs inside examples/ or starter/
  ok: no image files anywhere inside the lab
  ok: no generated report.md left inside the lab
  ok: no __pycache__ or .pytest_cache left behind
  ok: no d133 temporary directory left in the system temp directory

-------------------------------------------------------------
42 checks, 0 failure(s)
```

The full capture is in `expected-output/test-run.txt`, and the Markdown
the generator actually produced is in `expected-output/report-sample.md`.
`expected-output/FIELDS.md` records which captured numbers are exact
everywhere and which are specific to this machine — notably that the
byte-identity of the figure PNGs is asserted only across two runs on one
machine, never across machines.

## Validation steps

1. `bash tests/run_tests.sh` prints `42 checks, 0 failure(s)` and exits 0
   (`echo $?` immediately after, with no pipe in between — a pipeline
   reports the *last* command's status and will hide a real failure).
2. `.venv/bin/pytest examples -q` prints `9 passed`.
3. `.venv/bin/pytest starter -q` prints `9 skipped` before you start, and
   `9 passed` when you are done.
4. Open `expected-output/report-sample.md` and read it as a reader would.
   Every claim in the conclusion is a caption from a figure below it.
5. Render the report yourself and confirm that deleting one figure's
   image and re-checking makes `orphan_figures` complain.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints `N checks,
M failure(s)`, exits 0 only when `M` is zero, and covers:

1. the installed versions against `requirements/requirements.txt`;
2. the generator's own rules, driven directly: it refuses a question-less
   figure and a label caption, keeps 5 of 12 candidates, renders
   byte-identical Markdown, moves its numbers when the input moves,
   detects an orphan, catches a bare point estimate, orders the sections
   for the reader, and fails a red-against-green chart with four named
   problems;
3. `examples/` passing in full;
4. `starter/` skipping in full on an untouched checkout;
5. the `pytest examples starter` collision, run and asserted;
6. **the proof that the suite can fail** — the harness copies the solved
   suite into a scratch directory, confirms 9 passed, rewrites
   `assert len(kept) == 5` to `== 99`, confirms a non-zero exit and a
   printed failure, restores the file, and confirms 9 passed again;
7. no URLs in the exercise code, and no image, no generated `report.md`,
   no `__pycache__` and no stray temporary directory left behind.

## Cleanup

The harness cleans up after itself, before and after every run. To reset
completely:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: throws away your work and restores the skips
```

Nothing else exists to remove. Every report this lab renders goes into a
`tempfile.TemporaryDirectory` that is deleted when the test that made it
finishes, which is why the harness can assert that no image file exists
anywhere inside the lab.

## Troubleshooting

`troubleshooting.md` covers the failures in detail. The three most common:

- **`pytest: command not found`** — you have not created the `.venv`, or
  you are calling bare `pytest` instead of `.venv/bin/pytest`. The harness
  also accepts `PYTEST=/path/to/pytest bash tests/run_tests.sh`.
- **`import file mismatch`** — you ran `pytest examples starter` in one
  command. Run them as two.
- **A window tries to open, or matplotlib complains about a display** —
  something imported `pyplot` before `matplotlib.use("Agg")` ran. The
  `conftest.py` in each directory sets the backend first; if you added an
  import above it, move it back down.

## Security notes

`security.md` has the full account. In short: one network connection ever
(the `pip install`), no port bound, no `sudo`, no credential, no API key,
nothing written outside this lab's own directory and the temporary
directories it deletes. The dataset is synthetic and generated in
`data.py` — no real person's data is anywhere in this lab.

## Extension exercises

1. **Render the report and read it.** From `examples/`:
   `python -c "import data, analysis; f=data.monthly_sales(); print(analysis.build_report(f).render('out', f))"`.
   Open `out/report.md`. Then delete `out/` — the lab's own runs never
   leave it behind, and neither should yours.
2. **Break the claim rule.** Change one caption in `analysis.py` to a bare
   label and watch `build_report` raise before a single figure is drawn.
3. **Sharpen the claim heuristic.** Add "tripled" and "trebled" to
   `CLAIM_WORDS`, then find another real claim it still refuses. You will
   not run out. That is the honest ceiling on this kind of check.
4. **Promote a discarded candidate.** Give one of the seven a question, a
   `draw` and an `analyse`, and watch the survival rate move from 5/12 to
   6/12 — and the null-results section shrink by exactly one line.
5. **Add a check of your own.** For example: no figure may be referenced
   before the conclusion mentions its number, or no caption may exceed 200
   characters. Write the check, then write the test that proves it fails.
6. **Point the generator at your own data.** `build_report` takes a
   DataFrame. The candidates are yours to rewrite; the six checks are not
   meant to change.

## Navigation

- **Previous day:** Day 132 — Visual Storytelling and Chart Honesty
  (`labs/sections/math-statistics-and-data/day-132-visual-storytelling-and-chart-honesty/`).
- **Next day:** Day 134, opening Week 20
  (`labs/sections/math-statistics-and-data/`).
- **Week 19 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-19/`), where you
  produce a narrated exploratory report on a dataset of your own. This
  lab is the method and the machinery; the project is your analysis.
