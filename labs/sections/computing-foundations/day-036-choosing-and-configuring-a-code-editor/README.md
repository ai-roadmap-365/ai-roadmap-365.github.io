# Day 036 lab — Configure Your Editor with EditorConfig

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Choosing and Configuring a Code Editor
- **Day number:** 36 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-036-choosing-and-configuring-a-code-editor
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-036-choosing-and-configuring-a-code-editor` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 36's lesson explains how to choose and configure a code editor. This lab
makes one of its most practical ideas concrete: **EditorConfig**, the small,
editor-agnostic standard that keeps a whole team's formatting consistent. You
create an `.editorconfig` file with the standard rules and run a real checker
that reports which files obey the rules and which break them — the same kind
of check that editors and continuous-integration pipelines run for you.

## Learning objectives

- Write an `.editorconfig` file with the six standard keys and say what each enforces.
- Explain the difference between personal editor settings and a shared `.editorconfig`.
- Run an editor-agnostic checker that detects tabs-versus-spaces, trailing whitespace, and a missing final newline.
- Complete a working script by filling in four well-specified exercises.
- Record your own editor choice and configuration on a worksheet you keep for later lessons.

## Prerequisites

- The Day 36 lesson (read it first — it explains editors, settings, and EditorConfig).
- A terminal and basic comfort running `bash` scripts (from the earlier lessons in this section).
- Any code editor to view and edit the files (this lab is where you put one to use).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with `bash`, `awk`, `grep`, `mktemp`).
- **Windows** — run the scripts inside WSL (Windows Subsystem for Linux); the plain Windows shell is not supported for this lab.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab creates a few tiny
text files in a temporary directory and reads them; it needs no meaningful
RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard POSIX utilities only: `awk`, `grep`, `printf`, `tail`, `mktemp`, `basename`. All preinstalled.
- No editor extension or plugin is required to run the lab, though you will configure an editor as part of the practice assignment.

## Free and open-source options

Everything here is free. `bash` and every utility used are open-source or ship
with your OS, and EditorConfig itself is an open standard supported by many
free editors (VS Code, Vim/Neovim, Zed, and more, some via a free plugin). No
account, API key, or purchase is needed.

## Installation

None. Copy or clone this directory and change into it:

```bash
cd labs/sections/computing-foundations/day-036-choosing-and-configuring-a-code-editor
```

## File structure

```text
day-036-choosing-and-configuring-a-code-editor/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── editorconfig_demo.sh           ← YOUR working file (4 exercises)
│   └── editor-worksheet.md            ← worksheet for the practice assignment
├── examples/
│   └── editorconfig_demo.sh           ← completed reference implementation
├── tests/
│   └── run_tests.sh                   ← automated checks
├── expected-output/
│   ├── sample-run.txt                 ← real captured run of the demo
│   └── FIELDS.md                      ← which output lines are stable vs machine-specific
├── requirements/
│   └── README.md                      ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/editorconfig_demo.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/editorconfig_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/editorconfig_demo.sh` — runs the reference script: it creates a temporary sample project with one clean file and three messy ones (tab-indented, trailing whitespace, missing final newline), writes an `.editorconfig` with the six standard rules, checks every file against those rules using `awk`/`grep`/`tail`, prints a report, and deletes the temporary project on exit.
- `bash starter/editorconfig_demo.sh` — the same skeleton with four `FILL-IN` placeholders. Each exercise comment names the exact line to write: (1) the six `.editorconfig` rules, (2) a call to check a file, (3) a fix for the trailing-whitespace file, (4) a re-check to verify the fix. Edit the file in your editor and replace each placeholder.
- `bash tests/run_tests.sh` — verifies that the demo writes an `.editorconfig` containing all six required keys and that its checker detects the trailing-whitespace, missing-final-newline, and tab violations while passing the clean file; exits 0 on success, non-zero on any failure, so it can run in CI.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real captured run:

```text
=== EditorConfig demo ===
Created sample project in: /tmp/editorconfig-demo.XXXXXX
Wrote .editorconfig with 6 rules.

Checking files against .editorconfig ...
  clean.py ............ OK
  tabs.py ............. VIOLATION: uses tabs (indent_style = space)
  trailing.py ......... VIOLATION: trailing whitespace on 2 line(s)
  no_newline.py ....... VIOLATION: missing final newline

3 file(s) with violations, 1 clean.
Cleaning up temporary project.
```

Only the temporary path on the second line changes between runs and machines;
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) explains exactly which
lines are stable.

## Validation steps

1. Run `bash examples/editorconfig_demo.sh` — it must print the report and exit without error.
2. Complete the four exercises in `starter/editorconfig_demo.sh`, then run it — the "after the fix" check must report `trailing.py ... OK`.
3. Confirm your starter no longer contains any `FILL-IN` placeholder.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `12 checks, 0 failure(s).` (six checks that the demo
writes each required `.editorconfig` key, and six that its checker correctly
classifies the four sample files). If you have completed the starter, the
tests additionally run it and confirm your fix. The command exits 0 on success
and non-zero on any failure.

## Cleanup

Nothing to clean up: both scripts write only into a temporary directory that
they delete automatically on exit (via a `trap`), and they make no network
calls and change no settings. To reset your work, restore the starter from
git: `git checkout -- starter/editorconfig_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (wrong
directory, permission messages, missing utilities, WSL notes, and what to do
if the checker reports no violations).

## Security notes

See [security.md](security.md). Short version: the scripts run no network
calls, need no elevated privileges, and write only to a self-deleting
temporary directory — but read them first, as you should with any script.

## Extension exercises

1. Add a `[*.md]` section to the `.editorconfig` that sets `trim_trailing_whitespace = false` (Markdown uses two trailing spaces to mean a line break), and confirm the checker or your editor now treats Markdown differently from code.
2. Extend the checker to also flag files that use more than two spaces of indentation, mirroring `indent_size = 2`.
3. Install the EditorConfig support for your editor (built in for some, a free plugin for others), open the sample files, and watch your editor enforce the same rules the checker reports.

## Navigation

- **Previous day:** Day 35 — Git Workflows for Real Projects (`labs/sections/computing-foundations/day-035-git-workflows-for-real-projects/`).
- **Next day:** Day 37 — Debuggers, Linters, and Formatters (`labs/sections/computing-foundations/day-037-debuggers-linters-and-formatters/`, to be written).
