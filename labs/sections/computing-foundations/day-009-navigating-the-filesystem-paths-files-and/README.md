# Day 009 lab — Build and Explore a File Tree

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Navigating the Filesystem: Paths, Files, and Permissions
- **Day number:** 9 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-009-navigating-the-filesystem-paths-files-and
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-009-navigating-the-filesystem-paths-files-and` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 9's lesson explains the filesystem tree, paths, and permissions. This lab
makes them muscle memory: you build a small directory tree inside a safe,
temporary workspace, navigate it with `pwd`/`cd`/`ls`, create and move files,
and make a file executable with `chmod` while watching its permission string
change from `-rw-r--r--` (644) to `-rwxr-xr--` (754). Everything happens inside
a folder the script creates and then deletes, so you cannot harm anything else
on your machine.

## Learning objectives

- Run `pwd`, `cd`, and `ls -la` and read every field of a long listing.
- Build a nested directory tree with a single `mkdir -p` command.
- Create files with `touch`, move them with `mv`, and confirm the result.
- Change a file's permissions with `chmod` and read the before/after string.
- Translate a permission string to and from octal notation (e.g. 754).
- Run an automated test script and interpret its pass/fail output.

## Prerequisites

- The Day 9 lesson (read it first — it explains every concept this lab uses).
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL (Windows).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with `bash`, `mktemp`, and
  the standard file utilities).
- **Windows** — run the scripts unmodified inside WSL (Windows Subsystem for
  Linux); native PowerShell is not supported for this bash lab.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab creates a handful of
empty files in a temporary directory and removes them; it needs no meaningful
disk, RAM, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard utilities only: `mktemp`, `mkdir`, `touch`, `cp`, `mv`, `rm`, `ls`,
  `chmod`, `pwd`, `find` — all preinstalled.

## Free and open-source options

Everything in this lab is free: bash and every command used are open-source or
ship with your OS. No account, API key, or purchase is needed.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-009-navigating-the-filesystem-paths-files-and
```

## File structure

```text
day-009-navigating-the-filesystem-paths-files-and/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── explore_files.sh            ← YOUR working file (5 exercises)
│   └── filesystem-worksheet.md     ← worksheet for the practice assignment
├── examples/
│   └── explore_files.sh            ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks
├── expected-output/
│   ├── sample-macos.txt            ← real captured run (macOS, Apple Silicon)
│   └── FIELDS.md                   ← required output lines and platform notes
├── requirements/
│   └── README.md                   ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/explore_files.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/explore_files.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/explore_files.sh` — runs the reference script: creates a
  temporary workspace **inside this lab directory** with `mktemp -d`, registers
  a trap to delete it on exit, then `cd`s into it, builds `project/data` with
  `mkdir -p`, creates files with `touch`, lists with `ls`/`ls -la`, makes
  `run.sh` executable with `chmod 754` (printing the before/after `ls -l`),
  moves `report.md` into `data/` with `mv`, and finally removes the workspace.
- `bash starter/explore_files.sh` — the same skeleton with five exercises left
  as `REPLACE-ME` lines; each comment names the exact command to use. Edit the
  file in any text editor and replace each `REPLACE-ME` line with the command
  named beside it.
- `bash tests/run_tests.sh` — runs the reference script and checks that it
  builds the sample tree, makes `run.sh` executable (verifying both permission
  strings), prints the required lines, exits 0, and leaves **no** temporary
  workspace behind; then checks your starter the same way once you have
  replaced every `REPLACE-ME`.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run. The key lines are the two `run.sh` listings that bracket the
`chmod`:

```text
Before chmod:
-rw-r--r--@ 1 you  staff  0 Jul 12 13:34 run.sh
After chmod:
-rwxr-xr--@ 1 you  staff  0 Jul 12 13:34 run.sh
```

Your workspace path, owner name, and dates will differ. On macOS an `@` may
follow the permission string (extended attributes); the nine permission bits
before it are what matter. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists every required line and the small macOS/Linux differences.

## Validation steps

1. Run `bash examples/explore_files.sh` — it must exit without errors and print
   `=== Done ===` at the end.
2. Confirm the permission string on `run.sh` changes from `-rw-r--r--` to
   `-rwxr-xr--` across the `chmod`.
3. Run `find . -maxdepth 1 -type d -name 'tmp.explore.*'` — it must print
   nothing, proving the workspace was cleaned up.
4. Complete the five exercises in `starter/explore_files.sh`, then run the tests.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `15 checks, 0 failure(s).` (11 strict checks against the
reference script, and 4 structural checks against your starter — which become
11 strict checks once you have replaced every `REPLACE-ME`). The command exits
0 on success and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: each script deletes its own temporary workspace on exit
via a `trap`, so no files are left behind. To reset your edits to the starter,
restore it from git: `git checkout -- starter/explore_files.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (permission
errors, `No such file or directory`, hidden files, `mktemp` differences, WSL
notes).

## Security notes

See [security.md](security.md). Short version: the scripts write **only**
inside a temporary directory they create in this lab folder and then remove;
they make no network calls and need no elevated privileges. The file also
explains, in general, why `rm -rf` must be treated with care.

## Extension exercises

1. Give a file three different permission settings in turn (`chmod 644`,
   `chmod 600`, `chmod 755`), running `ls -l` after each, and predict the
   permission string before you check it.
2. Create a symbolic link with `ln -s data/notes.txt shortcut.txt`, inspect it
   with `ls -l` (note the leading `l` and the `->` arrow), then remove the link
   and confirm the original file is untouched.
3. Extend `explore_files.sh` to also copy a file with `cp` and print its
   `ls -l`, then add a matching check to `tests/run_tests.sh`.

## Navigation

- **Previous day:** Day 8 — the lab in `labs/sections/computing-foundations/` for the preceding lesson.
- **Next day:** Day 10 — Working with Text: cat, grep, sed, and Pipes (`labs/sections/computing-foundations/day-010-working-with-text-cat-grep-sed/`, to be written).
