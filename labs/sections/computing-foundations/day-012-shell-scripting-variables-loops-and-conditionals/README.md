# Day 012 lab — Write Your First Real Script

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Shell Scripting: Variables, Loops, and Conditionals
- **Day number:** 12 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-012-shell-scripting-variables-loops-and-conditionals
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-012-shell-scripting-variables-loops-and-conditionals` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 12's lesson turns you from someone who types commands into someone who
*writes* them down as reliable scripts. This lab makes that concrete: you build
`backup_notes.sh` — a genuinely useful tool that takes a directory, counts its
files by extension, and prints a summary — completing it through five numbered
exercises that each add one real concept (an argument with a default, a
validation conditional, a function, a counting loop, and a report). By the end
you will have written a real script using variables, quoting, a function, a
loop, a conditional, and `set -euo pipefail`, and confirmed it with an
automated test suite.

## Learning objectives

- Turn a sequence of commands into an executable, strict-mode shell script.
- Read a command-line argument with a sensible default (`${1:-.}`).
- Validate input with a conditional and signal failure with an exit code.
- Write a function and call it from a loop that counts files by extension.
- Quote every variable expansion so filenames with spaces are handled safely.
- Run an automated test that checks real behavior and interpret its output.

## Prerequisites

- The Day 12 lesson (read it first — it explains every construct this lab uses).
- Days 8–11: comfort in the terminal, moving around the filesystem, and reading text.
- A terminal and any text editor. No programming experience beyond the course so far.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, bash 3.2.57).
- **Linux** — fully supported (any distribution with bash; uses only portable commands).
- **Windows** — run the scripts unmodified inside WSL (Windows Subsystem for Linux). Native PowerShell is a different language and is not covered here.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads a directory
listing and prints a report; it needs no particular RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities only: `basename`, `sort`, `uniq`, `printf` — all preinstalled.
- Optional: **ShellCheck** (a free, open-source linter) if you want to check your script for common bugs. It is not required to complete the lab.

## Free and open-source options

Everything in this lab is free and open source: `bash` and every command used
ship with your OS. The optional ShellCheck linter is free and open source too.
No account, API key, network access, or purchase is needed.

## Installation

None required. Copy this directory (or clone the repository) and change into it:

```bash
cd labs/sections/computing-foundations/day-012-shell-scripting-variables-loops-and-conditionals
```

To optionally install ShellCheck: `brew install shellcheck` (macOS) or
`sudo apt install shellcheck` (Debian/Ubuntu).

## File structure

```text
day-012-shell-scripting-variables-loops-and-conditionals/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── backup_notes.sh                ← YOUR working file (5 exercises)
│   └── scripting-worksheet.md         ← predict-then-run worksheet
├── examples/
│   ├── backup_notes.sh                ← completed reference implementation
│   └── sample-notes/                  ← a known directory to run against
├── tests/
│   └── run_tests.sh                   ← automated checks (fixture-based)
├── expected-output/
│   ├── sample-run.txt                 ← real captured run on sample-notes
│   └── FIELDS.md                      ← the fields every correct run prints
├── requirements/
│   └── README.md                      ← dependency statement
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/backup_notes.sh examples/sample-notes

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/backup_notes.sh examples/sample-notes

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/backup_notes.sh examples/sample-notes` — runs the reference script against the sample directory: it takes the directory argument, validates it, loops over the files, uses the `extension_of` function and `sort | uniq -c` to count each extension, and prints the summary.
- `bash starter/backup_notes.sh examples/sample-notes` — runs your in-progress script. The skeleton runs from the start; each exercise you complete makes the output more correct until it matches the reference.
- `bash tests/run_tests.sh` — builds a temporary directory with a known set of files (3 `.txt`, 2 `.md`, 1 `.csv`, 1 file with no extension, plus a subdirectory), runs the reference script against it, and asserts the counts are exactly right; also checks the empty-directory and "not a directory" cases. Exits 0 on success, non-zero on any failure.

## Expected output

Running the reference script on the bundled sample directory prints (see
[`expected-output/sample-run.txt`](expected-output/sample-run.txt)):

```text
=== Notes summary ===
Directory: sample-notes
Total files: 6
By extension:
  (no extension): 1
  csv: 1
  md: 2
  txt: 2
=== End of summary ===
```

Extensions are printed in sorted order, so `(no extension)` (which begins with
`(`) sorts before the lettered extensions. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists exactly which lines a correct run must print.

## Validation steps

1. Run `bash starter/backup_notes.sh examples/sample-notes` — it must exit without errors.
2. Once you have completed all five exercises, its output must match `expected-output/sample-run.txt` exactly.
3. Confirm the script handles a bad path: `bash starter/backup_notes.sh /no/such/dir` prints an error to standard error and exits non-zero (check with `echo $?`).
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `11 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. The tests target the
reference script in `examples/`; complete the starter and compare its output
against the same sample to check your own version.

## Cleanup

Nothing to clean up: the scripts only read a directory and print a report —
they create, move, and delete nothing. The test suite writes only to a
temporary directory (`mktemp -d`) and removes it automatically on exit. To
reset your work, restore the starter from git:
`git checkout -- starter/backup_notes.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (syntax errors,
`unbound variable`, spaces around `=`, wrong test operators, permission notes).

## Security notes

See [security.md](security.md). Short version: the scripts make no network
calls, need no elevated privileges, and only *read* a directory listing to
print a report — they never execute the files they find or accept untrusted
input as commands.

## Extension exercises

1. Add a total-size line: inside the loop, sum each file's size (macOS `stat -f%z "${path}"`, Linux `stat -c%s "${path}"`) using command substitution, and print `Total size: N bytes`.
2. Convert the byte total to mebibytes with integer division (`$((bytes / 1048576))`) and print it alongside the byte count.
3. Add a guardrail: print a warning when the directory holds more than 100 files, the kind of check a real backup script uses to catch a mistakenly enormous folder.
4. If you installed ShellCheck, run `shellcheck examples/backup_notes.sh` and read any suggestions; then deliberately remove a pair of quotes and watch it flag the bug.

## Navigation

- **Previous day:** Day 11 — Environment Variables and Shell Configuration (`labs/sections/computing-foundations/day-011-environment-variables-and-shell-configuration/`).
- **Next day:** Day 13 — Package Managers: Homebrew, apt, and winget (`labs/sections/computing-foundations/day-013-package-managers-homebrew-apt-and-winget/`).
