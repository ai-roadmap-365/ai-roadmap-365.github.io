# Day 060 lab — Stdlib Toolkit

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A Tour of the Standard Library
- **Day number:** 60 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-060-a-tour-of-the-standard-library
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-060-a-tour-of-the-standard-library` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 60's lesson tours the Python standard library — the "batteries included"
modules that ship with Python — and teaches the judgement to prefer them
before adding a third-party dependency. This lab makes that concrete. You
build **Stdlib Toolkit**, a small directory-audit tool that uses four drawers
of the toolbox together: `pathlib` to walk a folder, `collections.Counter` to
tally file extensions, `datetime` to stamp the report, and `json` to write it
out — proving you solved a genuine, useful task with **nothing installed**.
You build it from a starter, one exercise at a time, then run an automated
test suite that checks the tally deterministically (ignoring the volatile
timestamp). This is the everyday glue of AI work: before anything is trained,
you must describe your data directory precisely and reproducibly.

## Learning objectives

- Walk a directory tree with `pathlib` (`Path`, `.rglob`, `.is_file`) instead
  of gluing path strings together.
- Tally categories with `collections.Counter` and read the result largest-first
  with `.most_common()`.
- Stamp a report with `datetime.now().isoformat()` for a sortable, unambiguous
  timestamp.
- Write and read structured results with `json`, and keep the tool testable by
  taking all input from arguments (`argparse`).
- Feel the standard-library-first habit directly: build a real tool with no
  `pip install` at all.

## Prerequisites

- The Day 60 lesson (read it first — it tours every module this lab uses).
- Days 57–59: functions and the `main` guard, modules and imports, and scope.
- Day 56: reading and writing JSON with `json.load`/`json.dump`, and
  command-line tools with `argparse`.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The tool is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The tool reads only file names and metadata
and writes a tiny JSON report; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `pathlib`, `collections`, `datetime`, `json`,
  `argparse`, and `sys` all ship with Python. No packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed — which
is the whole point of the lab. Every module it uses is part of Python itself.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-060-a-tour-of-the-standard-library
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-060-a-tour-of-the-standard-library/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── sample-data/                    ← bundled folder to audit (6 files, one nested)
│   ├── a.csv, b.csv
│   ├── sub/c.csv
│   ├── x.json, y.json
│   └── notes.txt
├── starter/
│   └── toolkit.py                  ← YOUR working file (4 numbered exercises)
├── examples/
│   └── toolkit.py                  ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (deterministic tally, import)
├── expected-output/
│   ├── sample-run.txt              ← real captured session with the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished tool first. Audit the bundled sample folder.
python3 examples/toolkit.py --dir sample-data

# 2. Write the same report to a file, then inspect it.
python3 examples/toolkit.py --dir sample-data --out report.json
cat report.json

# 3. Your task: complete the four exercises in the starter, then run it.
python3 starter/toolkit.py --dir sample-data

# 4. Prove a function is importable (the payoff of the main guard).
python3 -c "import sys; sys.path.insert(0, 'examples'); from toolkit import tally_extensions; print(tally_extensions(['a.csv', 'b.csv', 'c.txt']))"

# 5. Check your work, then clean up.
bash tests/run_tests.sh
rm -f report.json
```

## What the commands do

- `--dir sample-data` — walks the folder recursively with `pathlib`, tallies
  file extensions with `collections.Counter`, stamps the moment with
  `datetime`, and prints a JSON report. This is the four-drawer toolkit in one
  run.
- `--out report.json` — additionally writes the same report to a file with
  `json.dump`, so you can save it and compare against a later run.
- `cat report.json` — shows the persisted, human-readable JSON report on disk.
- `python3 -c "...tally_extensions..."` — imports one function from the module
  and calls it without running the whole tool, which works only because the
  main guard holds `main` back on import.
- `bash tests/run_tests.sh` — builds a throwaway directory with a known mix of
  files (including an uppercase `.CSV` and a file with no extension), runs the
  reference tool, and asserts on the stable fields only — the volatile
  timestamp is deliberately ignored. Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session. The report for the bundled `sample-data` folder is:

```text
{
  "generated_at": "2026-07-13T11:56:58",
  "directory": "sample-data",
  "total_files": 6,
  "by_extension": {
    ".csv": 3,
    ".json": 2,
    ".txt": 1
  }
}
```

The `generated_at` timestamp is the current time and will differ on your
machine; every other field is deterministic.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every input on every platform.

## Validation steps

1. `python3 examples/toolkit.py --dir sample-data` prints a report with
   `total_files: 6` and `by_extension` `{".csv": 3, ".json": 2, ".txt": 1}`.
2. `python3 examples/toolkit.py --dir sample-data --out report.json` then
   `cat report.json` shows the same report saved as valid JSON.
3. Complete the four exercises in `starter/toolkit.py`, run it on
   `sample-data`, and confirm the tally matches the reference.
4. `python3 -c "...tally_extensions(['a.csv', 'b.csv', 'c.txt'])..."` prints
   `{'.csv': 2, '.txt': 1}`.
5. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `14 checks, 0
failure(s).` Once you complete all four starter exercises, the suite runs your
version through the same deterministic tally plus the main-guard check, giving
`19 checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The tool writes only the report file you name with `--out`. Remove any you
created:

```bash
rm -f report.json my-report.json
```

To reset your work, restore the starter from git:
`git checkout -- starter/toolkit.py`. The test runner cleans up its own
temporary directory automatically.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, running from the lab directory, why the timestamp changes every
run, case-insensitive extension counting, files with no extension, importing
vs running, and permissions.

## Security notes

See [security.md](security.md). Short version: the tool makes no network
calls and needs no privileges; it reads only file names and metadata and
writes only the report you name. Preferring the standard library is itself a
security posture — fewer dependencies mean a smaller attack surface — and the
tool reads data with `json`, never `eval()`.

## Extension exercises

1. Add a `--top N` option (with `argparse`) so the report includes a
   `top_extensions` list of the N most common extensions, via
   `Counter.most_common(N)`.
2. Make the tool robust: if the `--dir` directory does not exist, print a
   clear message to standard error and exit non-zero instead of crashing.
3. Add a `--format` option (`json` or `text`) where `text` prints an aligned,
   human-readable one-line-per-extension summary.
4. Extend the report using two more drawers: `total_bytes` (sum
   `p.stat().st_size` with `pathlib`) and `mean_bytes` (with `statistics`,
   guarding the empty-folder case).
5. Write your own `tests/test_toolkit.py` that imports `tally_extensions` and
   asserts its behaviour, including the case-insensitive and no-extension
   cases, printing `all tests passed` only if every assertion holds.

## Navigation

- **Previous day:** Day 59 — Scope and Namespaces
  (`labs/sections/programming-with-python/day-059-scope-and-namespaces/`).
- **Next day:** Day 61 — Writing Readable Code
  (`labs/sections/programming-with-python/day-061-writing-readable-code/`, to be written).
- **Week 9 theme:** Functions and Program Design — building, organising, and
  reaching for well-made code, of which the standard library is the largest
  and best-tested example.
