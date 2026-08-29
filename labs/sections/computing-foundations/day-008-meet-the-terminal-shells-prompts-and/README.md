# Day 008 lab — Your First Shell Session

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Meet the Terminal: Shells, Prompts, and Commands
- **Day number:** 8 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-008-meet-the-terminal-shells-prompts-and
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-008-meet-the-terminal-shells-prompts-and` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 8's lesson explains what a terminal, a shell, and a command are. This lab
makes it concrete: you run a short **tour of your own shell** that reveals which
shell is running, what your prompt string is, and what a handful of everyday
commands (`pwd`, `echo`, `date`, `whoami`, `history`, `type`) actually print.
Then you fill in a worksheet describing your session in your own words.

## Learning objectives

- Discover which shell you are running and your default shell (`echo $0`, `echo $SHELL`, `ps -p $$`).
- See your raw prompt string (`echo "$PS1"`) and understand what it is.
- Run and read the output of `pwd`, `echo`, `date`, and `whoami`.
- Recall recent commands with `history | tail` and identify a command with `type`.
- Complete a shell script by filling in five well-specified exercises, then verify it with an automated test.

## Prerequisites

- The Day 8 lesson (read it first — it explains every term this lab shows you).
- A terminal: Terminal.app (macOS), any terminal (Linux), or PowerShell/WSL (Windows).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, default shell zsh).
- **Linux** — fully supported (any distribution with bash and standard utilities).
- **Windows** — run the scripts unmodified inside WSL, or type the individual commands from the lesson's hands-on section in PowerShell where equivalents exist.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only *reads* session
information; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard OS utilities only: `ps`, `pwd`, `echo`, `date`, `whoami`, `sed`, `tail`. All preinstalled.

## Free and open-source options

Everything in this lab is free: bash and every command used are open-source or
ship with your OS. No account, API key, or purchase is needed.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-008-meet-the-terminal-shells-prompts-and
```

## File structure

```text
day-008-meet-the-terminal-shells-prompts-and/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── shell_tour.sh                  ← YOUR working file (5 exercises)
│   └── shell-session-worksheet.md     ← worksheet for the practice assignment
├── examples/
│   └── shell_tour.sh                  ← completed reference implementation
├── tests/
│   └── run_tests.sh                   ← automated checks
├── expected-output/
│   ├── sample-macos.txt               ← real captured run (macOS, zsh default)
│   └── FIELDS.md                      ← required sections on every platform
├── requirements/
│   └── README.md                      ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/shell_tour.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/shell_tour.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/shell_tour.sh` — runs the reference tour: prints the running shell (`echo $0`), your default shell (`echo $SHELL`), the shell process (`ps -p $$`), your prompt string (`echo "$PS1"`), then `pwd`, `echo hello`, `date`, `whoami`, a `history | tail` sample, and `type echo`.
- `bash starter/shell_tour.sh` — the same skeleton with five values set to `unknown`; each exercise comment names the exact command to use. Edit the file in any text editor and replace each `unknown` assignment with the command in `$(...)` form.
- `bash tests/run_tests.sh` — runs both scripts and checks: exit code 0, the tour header/footer, every required section, that `echo hello` prints `hello` and `type echo` reports a shell builtin; and (once your starter has no `unknown` left) that the five exercise fields hold real values.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run. A shortened view:

```text
=== Shell Tour ===
Generated on: 2026-07-12

--- Which shell am I running? ---
Current shell (echo $0): examples/shell_tour.sh
Default shell (echo $SHELL): /bin/zsh
Shell process (ps -p $$):
      PID TTY           TIME CMD
    12117 ??         0:00.00 bash examples/shell_tour.sh
...
Echo demo (echo hello): hello
Date (date): Sun Jul 12 13:32:42 IST 2026
User (whoami): you
...
type echo: echo is a shell builtin
=== End of tour ===
```

Your values will differ — that is the point. Note that `echo $0` inside a script
prints the script's name; run `echo $0` **directly in your terminal** to see
your interactive shell (e.g. `-zsh`). [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists exactly which sections must appear on every platform.

## Validation steps

1. Run `bash starter/shell_tour.sh` — it must exit without errors.
2. Confirm **no exercise line reads `unknown`** (the five fields you filled in).
3. Confirm the tour prints your shell, your default shell, `pwd`, `date`, and `whoami`.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `35 checks, 0 failure(s).` (20 strict checks against the
reference tour, and 15 structural checks against your starter — which become 20
strict checks once you have replaced every `unknown`). The command exits 0 on
success and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts only read session information and write nothing
outside their own console output. To reset your work, restore the starter file
from git: `git checkout -- starter/shell_tour.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (empty `$PS1`,
empty history, `$0` showing the script name, WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts run no network calls,
need no elevated privileges, and expose only local session facts — but a shell
profile is mildly identifying, so think before pasting it publicly.

## Extension exercises

1. Run `echo $0` and `echo "$PS1"` **directly in your interactive terminal** (not through the script) and compare the values with the script's output — explain the difference in one sentence.
2. Start a different shell by hand (`bash`, then later `exit`) and re-run `echo $0` inside it; confirm `$SHELL` is unchanged while `$0` now names the shell you started.
3. Open `man ls`, read the descriptions of `-l` and `-a`, quit with `q`, then run `ls -la /` and confirm you can label the command, options, and argument.

## Navigation

- **Previous day:** Day 7 — the final lesson of Week 1.
- **Next day:** Day 9 — the next lesson of Week 2 (to be written).
