# Day 127 lab — Charts That Answer the Question

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Why We Visualize, and Choosing the Right Chart
- **Day number:** 127 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-127-why-we-visualize-and-choosing-the
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-127-why-we-visualize-and-choosing-the` when the site is running.
<!-- generated-links:end -->

## Purpose

Nine numbered exercises on the one hard problem in a visualisation lab:
**"looks better" is not testable, so test the things that genuinely are.**

The through-line is that **a chart is an argument, and the encoding is
the claim**. The same numbers drawn two ways answer different questions,
and one of the two usually answers none. Every exercise here turns some
part of that into a number:

- Encoding a value as a circle's *radius* squares every ratio in the
  chart. Measured analytically and again by counting pixels: 5,156 px
  against 20,368 px for a doubled value, a ratio of 3.95 where the data
  ratio is 2.
- The Cleveland-McGill accuracy ordering, used as a decision function
  rather than quoted as a slogan.
- A chart-choice function that recommends a **table** below a stated
  number of values and never recommends a pie chart for anything.
- Matplotlib's own default red and green — the pass/fail reflex — start
  119.77 apart in CIELAB and end **7.31** apart under a published
  deuteranopia transform. Seaborn's colourblind-safe pair keeps 100.7%
  of its separation through the identical transform.
- An ordered variable on a sequential palette has rank correlation
  **+1.00** between its order and the palette's luminance; on a
  categorical palette, **-0.20**.
- Sorting turns 19 reader comparisons into 1 without changing the answer.
- The same eight numbers drawn with and without furniture: **37%** of the
  decorated chart's ink is data, against **93%** of the plain one's.
- 10,000 one-pixel points paint only **6,349** distinct pixels — 3,651
  points, 36.5% of the data, changed nothing — and the opaque image
  contains exactly **two** grey levels. Alpha blending and hexbin
  recover what opaque compositing threw away.

## Learning objectives

By the end of this lab you will be able to:

- Prove that radius-scaled size encoding squares every ratio in a chart,
  both analytically and by measuring rendered pixels, and fix it by
  scaling area instead.
- Use the Cleveland-McGill ordering as a decision procedure: given a data
  type and the reader's task, name the most accurately-judged channel
  that is still honest.
- Justify, in a case table, why a nominal variable belongs on hue and an
  ordinal one never does.
- Recommend a chart from a question, a value count and a list of data
  types — including recommending a table, and never a pie.
- Measure how much of a colour pair's separation survives a published
  deuteranopia transform, and state precisely what a simulation does and
  does not license you to claim.
- Measure, as a rank correlation, the order a categorical palette
  destroys and a sequential palette preserves.
- Express sorting as a saving in reader effort rather than a matter of
  neatness.
- Compute a data-ink ratio from a rendered PNG and show it moves when
  non-data ink is removed.
- Measure overplotting as painted pixels against point count, show that
  an opaque scatter carries exactly two grey levels, and demonstrate two
  renderings that recover the density.
- Render everything headlessly through matplotlib's `Agg` backend into a
  temporary directory, leaving no image behind.

## Prerequisites

- **Day 116** — descriptive statistics that do not lie, including
  Anscombe's quartet. This lab does not re-tell it; it assumes you
  already know why identical summary statistics do not imply identical
  data.
- **Day 104** — NumPy arrays and vectorised thinking. Every pixel count
  here is a NumPy comparison over an image array.
- **Days 120-126** — pandas. Not imported by this lab, but the analysis
  habits carry: measure, reconcile, and never assert what you did not run.
- A working `python3` on your `PATH` to create the lab's virtual
  environment.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given the pinned versions. Agg is a pure software rasteriser and needs no display, so no X11 or Wayland session is required |
| Windows | Use WSL and follow the Linux path. `mktemp -d` is used inside `tests/run_tests.sh`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The largest thing this lab builds is a 10,000-point array and a
400×400 pixel image. No GPU — matplotlib's `Agg` backend is CPU-only
software rendering by design. No network beyond the one-time install. No
display, no window server, no `DISPLAY` variable.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | Runs everything; standard library `venv` builds the lab's environment |
| `matplotlib` | 3.11.1 exactly | 3.11.1 | Every render, and the `viridis` and `tab10` palettes exercise 5 measures |
| `seaborn` | 0.13.2 exactly | 0.13.2 | `color_palette("colorblind")` — the safe pair exercise 4 measures |
| `numpy` | 2.5.2 | 2.5.2 | The point cloud, and every pixel count (images are read as arrays) |
| `pillow` | 12.3.0 | 12.3.0 | Reads rendered PNGs back off disk so their pixels can be counted |
| `pandas` | 3.0.5 | 3.0.5 | Not imported here; pinned because seaborn requires it |
| `pytest` | 9.1.1 | 9.1.1 | The test harness, plus its `tmp_path`-style fixtures |
| `bash` | 3.2 | 3.2.57 | The outer test harness |

`math`, `pathlib` and `tempfile` are Python standard library — already
present, no install, no cost.

Check your Python in one line: `python3 --version`.

## Free and open-source options

Everything here is free, and there is no paid tier of anything in this
lab, no account, no key and no signup.

- **matplotlib** (a BSD-style licence derived from the PSF licence),
  **seaborn** (BSD 3-Clause), **NumPy** (BSD 3-Clause), **pandas** (BSD
  3-Clause) and **pytest** (MIT) are fully open source.
- **Pillow** (MIT-CMU) is the maintained fork of the Python Imaging
  Library, also fully open source.
- **Vega-Lite** (BSD 3-Clause) and **plotly.py** (MIT) are described in
  the lesson's Tools section from their public documentation. Neither is
  installed here and **no output attributed to either is reproduced
  anywhere in this lab.**

## Installation

From this directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import matplotlib, seaborn; print(matplotlib.__version__, seaborn.__version__)"
```

That last line should print `3.11.1 0.13.2`. One network connection, ever
— this install. Everything after it runs offline.

## File structure

```
day-127-why-we-visualize-and-choosing-the/
├── README.md                  this file
├── metadata.yml               how the lab was actually run
├── security.md                what this lab does to your machine
├── troubleshooting.md         grouped by the message you actually see
├── requirements/
│   ├── README.md              what each package is for, and what it costs
│   └── requirements.txt       exact pins
├── starter/                   YOUR work
│   ├── 00_brief.md            the exercise-by-exercise brief
│   ├── charts.py              decision functions (read, do not edit)
│   ├── encoding.py            geometry and colour maths (read, do not edit)
│   ├── palettes.py            the swatches (read, do not edit)
│   ├── render.py              drawing and measuring (read, do not edit)
│   ├── conftest.py            fixtures: points, png_dir
│   └── test_charts.py         nine exercises, all skipped until you write them
├── examples/                  the worked answer key, same four modules
│   └── test_charts.py         every exercise solved, with the reasoning
├── expected-output/
│   ├── FIELDS.md              what is exact, what may differ, and why
│   ├── measurements.txt       every number this lab asserts, in one place
│   ├── examples-run.txt       captured `pytest examples -v`
│   ├── starter-run.txt        captured `pytest starter -q -rs`
│   └── test-run.txt           captured `bash tests/run_tests.sh`
└── tests/
    └── run_tests.sh           the outer harness — 19 checks
```

## How to run

Three commands, in this order:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
bash tests/run_tests.sh
```

**Run `pytest examples` and `pytest starter` as two separate commands.**
Never `pytest examples starter`. Both directories define modules with the
same six names, and pytest refuses to collect the second with an
`import file mismatch` error. The harness checks that this is what
happens, so the warning is measured rather than folklore.

Work through `starter/test_charts.py` top to bottom, following
`starter/00_brief.md`. Check one exercise at a time:

```bash
.venv/bin/pytest starter -v -k test_4
```

## What the commands do

| Command | What it does |
| --- | --- |
| `python3 -m venv .venv` | Creates the lab-local environment. Nothing is installed system-wide |
| `.venv/bin/pip install -r requirements/requirements.txt` | Installs the six pinned packages. The only network access this lab ever makes |
| `.venv/bin/pytest examples` | Runs the worked answer key: 17 tests, all passing |
| `.venv/bin/pytest starter` | Runs your suite. 17 skipped on an untouched checkout |
| `.venv/bin/pytest starter -v -k test_4` | Runs one exercise at a time |
| `bash tests/run_tests.sh` | The outer harness: 19 checks, including proving the suite can genuinely fail |

## Expected output

`bash tests/run_tests.sh` ends with:

```
-------------------------------------------------------------
19 checks, 0 failure(s)
```

and exits 0. `pytest examples` reports `17 passed`. `pytest starter` on
an untouched checkout reports `17 skipped`.

The full captured runs are in `expected-output/`, and every number the
lab asserts is printed together in `expected-output/measurements.txt`.
Read `expected-output/FIELDS.md` before comparing your run against them:
it says exactly which values are arithmetic (identical everywhere), which
are rendered pixel counts (identical on this matplotlib version), and
which are machine-dependent.

## Validation steps

1. `bash tests/run_tests.sh; echo "exit=$?"` — expect `19 checks, 0
   failure(s)` and `exit=0`. Capture the script's **own** exit status;
   piping it into `tail` and reading `$?` reports `tail`'s status and
   will hide a real failure.
2. `.venv/bin/pytest examples -q` — expect `17 passed`.
3. `.venv/bin/pytest starter -q` — expect `17 skipped` before you start,
   and `17 passed` when you are finished.
4. Confirm nothing was left behind:
   `find . -name '.venv' -prune -o -name '*.png' -print` should print
   nothing at all.
5. Compare your numbers against `expected-output/measurements.txt`. If a
   pixel count differs by a few percent, check your matplotlib version
   first — the harness checks the pin for you.

## Tests

`tests/run_tests.sh` runs 19 checks in nine sections:

1. The installed matplotlib and seaborn match the pins exactly.
2. Importing `render.py` really selects the `Agg` backend, and nothing
   calls `plt.show()` — either would hang a headless run.
3. `examples/` exits 0 and reports 17 passed.
4. `starter/` on an untouched checkout exits 0 and reports 17 skipped.
5. `pytest examples starter` in one invocation does **not** exit 0, and
   reports an `import file mismatch` rather than a quiet partial run.
6. The suite can genuinely fail: the harness copies the solved suite to a
   scratch directory, confirms green, breaks exercise 8's exact
   `luminance levels == 2` assertion, confirms a non-zero exit and a
   printed failure, restores it, and confirms green again.
7. No URL appears anywhere in `examples/` or `starter/`.
8. No `.png`, `.jpg`, `.svg` or `.pdf` is left anywhere under the lab.
9. No `__pycache__` or `.pytest_cache` is left behind by this run.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: reset your work
```

The harness cleans up after itself both before and after every run, so
these are for tidying a session you interrupted rather than a normal
finish. Every rendered image already goes to a temporary directory
outside the lab that its fixture removes.

## Troubleshooting

See `troubleshooting.md`, grouped by the message you actually see. The
three you are most likely to hit:

- `ModuleNotFoundError: No module named 'matplotlib'` — the dependencies
  live in the lab's own `.venv`, not on your system Python.
- `import file mismatch` — you ran `pytest examples starter` in one
  invocation. Run them separately; this is expected, not a bug.
- A pixel count a few percent off — check your matplotlib version against
  the pin.

## Security notes

See `security.md`. In short: one network connection ever (the install),
no `sudo`, no port, no credential, and every file this lab writes goes
either into `.venv` or into a temporary directory outside the lab that is
deleted automatically.

## Extension exercises

1. **Move the boundary and watch the tests move.** Change
   `charts.TABLE_MAX_VALUES` from 5 to 8 and re-run. Which assertions
   break? Now argue for the number you would actually use with your own
   readers, and update the exercise 9 comment to match.
2. **Add a second deficiency.** Look up the protanopia matrix from the
   same published source and add `simulate_protanopia`. Which pairs that
   survive deuteranopia collapse under protanopia, and which survive
   both?
3. **Measure your own palette.** Replace `PAL.SAFE_BLUE` and
   `PAL.SAFE_ORANGE` with your organisation's brand colours and run
   exercise 4 against them. Report the retained fraction honestly, even
   if the answer is inconvenient.
4. **Extend `choose_chart` to the map case.** `best_encoding` already
   returns `area` for `magnitude_on_map`. Add a `question_kind` for
   geographic magnitude, and make sure your recommendation scales bubbles
   by area rather than radius — exercise 1 says why.
5. **Push the overplotting further.** Re-run exercise 8 with 100,000
   points. At what point does alpha blending saturate, and how does the
   number of distinct grey levels behave once it does?
6. **Small multiples for real.** `choose_chart` recommends
   `small_multiples_line` above eight series. Render both — one tangled
   panel and eight small ones — and find a measurable difference between
   them. This one is genuinely hard, and finding that you cannot measure
   it is a legitimate result to report.

## Navigation

- The lesson for this day is linked at the top of this file.
- Previous lab: Day 126 — A Pipeline You Can Re-run.
- Next lab: Day 128, which takes matplotlib's mechanics seriously. This
  day chose the chart; that day draws it properly.
