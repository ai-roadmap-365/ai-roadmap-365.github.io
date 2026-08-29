# Day 013 lab — Know Your Package Manager

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Package Managers: Homebrew, apt, and winget
- **Day number:** 13 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-013-package-managers-homebrew-apt-and-winget
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-013-package-managers-homebrew-apt-and-winget` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 13's lesson explains what package managers are and why they matter. This
lab makes it concrete and safe: you inspect **your own machine** to discover
which package managers it already has, run read-only queries against them, and
record how you *would* install software — **without installing anything**. It is
a look-before-you-leap tour of the software that manages all your other
software.

## Learning objectives

- Detect which package managers are present on your machine with `command -v`.
- Run safe, read-only queries against a manager (version, list, repository info).
- Identify your operating system's *default* system package manager.
- Read a cross-manager command cheat sheet and map a task across brew/apt/winget.
- Explain why a manager install is safer and more repeatable than a manual one.

## Prerequisites

- The Day 13 lesson (read it first — it explains every concept this lab inspects).
- A terminal: Terminal.app (macOS), any terminal (Linux), or PowerShell/WSL (Windows).
- Comfort running basic commands (Days 8–12). No prior package-manager experience needed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon). Detects `brew`, and `pip`/`npm` when present.
- **Linux** — fully supported. Detects `apt`/`apt-get` and runs `apt-cache policy` read-only.
- **Windows** — run the winget commands from the cheat sheet in PowerShell, or run the scripts unmodified inside WSL.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only *reads*
information about installed software; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities only: `command`, `uname`, `date`, `sed`, `grep`, `head`.
- Whatever package managers you already have — the lab installs none.

## Free and open-source options

Everything here is free. Homebrew and apt are fully open-source, as are the
packages in their main repositories; winget is free and first-party on Windows.
The lab itself uses only bash and standard utilities. No account, API key, or
purchase is required.

## Installation

None. Copy this directory (or clone the repository) and you are ready:

```bash
cd labs/sections/computing-foundations/day-013-package-managers-homebrew-apt-and-winget
```

## File structure

```text
day-013-package-managers-homebrew-apt-and-winget/
├── README.md                              ← you are here
├── metadata.yml                           ← machine-readable lab metadata
├── starter/
│   ├── detect_pkg_manager.sh              ← YOUR working file (4 exercises)
│   └── package-manager-worksheet.md        ← worksheet for the practice assignment
├── examples/
│   ├── detect_pkg_manager.sh              ← completed reference detector
│   └── command-cheatsheet.md               ← brew / apt / winget task-by-task table
├── tests/
│   └── run_tests.sh                        ← automated checks (read-only, exits 0/1)
├── expected-output/
│   ├── sample-macos.txt                    ← real captured run (macOS, Apple Silicon)
│   └── FIELDS.md                           ← required fields on every platform
├── requirements/
│   └── README.md                           ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/detect_pkg_manager.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/detect_pkg_manager.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/detect_pkg_manager.sh` — runs the reference detector: it checks
  for `brew`, `apt`, `apt-get`, `winget`, `pip`, `pip3`, and `npm` with
  `command -v`, and for each one found prints its location and one read-only
  query (`brew --version` and `brew list`; `apt-cache policy`;
  `winget --version`; `pip/pip3 --version`; `npm --version`). It installs nothing.
- `bash starter/detect_pkg_manager.sh` — the same skeleton with four read-only
  queries left as numbered exercises; each comment names the exact command to add.
- `bash tests/run_tests.sh` — runs both scripts and checks they exit 0, print the
  report header/footer, and report either a found manager or a clear
  "none detected" message; it also statically scans both scripts to confirm they
  contain no `sudo` and no install/remove/upgrade commands.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run:

```text
=== Package Manager Report ===
Generated on: 2026-07-12
Operating system kernel: Darwin

FOUND: brew -> /opt/homebrew/bin/brew
  read-only query: brew --version
    Homebrew 6.0.9
  read-only query: brew list | head
    abseil
    ada-url
    aom
    apr
    apr-util

FOUND: pip -> /opt/homebrew/opt/python@3.14/libexec/bin/pip
  read-only query: pip --version
    pip 25.2 from /opt/homebrew/lib/python3.14/site-packages/pip (python 3.14)

FOUND: npm -> /opt/homebrew/bin/npm
  read-only query: npm --version
    11.17.0

----------------------------------------
Detected 3 package manager(s) above (read-only).
Nothing was installed, removed, or upgraded.
=== End of report ===
```

Your values will differ — that is the point. On Debian/Ubuntu the report finds
`apt`/`apt-get` and shows `apt-cache policy` output instead;
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly which
fields must appear on every platform.

## Validation steps

1. Run `bash examples/detect_pkg_manager.sh` — it must exit without errors and print the header and footer.
2. Confirm it either lists at least one `FOUND:` manager or states clearly that none were detected.
3. Complete the four exercises in `starter/detect_pkg_manager.sh` and run it — the placeholder `(exercise N: ...)` lines should be replaced by real read-only query output.
4. Confirm you installed and removed **nothing**.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `14 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. The suite includes a static
safety scan that fails if either script contains `sudo` or an
install/remove/upgrade command — this lab is strictly read-only.

## Cleanup

Nothing to clean up: the scripts only read information and write nothing outside
their own console output. To reset your work, restore the starter from git:
`git checkout -- starter/detect_pkg_manager.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (no managers
found, brew/pip absent, Windows/WSL notes, safety-scan failures).

## Security notes

See [security.md](security.md). Short version: the scripts make no network
calls, need no elevated privileges, and install nothing — but real installs
elsewhere *do* change your system and sometimes need `sudo`, so run those
deliberately and only from trusted repositories.

## Extension exercises

1. Show the dependency tree of a package you have: `brew deps --tree wget`
   (macOS) or `apt-cache depends wget` (Linux). Count how many packages one
   small tool rests on.
2. Add a `pip3 list` (Python) or `npm ls -g --depth=0` (global Node packages)
   read-only query to the detector and note how a language manager's inventory
   differs from a system manager's.
3. Using the cheat sheet, write out (do not run) the full sequence you would use
   on your OS to search for, install, list, and then remove a package — the
   complete life cycle.

## Navigation

- **Previous day:** Day 12 — Shell Scripting: Variables, Loops, and Conditionals (`labs/sections/computing-foundations/day-012-shell-scripting-variables-loops-and-conditionals/`).
- **Next day:** Day 14 — Automating Tasks with Shell Scripts and cron (`labs/sections/computing-foundations/day-014-automating-tasks-with-shell-scripts-and/`, to be written).
