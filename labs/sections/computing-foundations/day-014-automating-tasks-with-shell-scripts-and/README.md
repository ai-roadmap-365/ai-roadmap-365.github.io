# Day 014 lab — Automate a File-Organizing Task

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Automating Tasks with Shell Scripts and cron
- **Day number:** 14 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-014-automating-tasks-with-shell-scripts-and
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-014-automating-tasks-with-shell-scripts-and` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 14's lesson explains task automation: a safe script plus a scheduler. This
lab makes the "safe script" half real. You build a file organizer that sorts a
folder's files into subfolders by extension — with the three properties every
scheduled job needs: a **dry-run** preview, a **log** of what it did, and
**idempotency** so it is safe to run twice. You then read (but do not install)
the cron schedules that would run it daily or weekly. Nothing here edits your
crontab or touches anything outside a practice folder you create.

## Learning objectives

- Write a shell script that sorts files into subfolders by extension.
- Add a `--dry-run` mode that previews actions without changing anything.
- Make a script log every action with a timestamp.
- Make a move operation idempotent, so a second run is harmless.
- Read a cron schedule field by field and write lines for "8 p.m. daily" and
  "6 a.m. Monday" — without adding them to your real crontab.

## Prerequisites

- The Day 14 lesson (read it first — it explains cron, logging, dry-run, and
  idempotency).
- Day 12 (shell scripting: variables, loops, conditionals).
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL (Windows).
- No software to install and no scheduler to configure.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with a POSIX shell).
- **Windows** — run the scripts unmodified inside WSL.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only creates a small
scratch folder of empty files; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities only: `basename`, `dirname`, `mkdir`, `mv`, `tr`,
  `date`, `find`. All preinstalled.

## Free and open-source options

Everything here is free: bash and every command used ship with your OS. No
account, API key, purchase, or network access is needed. The schedulers
discussed in the lesson (cron, launchd, systemd timers, Task Scheduler) are all
built into their operating systems at no cost — but this lab installs none of
them.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-014-automating-tasks-with-shell-scripts-and
```

## File structure

```text
day-014-automating-tasks-with-shell-scripts-and/
├── README.md                         ← you are here
├── metadata.yml                      ← machine-readable lab metadata
├── starter/
│   ├── organize_files.sh             ← YOUR working file (5 exercises)
│   └── automation-worksheet.md       ← cron expressions + dry-run prediction
├── examples/
│   ├── organize_files.sh             ← completed reference implementation
│   └── schedule-examples.md          ← cron lines to READ (not install)
├── tests/
│   └── run_tests.sh                  ← automated checks in an isolated temp dir
├── expected-output/
│   ├── sample-dry-run.txt            ← real captured dry run
│   ├── sample-real-run.txt           ← real captured real run + log
│   └── FIELDS.md                     ← invariants and platform notes
├── requirements/
│   └── README.md                     ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. Make a scratch folder with some mixed files
mkdir -p ~/organize-demo
touch ~/organize-demo/report.pdf ~/organize-demo/notes.txt \
      ~/organize-demo/photo.jpg ~/organize-demo/data.csv ~/organize-demo/archive.zip

# 2. Preview first — the dry run changes nothing
bash examples/organize_files.sh --dry-run ~/organize-demo

# 3. Run it for real, then run it AGAIN to see idempotency
bash examples/organize_files.sh ~/organize-demo
bash examples/organize_files.sh ~/organize-demo

# 4. Your task: complete the five exercises in the starter, then run it
bash starter/organize_files.sh --dry-run ~/organize-demo

# 5. Check everything
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/organize_files.sh --dry-run ~/organize-demo` — runs the
  reference organizer in preview mode: it prints one "would create directory"
  line per new extension and one "would move" line per file, and changes
  nothing on disk.
- `bash examples/organize_files.sh ~/organize-demo` — the real run: it creates
  extension subfolders (`pdf/`, `txt/`, …), moves each file into its folder,
  and appends a timestamped line per move to `~/organize-demo/organize.log`. A
  second identical run moves nothing (idempotency).
- `bash starter/organize_files.sh ...` — the same script with five exercises to
  complete; each numbered comment names the exact code to add.
- `bash tests/run_tests.sh` — creates a fresh temp directory of known files,
  verifies the dry run changes nothing, the real run sorts correctly and logs,
  and a second run is idempotent, then removes the temp directory. It never
  touches cron or anything outside its sandbox.

## Expected output

See [`expected-output/sample-dry-run.txt`](expected-output/sample-dry-run.txt)
and [`expected-output/sample-real-run.txt`](expected-output/sample-real-run.txt)
— real captured runs. The dry run prints, for a folder of five mixed files:

```text
[dry-run] would create directory: /home/you/organize-demo/pdf
[dry-run] would move report.pdf -> pdf/
...
[dry-run] complete: 5 file(s) would be organized, 0 changes made
```

The real run reports the same moves as actions taken and writes `organize.log`;
a second real run reports `0 file(s) organized`. Your file names and line order
may differ. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the
invariants every correct run must satisfy.

## Validation steps

1. Run the dry run and confirm with `ls ~/organize-demo` that **nothing moved**.
2. Run it for real and confirm files landed in subfolders named for their
   (lowercased) extension.
3. Confirm `~/organize-demo/organize.log` has one timestamped line per move.
4. Run it a second time and confirm it reports `0 file(s) organized`.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `18 checks, 0 failure(s).` The command exits `0` on
success and non-zero on any failure, so it can run in CI. All test activity
happens inside a temporary directory created with `mktemp` and removed on exit
— the tests never read or write cron, launchd, systemd, or anything outside
that sandbox.

## Cleanup

```bash
rm -rf ~/organize-demo                        # remove your scratch folder
git checkout -- starter/organize_files.sh     # optional: reset your work
```

The tests clean up their own temp directory automatically. Nothing in this lab
leaves a scheduled job behind, because nothing in this lab creates one.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (missing target
folder, dry run appearing to move files, files without extensions, idempotency
confusion, WSL notes, and why a real scheduled job might not run).

## Security notes

See [security.md](security.md). Short version: the script only touches the
folder you give it, needs no `sudo`, makes no network calls, and this lab never
edits your crontab. Always dry-run a move-or-delete script first.

## Extension exercises

1. Add a per-run summary line to `organize.log` (a timestamp and the count of
   files moved this run) so a week of logs tells the folder's story at a glance.
2. Add a `--quiet` flag that suppresses per-file output but still logs, for use
   in a scheduled job whose console output you do not read.
3. On paper, design a real crontab line for your own Downloads folder: choose a
   time, write the full line with absolute paths, and note which log you would
   check the next morning to confirm it ran.

## Navigation

- **Previous day:** Day 13 — Package Managers: Homebrew, apt, and winget
  (`labs/sections/computing-foundations/day-013-package-managers-homebrew-apt-and-winget/`).
- **Next day:** Day 15 begins the next week (to be written). This lab feeds the
  **Week 2 project — a Personal Automation Script.**
