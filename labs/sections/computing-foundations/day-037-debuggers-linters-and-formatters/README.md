# Day 037 lab — Lint and Format a Script

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Debuggers, Linters, and Formatters
- **Day number:** 37 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-037-debuggers-linters-and-formatters
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-037-debuggers-linters-and-formatters` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 37's lesson explains debuggers, linters, and formatters. This lab makes
two of them concrete on a real, deliberately flawed shell script: you run a
small quality pipeline — a syntax check (`bash -n`), a lint pass (ShellCheck,
if installed), and a formatting check (trailing whitespace and tabs) — and
learn to read each finding for what it is. It is a miniature of the automated
quality gate the Week 6 project builds.

## Learning objectives

- Run `bash -n` and explain what a syntax check does and does not prove.
- Run a lint pass and name the real bugs a shell linter catches (unquoted
  variables, unused variables, fragile `[ ]` tests).
- Run a formatting check and distinguish layout issues from correctness bugs.
- Experience graceful degradation: a tool that reports clearly when an
  optional dependency (ShellCheck) is absent instead of failing.
- Complete a working shell script by filling in four well-specified exercises.

## Prerequisites

- The Day 37 lesson (read it first — it explains every tool this lab runs).
- Day 36 (a configured editor) and basic shell scripting from Week 2.
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL/Git Bash (Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS, Apple Silicon).
- **Linux** — fully supported (any distribution with `bash`, `grep`, `sed`).
- **Windows** — run the scripts unmodified inside WSL or Git Bash.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads and
analyzes small text files; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard utilities: `grep`, `sed`, `printf`, `mktemp` — all preinstalled.
- **Optional:** ShellCheck (free) enables the lint step; the lab works without it.

## Free and open-source options

Everything here is free and open source. `bash` and every utility ship with
your OS, and ShellCheck — the one optional extra — is free and open source
(see `requirements/README.md`). No account, API key, or purchase is needed.

## Installation

None required. Copy this directory (or clone the repository) and change into it:

```bash
cd labs/sections/computing-foundations/day-037-debuggers-linters-and-formatters
```

To enable the lint step, optionally install ShellCheck (free):
`brew install shellcheck` (macOS) or `sudo apt install shellcheck` (Debian/Ubuntu).

## File structure

```text
day-037-debuggers-linters-and-formatters/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── quality_check.sh            ← YOUR working file (4 exercises)
│   └── quality-worksheet.md        ← worksheet for the practice assignment
├── examples/
│   ├── quality_check.sh            ← completed reference quality gate
│   └── samples/
│       └── buggy.sh                ← deliberately flawed sample to analyze
├── tests/
│   └── run_tests.sh                ← automated checks
├── expected-output/
│   ├── quality-check-no-shellcheck.txt   ← real captured run (no shellcheck)
│   ├── tests.txt                          ← real captured test run
│   └── FIELDS.md                          ← what to look for; platform notes
├── requirements/
│   └── README.md                   ← dependency + optional ShellCheck install
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. Look at the flawed sample and confirm the shell can parse it
cat examples/samples/buggy.sh
bash -n examples/samples/buggy.sh          # no output = valid syntax

# 2. Run the full quality check (syntax + lint + formatting)
bash examples/quality_check.sh examples/samples/buggy.sh

# 3. Your task: complete the four exercises in the starter, then run it
bash starter/quality_check.sh examples/samples/buggy.sh

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash -n examples/samples/buggy.sh` — the shell's built-in syntax check:
  parses the script without running it; prints nothing and exits 0 when valid.
- `bash examples/quality_check.sh <file>` — runs three checks and prints a
  report: (1) `bash -n` syntax, (2) ShellCheck if installed — otherwise a
  clear SKIP describing what it would catch, (3) a `grep`-based formatting
  check for trailing whitespace and tab indentation. It always exits 0.
- `bash starter/quality_check.sh <file>` — the same skeleton with four checks
  left as numbered exercises; each comment names the exact command to add.
- `bash tests/run_tests.sh` — verifies `bash -n` flags a broken variant, the
  formatting check flags trailing whitespace and tabs, the quality check exits
  0, and the lint step skips gracefully (or runs) depending on ShellCheck.

## Expected output

See [`expected-output/quality-check-no-shellcheck.txt`](expected-output/quality-check-no-shellcheck.txt)
— a real captured run on a machine without ShellCheck:

```text
=== Quality check: examples/samples/buggy.sh ===

[1/3] Syntax check (bash -n)...
  ok: script is syntactically valid.

[2/3] Lint check (shellcheck)...
  SKIP: shellcheck is not installed on this machine.
        Install it (free) to catch bugs like:
        - SC2086: unquoted $variable may word-split or glob
        - SC2034: variable appears unused
        - using [ ] where [[ ]] is safer
        See requirements/README.md for install instructions.

[3/3] Formatting check (trailing whitespace / tabs)...
  FAIL: found 1 line(s) with trailing whitespace.
    13:echo "Hi, $name"   
  FAIL: found 1 line(s) containing tab indentation.
    14:	echo "all done"

Summary: syntax OK; lint skipped (shellcheck absent); formatting issues found.
```

With ShellCheck installed, step [2/3] shows its real findings instead of the
SKIP block. See [`expected-output/FIELDS.md`](expected-output/FIELDS.md) for
platform notes.

## Validation steps

1. Run `bash examples/quality_check.sh examples/samples/buggy.sh` — it must
   print all three sections and exit 0.
2. Confirm the formatting section reports the trailing-whitespace line (13)
   and the tab line (14).
3. Complete the four exercises in `starter/quality_check.sh` and run it; its
   formatting section should now match the reference.
4. Fill in `starter/quality-worksheet.md` completely.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `9 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It uses no network.

## Cleanup

Nothing to clean up: the scripts write nothing outside their own console
output, and the tests remove their temporary directory automatically. If your
editor stripped the intentional flaws from the sample, restore it with
`git checkout -- examples/samples/buggy.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (empty `bash -n`
output, missing ShellCheck, invisible trailing whitespace, editors that strip
it, permission messages, Windows notes).

## Security notes

See [security.md](security.md). Short version: the scripts only *analyze*
local files (they never run the sample), make no network calls, and need no
elevated privileges — modelling the rule to lint and read untrusted code
rather than run it.

## Extension exercises

1. Install ShellCheck (free) and re-run the quality check; look up two SC
   codes (e.g. `SC2086`, `SC2034`) and read their explanations.
2. Fix `buggy.sh`: quote the variables, remove or use the unused variable,
   switch `[ ]` to `[[ ]]`, and confirm ShellCheck then reports nothing.
3. Extend the formatting check to also flag lines longer than 100 characters
   (`awk 'length > 100'`), and add a test for it in `tests/run_tests.sh`.

## Navigation

- **Previous day:** Day 36 — Choosing and Configuring a Code Editor (`labs/sections/computing-foundations/day-036-choosing-and-configuring-a-code-editor/`).
- **Next day:** Day 38 — Regular Expressions (`labs/sections/computing-foundations/day-038-regular-expressions/`, to be written).
