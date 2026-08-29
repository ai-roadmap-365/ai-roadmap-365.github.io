# Day 043 lab — Create and Verify a Virtual Environment

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Installing Python and Virtual Environments
- **Day number:** 43 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-043-installing-python-and-virtual-environments
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-043-installing-python-and-virtual-environments` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 43's lesson explains why every project should keep its packages isolated in
a virtual environment. This lab makes that concrete and **offline**: you create
a venv with `python3 -m venv`, activate it, and watch `which python` and
`sys.prefix` move *inside* the environment — proof, on your own machine, that
the isolation is real. No packages are downloaded and no network is used.

## Learning objectives

- Create a virtual environment with `python3 -m venv .venv`.
- Activate and deactivate it, and explain what activation changes.
- Prove isolation by inspecting `which python` and `sys.prefix` before and after
  activation.
- Record a project's dependencies in a `requirements.txt` file.
- Run an automated test script and interpret its pass/fail output.

## Prerequisites

- The Day 43 lesson (read it first — it explains every concept this lab
  demonstrates).
- Course 1 fluency: the terminal, `PATH` (Day 11), and package managers (Day 13).
- Python 3 installed (`python3 --version` prints 3.x). See
  `requirements/README.md` if it is missing.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python 3.14.0).
- **Linux** — fully supported (any distribution with `python3` and the `venv`
  module; install `python3-venv` on minimal Debian/Ubuntu).
- **Windows** — use `.venv\Scripts\activate` in PowerShell, or run the scripts
  unchanged inside WSL (recommended). See `troubleshooting.md`.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab creates a tiny, empty
environment in a temp directory; it needs no meaningful RAM, disk, or GPU.

## Required software

- `python3` ≥ 3.8 with the `venv` module (bundled since Python 3.3).
- `bash` ≥ 3.2 (preinstalled on macOS and Linux).

No PyPI packages, accounts, API keys, or network access are required.

## Free and open-source options

Everything in this lab is free and open source: Python, the `venv` module, and
`pip` all ship with Python at no cost, and PyPI (used in later labs, not this
one) is a free public repository. No purchase or account is ever needed.

## Installation

None beyond Python itself. Copy this directory (or clone the repository) and
change into it:

```bash
cd labs/sections/programming-with-python/day-043-installing-python-and-virtual-environments
```

## File structure

```text
day-043-installing-python-and-virtual-environments/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── venv_demo.sh                ← YOUR working file (4 exercises)
│   └── venv-worksheet.md           ← worksheet for the practice assignment
├── examples/
│   └── venv_demo.sh                ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated, offline checks
├── expected-output/
│   ├── sample-macos.txt            ← real captured run (macOS, Apple Silicon)
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (just Python 3)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/venv_demo.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/venv_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/venv_demo.sh` — the reference script. It makes a temp
  directory, prints the interpreter version, creates `.venv` with
  `python3 -m venv .venv`, shows `which python` before activation, activates the
  venv, then shows `which python`, `which pip`, and `sys.prefix` all pointing
  inside `.venv`, writes a `requirements.txt`, deactivates, and deletes the temp
  directory on exit.
- `bash starter/venv_demo.sh` — the same scaffolding with four numbered
  exercises for you to fill in: (1) create the venv, (2) activate it, (3) prove
  isolation by printing `which python` and `sys.prefix`, (4) deactivate. Each
  exercise comment names the exact command.
- `bash tests/run_tests.sh` — offline checks: `python3` is available, a venv can
  be created, `sys.prefix` points inside it, activation redirects `which
  python`, cleanup leaves nothing behind, the example runs and confirms
  isolation, and the starter still ships its four exercises.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run. The key lines:

```text
--- Step 4: activate and prove isolation ---
which python -> /private/var/folders/.../venv-demo.qPEavX/.venv/bin/python
sys.prefix   -> /private/var/folders/.../venv-demo.qPEavX/.venv
OK: sys.prefix is inside the .venv — the environment is isolated.
```

Your temp path will differ on every run — only the *shape* matters.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour and documents platform differences.

## Validation steps

1. Run `bash examples/venv_demo.sh` — it must exit without errors and print
   `OK: sys.prefix is inside the .venv`.
2. Complete `starter/venv_demo.sh` (replace all four `EXERCISE_*_NOT_DONE`
   lines) and run it; confirm activation changes `which python`.
3. Fill in `starter/venv-worksheet.md` with your real before/after paths.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `11 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It needs no network.

## Cleanup

Nothing to clean up: both scripts do all their work in a temporary directory
and remove it on exit (via a cleanup trap), even if a step fails. To reset your
edited starter, restore it from git: `git checkout -- starter/venv_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (`python` vs
`python3`, activation per shell and on Windows, missing `python3-venv`, keeping
`.venv` out of git).

## Security notes

See [security.md](security.md). Short version: the scripts run no network calls,
need no elevated privileges, work only in a temp directory, and never commit
anything. Never commit a `.venv` folder; pin your dependencies.

## Extension exercises

1. With a venv active, run `pip list` and `pip freeze` — note that a fresh venv
   has almost nothing installed, which is the point of starting clean.
2. Create two venvs in two folders and confirm, with `sys.prefix`, that each is
   independent of the other.
3. Add a real `.gitignore` containing `.venv/` to a scratch project and verify
   with `git status` that the environment is ignored while `requirements.txt`
   is tracked.

## Navigation

- **Previous day:** Day 42 — Section Review: Your Computing Foundations Toolkit
  (`labs/sections/computing-foundations/day-042-section-review-your-computing-foundations-toolkit/`).
- **Next day:** Day 44 — Variables and Types
  (`labs/sections/programming-with-python/day-044-variables-and-types/`, to be written).
