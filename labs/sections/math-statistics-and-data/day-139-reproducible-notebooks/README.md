# Day 139 lab — Notebooks That Reproduce

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Reproducible Notebooks
- **Day number:** 139 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-139-reproducible-notebooks
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-139-reproducible-notebooks` when the site is running.
<!-- generated-links:end -->

## Purpose

You build and execute real Jupyter notebooks entirely in memory —
`nbformat` builds them, `nbclient` runs them against a real kernel, and
your assertions read the resulting JSON — and use that machinery to
prove nine claims about what makes a notebook a document you can trust:
that cell order matters even though the file looks the same either way,
that a deleted cell's variable can outlive its own deletion in a live
kernel, that `nbclient` turns "does this still work?" into something CI
can check, and that a notebook is a poor home for logic anything else
depends on.

Every notebook this lab touches lives only in memory. None is ever
written to disk, which is also why the harness can assert that no
stray `.ipynb` file exists anywhere in this lab when it is done.

## Learning objectives

By the end of this lab you will be able to:

- Execute the same three notebook cells in two different orders and get
  two different, non-error answers, with `execution_count` as the only
  trace of what actually happened.
- Explain why a kernel that has not been restarted can make a notebook
  run for you and fail for everyone else, and reproduce that failure on
  purpose.
- Use `nbclient` to fail a CI-style check on a broken notebook, with the
  failing cell named in the error.
- Show precisely what makes two runs of an unchanged notebook differ as
  committed JSON, and what stripping outputs actually removes.
- Build a parameterised notebook variant by hand, the way `papermill`
  does it, without installing `papermill`.
- Convert an executed notebook to Markdown with `nbconvert` and confirm
  the artifact carries both its prose and its computed values.
- State, and prove with a real `pytest` run, why logic that other code
  depends on belongs in an imported module and not in a cell.
- Record a notebook's own Python and package versions and show that a
  changed pin changes the record.

## Prerequisites

- Day 126 — the reproducible cleaning pipeline: idempotence, determinism
  and a manifest of hashes, all applied here to a document instead of to
  data.
- Day 133 — why nothing in this lab's dependency stack is installed in
  the shared authoring environment, and why that is a deliberate,
  lab-local choice rather than an oversight.
- Comfort with `pytest`, and a working `python3` (3.11 or newer) on your
  PATH.

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

Nothing special. Every notebook in this lab has two to four cells and
runs in well under a second once its kernel is up; the first kernel
start in a session is the slowest step, typically one to two seconds.
The full harness runs in under fifteen seconds on a laptop, needs no
GPU, no display and no network after install.

## Required software

- Python 3.11 or newer (3.14.0 here).
- The pins in `requirements/requirements.txt`: `nbformat` 5.11.1,
  `nbclient` 0.11.0, `nbconvert` 7.17.1, `ipykernel` 7.3.0, `pytest`
  9.1.1.
- `bash` for the test harness (3.2 or newer; macOS's system bash is
  fine).

## Free and open-source options

Every tool this lab installs is free and open source under a BSD or
similar permissive licence: `nbformat`, `nbclient` and `nbconvert` are
Project Jupyter's own reference implementations (BSD-3-Clause),
`ipykernel` is the reference Python kernel (BSD-3-Clause), and `pytest`
is MIT-licensed. There is no paid tier anywhere in this lab. Jupyter
Lab itself, discussed in the lesson but not run here, is equally free;
so is Quarto. Google Colab is discussed in the lesson with its free and
paid tiers stated plainly — nothing in this lab depends on it.

## Installation

```bash
cd labs/sections/math-statistics-and-data/day-139-reproducible-notebooks
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import nbformat, nbclient, nbconvert; print(nbformat.__version__, nbclient.__version__, nbconvert.__version__)"
```

That last line should print `5.11.1 0.11.0 7.17.1`. The `pip install` is
the only step that touches the network.

## File structure

```
day-139-reproducible-notebooks/
├── README.md                 this file
├── metadata.yml               lab metadata and the literal result of the real run
├── security.md                what this lab does to your machine
├── troubleshooting.md         the failures you are most likely to hit
├── requirements/
│   ├── README.md              why the pins are exact
│   └── requirements.txt       nbformat, nbclient, nbconvert, ipykernel, pytest
├── starter/                   your work
│   ├── 00_brief.md            the nine exercises, explained
│   ├── nb_lib.py              notebook-building and execution helpers (complete)
│   ├── calc.py                the one piece of logic that lives in a module (complete)
│   ├── test_calc.py           tests for calc.py (complete -- exercise 8's other half)
│   └── test_notebooks.py      nine exercises, each currently a pytest.skip
├── examples/                  the reference answers -- read after you try
│   ├── nb_lib.py               identical to starter/nb_lib.py
│   ├── calc.py                 identical to starter/calc.py
│   ├── test_calc.py            identical to starter/test_calc.py
│   └── test_notebooks.py       the nine exercises, solved
├── tests/
│   └── run_tests.sh            the bash harness: 16 checks
└── expected-output/
    ├── FIELDS.md                what is exact, what may differ, and why
    ├── examples-run.txt         pytest examples -q
    ├── starter-run.txt          pytest starter -q
    ├── test-run.txt             bash tests/run_tests.sh
    ├── scrambled-vs-clean.txt   the two real, differing answers from exercise 1
    ├── markdown-sample.md       real nbconvert Markdown output from exercise 7
    └── environment-record.txt   the real recorded environment from exercise 9
```

## How to run

Read `starter/00_brief.md` first, then `starter/nb_lib.py`. Then:

```bash
# your work, from the lab directory
.venv/bin/pytest starter -v

# the reference answers, once you have tried
.venv/bin/pytest examples -q

# everything, including the proof that the suite can fail
bash tests/run_tests.sh
```

**Run `pytest starter` and `pytest examples` as two separate commands.**
Both directories contain `test_calc.py` and `test_notebooks.py`, and
pytest collects test modules by dotted name; a single
`pytest examples starter` aborts collection with an `import file
mismatch`. Section 5 of the harness runs that combined form on purpose
and asserts it fails, so the warning here is checked, not just stated.

## What the commands do

| Command | What happens |
| --- | --- |
| `.venv/bin/pytest starter -v` | Runs your nine exercises. On an untouched checkout, `test_calc.py`'s 3 tests pass and all 9 notebook exercises skip, each skip message naming what to assert |
| `.venv/bin/pytest examples -q` | Runs the reference answers. Should print `12 passed` |
| `bash tests/run_tests.sh` | The full harness: version pins, the library driven directly from Python, both suites, the collision check, the fail-then-restore proof, and the cleanliness checks |

Section 2 of the harness is the interesting one. It does not import
`pytest` at all — it drives `nb_lib` directly, building and executing
notebooks and asserting on the results, exactly as your own code outside
a test suite would.

## Expected output

The final section of a green run:

```
7. Offline, and nothing left behind
  ok: no URLs inside examples/ or starter/ source
  ok: no .ipynb file anywhere inside the lab -- every notebook in this lab exists only in memory
  ok: no .ipynb_checkpoints directory anywhere inside the lab
  ok: no __pycache__ left behind (cleaned during this run)
  ok: no .pytest_cache left behind (cleaned during this run)

---------------------------------------------------------------
16 checks, 0 failure(s)
```

The full capture is in `expected-output/test-run.txt`. The two real,
differing answers from exercise 1 are in
`expected-output/scrambled-vs-clean.txt`; the real converted Markdown
from exercise 7 is in `expected-output/markdown-sample.md`.
`expected-output/FIELDS.md` records exactly which captured values are
exact everywhere and which are specific to this machine's pinned
versions — most notably, that the `cell.metadata.execution` timestamps
are the one field guaranteed to differ between any two runs, by design.

## Validation steps

1. `bash tests/run_tests.sh` prints `16 checks, 0 failure(s)` and exits 0
   (`echo $?` immediately after, with no pipe in between — a pipeline
   reports the *last* command's status and will hide a real failure).
2. `.venv/bin/pytest examples -q` prints `12 passed`.
3. `.venv/bin/pytest starter -q` prints `3 passed, 9 skipped` before you
   start, and `12 passed` when you are done.
4. Open `expected-output/scrambled-vs-clean.txt` and confirm for
   yourself that `30.0` and `50.0` really are different answers from the
   same three cells, in the same file, with no error anywhere.
5. Diff two runs of the exercise 5 notebook by hand (or read the
   assertion in `test_notebooks.py`) and confirm which JSON field
   actually differs.

## Tests

`tests/run_tests.sh` is a bash assert harness. It prints `N checks,
M failure(s)`, exits 0 only when `M` is zero, and covers:

1. the installed versions against `requirements/requirements.txt`;
2. all nine exercises, driven directly against `nb_lib` with no `pytest`
   involved;
3. `examples/` passing in full;
4. `starter/` in its untouched state;
5. the `pytest examples starter` collision, run and asserted;
6. **the proof that the suite can fail** — the harness copies the solved
   suite into a scratch directory, confirms it passes, breaks exercise
   1's central assertion, confirms a non-zero exit that names the
   failing test, and discards the scratch copy;
7. no URLs in the exercise code, and no `.ipynb` file, no
   `.ipynb_checkpoints` directory, no `__pycache__` and no
   `.pytest_cache` left behind anywhere in the lab.

## Cleanup

The harness cleans up after itself, before and after every run. To reset
completely:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv          # optional: removes the lab virtual environment
git checkout -- starter/   # optional: throws away your work and restores the skips
```

Nothing else exists to remove. No notebook this lab builds is ever
written to disk, so there is no `.ipynb` file, no `.ipynb_checkpoints`
directory and no orphaned kernel connection file to clean up — the
harness asserts all three directly.

## Troubleshooting

`troubleshooting.md` covers the failures in detail. The three most
common:

- **`pytest: command not found`** — you have not created the `.venv`, or
  you are calling bare `pytest` instead of `.venv/bin/pytest`.
- **`import file mismatch`** — you ran `pytest examples starter` in one
  command. Run them as two.
- **`[IPKernelApp] WARNING | Kernel is running over TCP without
  encryption`** — expected on every kernel start in this lab; see
  `security.md`. Not a failure.

## Security notes

`security.md` has the full account. In short: one network connection
ever (the `pip install`), every kernel bound to `127.0.0.1` only, no
port exposed beyond loopback, no `sudo`, no credential, no API key,
nothing written outside a `pytest`-managed temporary directory this lab
deletes itself. Every value in every exercise is a small invented
literal — no real dataset appears anywhere in this lab.

## Extension exercises

1. **Watch the hidden-state bug happen without `nb_lib`.** Start
   `.venv/bin/python3 -i`, `import nbformat as nbf`, build a two-cell
   notebook by hand, execute both cells with a `NotebookClient` inside
   `with client.setup_kernel():`, delete the first cell from
   `nb.cells`, and rerun the second cell in the same interpreter
   session. Then start a *fresh* Python process and try the same
   one-cell notebook in a new kernel.
2. **Break the parameterisation exercise on purpose.** Change the
   injected-parameters cell to set a *different* variable name than the
   parameters cell declares, and watch the analysis cells raise
   `NameError` — the same failure mode `papermill` is built to prevent
   by tagging the parameters cell explicitly.
3. **Add a tenth check.** For example: assert that a notebook whose
   cells are executed twice in a row (idempotent, Day 126's sense)
   produces the same final answer both times — and find a notebook
   design where that is *not* true (a cell that appends to a list rather
   than reassigning it is the classic one).
4. **Convert to a script instead of Markdown.** Call
   `nb_lib.to_script(executed_notebook)` (already in `nb_lib.py`, not
   exercised directly) and compare what a script conversion keeps and
   drops relative to a Markdown conversion.
5. **Time a kernel's cold start.** Wrap `nb_lib.execute_clean` in
   `time.perf_counter()` calls and see how much of the harness's runtime
   is one kernel process starting up versus the code inside it running.
6. **Read `nb_lib.parameters_notebook` and rebuild it as `papermill`
   would really produce it**, using `papermill`'s documentation (do not
   install it in this lab's `.venv` unless you also add and pin it in
   `requirements/requirements.txt`), and compare the injected cell's
   exact source text to this lab's hand-built version.

## Navigation

- **Previous day:** Day 138 — Data Ethics, Bias, and Provenance
  (`labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance/`).
- **Next day:** Day 140 — Section Project: An Exploratory Study
  (`labs/sections/math-statistics-and-data/day-140-section-project-an-exploratory-study/`).
- **Week 20 project:** the week's project directory
  (`labs/sections/math-statistics-and-data/projects/week-20/`), where the
  reproducibility discipline this lab teaches applies directly to the
  notebook the project asks for.
