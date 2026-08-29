# Day 042 lab — Your Computing Foundations Toolkit Check

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Section Review: Your Computing Foundations Toolkit
- **Day number:** 42 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-042-section-review-your-computing-foundations-toolkit
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-042-section-review-your-computing-foundations-toolkit` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 42 closes Course 1 by consolidating six weeks of foundations. This lab
makes that consolidation concrete on **your own machine**: a capstone script
inspects your computer for the core Course 1 toolkit — a shell, `git`,
`curl`, `python3`, `sqlite3`, and an editor — reports each tool's version and
the day that taught it, then runs three live skill checks (make a git repo,
run a shell pipeline, query a SQLite database) that exercise skills from
across the section. The output is a **readiness report**: proof that the
foundation is real, and a pointer to any gap you should fill before Course 2.

## Learning objectives

- Run a capstone inspection script and read a readiness report.
- Confirm the core Course 1 tools are installed and note their versions.
- Perform three cross-section skills end to end: a git commit, a shell
  pipeline, and a SQLite query.
- Map each tool and skill back to the day of Course 1 that taught it.
- Complete a self-assessment worksheet and identify your weakest area and the
  exact day to revisit.

## Prerequisites

- The Day 42 lesson (read it first — it explains the six areas this lab checks).
- Days 1-41 of Course 1, which taught every tool the check looks for.
- A terminal: Terminal.app (macOS), any terminal (Linux), or PowerShell/WSL
  (Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with a POSIX shell and the
  standard utilities).
- **Windows** — run the scripts unmodified inside WSL, or run the individual
  version commands (`git --version`, etc.) manually in PowerShell and fill the
  worksheet by hand (see [troubleshooting.md](troubleshooting.md)).

## Hardware requirements

Any computer that ran the rest of Course 1. The lab only *reads* system
information and runs tiny in-memory checks; it needs no minimum RAM, disk, or
GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities: `uname`, `date`, `command`, `mktemp`, `printf`,
  `grep`, `wc`, `tr`. The tools the check *inspects* (`git`, `curl`,
  `python3`, `sqlite3`, an editor) are the section's toolkit — the script
  degrades gracefully if any are missing.

## Free and open-source options

Everything in this lab is free: bash and every command used are open-source
or ship with your OS. No account, API key, or purchase is needed. The tools
the check looks for are all free and open-source too; `requirements/README.md`
lists how to install any that are missing.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-042-section-review-your-computing-foundations-toolkit
```

## File structure

```text
day-042-section-review-your-computing-foundations-toolkit/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── toolkit_check.sh               ← YOUR working file (4 exercises)
│   └── toolkit-worksheet.md           ← self-assessment for the practice assignment
├── examples/
│   └── toolkit_check.sh               ← completed reference implementation
├── tests/
│   └── run_tests.sh                   ← automated checks
├── expected-output/
│   ├── sample-macos.txt               ← real captured run (macOS, Apple Silicon)
│   ├── tests-macos.txt                ← real captured test run
│   └── FIELDS.md                      ← required fields on every platform
├── requirements/
│   └── README.md                      ← which day covers installing each tool
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished readiness report first
bash examples/toolkit_check.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/toolkit_check.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/toolkit_check.sh` — runs the reference capstone: detects your
  OS (`uname -s`), checks for and versions the six toolkit tools mapping each
  to its Course 1 day, then runs three skill checks (a throwaway `git init` +
  commit, a `printf | grep | wc -l` pipeline, and an in-memory SQLite
  `CREATE`/`INSERT`/`SELECT`), and prints a readiness score. It is read-only
  on your real files and makes no network calls.
- `bash starter/toolkit_check.sh` — the same skeleton with four exercises left
  as `FILL_ME_IN`. Each exercise comment names the exact command to use: the
  git version, the git init/commit pair, the shell pipeline, and the final
  readiness test. Edit the file and replace each placeholder.
- `bash tests/run_tests.sh` — runs the reference script and checks it exits 0,
  prints every report block, reports git/curl/python3 as present, passes all
  three skill checks, and uses no network. It then checks your starter
  structurally, and — once you have replaced every executable `FILL_ME_IN` —
  holds it to the same strict standard.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run:

```text
=== Computing Foundations Toolkit Check ===
Generated on: 2026-07-12
Operating system kernel: Darwin

-- Tool inventory --
[ok]   shell     : /bin/zsh (maps to Day 8: Meet the Terminal)
[ok]   git       : git version 2.50.1 (Apple Git-155) (maps to Day 30: Git Fundamentals)
[ok]   curl      : curl 8.7.1 (maps to Day 21: Inspecting Traffic with curl)
[ok]   python3   : Python 3.14.0 (maps to Day 15+: used across the course)
[ok]   sqlite3   : 3.51.0 (maps to Day 39: Data Storage)
[ok]   editor    : found vim on PATH ($EDITOR unset) (maps to Day 36: Choosing an Editor)

-- Skill checks --
[ok]   git init + commit works        (Days 29-30)
[ok]   shell pipeline works           (Days 10-12)
[ok]   sqlite query works             (Day 39)

-- Readiness --
Tools present: 6 / 6   Skills passed: 3 / 3
You are ready for Course 2. Nice work finishing the foundations.
=== End of check ===
```

Your values will differ. A missing tool shows a `[--]` line naming its
install day instead of `[ok]` — the script does not crash on a gap.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the fields that
must appear on every platform.

## Validation steps

1. Run `bash examples/toolkit_check.sh` — it must exit without errors and
   print the header, tool inventory, skill checks, readiness line, and footer.
2. Confirm `git`, `curl`, and `python3` report `[ok]` on your machine.
3. Confirm all three skill checks (git commit, pipeline, SQLite query) pass.
4. Complete `starter/toolkit_check.sh` and confirm it produces the same
   readiness report.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `22 checks, 0 failure(s).` while the starter is
unfinished (14 strict checks on the reference script plus 8 structural checks
on your starter and the offline check). Once you have completed the starter it
becomes `29 checks, 0 failure(s).`. The command exits 0 on success and
non-zero on any failure, so it can run in CI. No network is used.

## Cleanup

Nothing to clean up: the scripts only read system information and use a
throwaway temp directory and an in-memory database, both discarded
automatically. To reset your work, restore the starter from git:
`git checkout -- starter/toolkit_check.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — it maps every possible `[--]`
line back to the Course 1 day that fixes it (a missing tool, an unset
editor, a failed skill check, Windows/WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts are read-only, make
no network calls, need no elevated privileges, touch no secrets, and their
only writes are a throwaway temp repo and an in-memory database that are both
discarded.

## Extension exercises

1. Add one more check to the completed script from a Course 1 area the
   starter does not cover — e.g. a global git identity (`git config --get
   user.name`), or a Python JSON parse (`python3 -c 'import json; ...'`) — map
   it to its day, degrade gracefully, and add a matching test assertion.
2. Have the script write its readiness report to a timestamped file and keep a
   history, so you can re-run it after revisiting a weak day and see progress.
3. Turn the readiness check into a git hook (Day 41) that runs on commit in a
   practice repo, refusing the commit if a core tool is missing.

## Navigation

- **Previous day:** Day 41 — Thinking in Automation: Scripts, Hooks, and
  Pipelines (`labs/sections/computing-foundations/day-041-thinking-in-automation-scripts-hooks-and/`).
- **Next day:** Day 43 — the first lesson of Course 2, Programming with
  Python (`labs/sections/programming-with-python/`, to be written).
