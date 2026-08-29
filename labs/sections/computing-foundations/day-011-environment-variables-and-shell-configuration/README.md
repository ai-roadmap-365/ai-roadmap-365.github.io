# Day 011 lab — Explore and Extend Your Environment

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Environment Variables and Shell Configuration
- **Day number:** 11 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-011-environment-variables-and-shell-configuration
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-011-environment-variables-and-shell-configuration` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 11's lesson explains the invisible layer every program inherits from your
shell. This lab makes it concrete and **safe**: you inspect your own
environment, watch an exported variable flow into a child process and *not*
leak back out, define an alias, and see how `PATH` turns a bare command name
into a specific program — all without changing your real setup.

## Learning objectives

- Read the key environment variables `HOME`, `USER`, `SHELL`, and `LANG`.
- Print your `PATH` one directory per line and count its entries.
- Demonstrate that `export` sends a value *down* to a child process and that a
  subshell variable does not leak back into the parent environment.
- Define and run an alias, and resolve a command with `command -v` and `type`.
- Record your environment on a worksheet and design one alias you would use.

## Prerequisites

- The Day 11 lesson (read it first — it explains every idea this lab exercises).
- Days 8–10: comfort opening a terminal and running basic commands.
- A terminal with `bash`: Terminal.app (macOS), any terminal (Linux), or WSL
  (Windows). No programming experience required.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, zsh login shell).
- **Linux** — fully supported (any distribution with `bash`, `tr`, `sed`, `grep`).
- **Windows** — run the scripts unmodified inside WSL; native PowerShell is a
  different shell and is not supported by these bash scripts.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads environment
information; it needs no particular RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard utilities only: `tr`, `sed`, `grep`, `id`, and shell builtins
  (`echo`, `export`, `alias`, `type`, `command`). All preinstalled.

## Free and open-source options

Everything here is free and ships with your OS. No account, API key, or
purchase is needed. The `examples/sample.env` file shows the popular **dotenv**
pattern and mentions **direnv** (a free, open-source tool) as a way to automate
per-project environments — both optional and free.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-011-environment-variables-and-shell-configuration
```

## File structure

```text
day-011-environment-variables-and-shell-configuration/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── inspect_env.sh                 ← YOUR working file (4 exercises)
│   └── env-worksheet.md               ← worksheet for the practice assignment
├── examples/
│   ├── inspect_env.sh                 ← completed reference implementation
│   └── sample.env                     ← safe dotenv example (FAKE values only)
├── tests/
│   └── run_tests.sh                   ← automated checks
├── expected-output/
│   ├── sample-macos.txt               ← real captured run (macOS)
│   └── FIELDS.md                      ← required fields on every platform
├── requirements/
│   └── README.md                      ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/inspect_env.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/inspect_env.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/inspect_env.sh` — the reference script. It prints `HOME`,
  `USER`, `SHELL`, and `LANG`; lists `PATH` one directory per line and counts
  it; exports a variable inside a subshell and proves a child inherits it while
  the parent does not; defines and calls an alias; and resolves `ls` with
  `command -v` and `cd` with `type`. Everything runs in a child process and a
  subshell, so your real environment is untouched.
- `bash starter/inspect_env.sh` — the same script with four exercises to fill
  in. Each comment names the exact command; replace each numbered placeholder.
- `bash tests/run_tests.sh` — runs the reference (strict checks) and your
  starter (structure only until you finish, then strict), confirming the fields
  print, the export reaches the child, and the subshell variable does **not**
  leak.

## Expected output

See [`expected-output/sample-macos.txt`](expected-output/sample-macos.txt) — a
real captured run:

```text
=== Environment Inspection ===
HOME:  <home>
USER:  you
SHELL: /bin/zsh
LANG:  C.UTF-8
PATH directories (one per line):
  - /usr/local/bin
  - /usr/bin
  - /bin
  - /usr/sbin
  - /sbin
PATH contains 5 directories.
--- Subshell variable demo ---
  child process sees demo_var = hello from a subshell
  after subshell, demo_var = '<empty, did not leak>'
--- Alias demo ---
  alias greet ran: hello
--- Command resolution ---
  command -v ls  -> /bin/ls
  type cd        -> cd is a shell builtin
=== End of inspection ===
```

Your `HOME`, `USER`, `LANG`, and `PATH` will differ — that is the point. The
sample was captured with a short representative `PATH` for readability; a real
machine's `PATH` is often longer. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists the fields that must appear on every platform.

## Validation steps

1. Run `bash starter/inspect_env.sh` after filling the exercises — it must exit
   without errors and print no `REPLACE_ME` text.
2. Confirm the child process line shows `hello from a subshell`.
3. Confirm the `after subshell` line shows `<empty, did not leak>` — the
   variable stayed inside the subshell.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `13 checks, 0 failure(s).`
(12 strict checks against the reference script plus 1 structural check on the
starter). Once you replace all four placeholders, the starter is held to the
same strict standard and the count rises to `24 checks, 0 failure(s).` The
command exits 0 on success and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts only read information and write nothing outside
their own console output. The extension exercise in the lesson creates a
`~/demo-bin` directory and removes it in the same snippet. To reset your work,
restore the starter from git: `git checkout -- starter/inspect_env.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (variable
expansion, alias expansion in scripts, subshell leakage, `command -v` misses,
spaces around `=`, and WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts hold no real
secrets, need no `sudo`, and make no network calls; the only example key is an
obvious fake, and a real `.env` must always be listed in `.gitignore`.

## Extension exercises

1. Prepend a personal directory to `PATH` inside a subshell, drop a tiny script
   named after a common command into it, and use `command -v` to watch your
   copy win because it is searched first (the lesson's extension challenge walks
   through this).
2. Load `examples/sample.env` into a subshell with `set -a; source examples/sample.env; set +a`
   and confirm with `printenv APP_ENV` that the values arrived — then note why
   you would never do this with a *real* committed `.env`.
3. Add a `PATH contains N directories` style summary line for a second variable
   of your choice, and extend `tests/run_tests.sh` to check for it.

## Navigation

- **Previous day:** Day 10 — Working with Text: cat, grep, sed
  (`labs/sections/computing-foundations/day-010-working-with-text-cat-grep-sed/`).
- **Next day:** Day 12 — Shell Scripting: Variables, Loops, and Conditionals
  (`labs/sections/computing-foundations/day-012-shell-scripting-variables-loops-and-conditionals/`, to be written).
