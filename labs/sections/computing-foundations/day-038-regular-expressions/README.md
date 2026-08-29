# Day 038 lab — Match Patterns with grep and sed

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Regular Expressions
- **Day number:** 38 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-038-regular-expressions
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-038-regular-expressions` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 38's lesson builds regex syntax from the ground up. This lab makes it real:
you run `grep -E` and `sed -E` against a small, clearly synthetic sample file
that mixes emails, dates, phone-ish numbers, and access-log lines with IP
addresses and status codes. You extract, count, and reformat text — and confirm
your patterns are right by matching known counts.

## Learning objectives

- Extract matches from text with `grep -E -o`.
- Count matching lines with `grep -E -c` (and invert with `-v`).
- Write patterns for emails, dates, IP addresses, and status codes, and reason
  about what they do and do not match.
- Capture fields and reformat them with `sed -E` and backreferences (`\1`, `\2`).
- Run an automated test script and read its pass/fail output.

## Prerequisites

- The Day 38 lesson (read it first — it teaches every metacharacter used here).
- Comfort running basic shell commands (Days 8–14).
- A terminal with `grep` and `sed` (preinstalled on macOS and Linux).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, BSD grep/sed).
- **Linux** — fully supported (GNU grep/sed). Output is byte-for-byte identical.
- **Windows** — use WSL or Git Bash and follow the Linux path.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads a small text
file and prints to the terminal; it needs no particular RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `grep` and `sed`, both supporting the `-E` extended-regex flag. Preinstalled
  on macOS and Linux.

## Free and open-source options

Everything in this lab is free and ships with your OS. No account, API key, or
purchase is needed; nothing reaches the network. See the lesson for free regex
testers (such as regex101) you can use in a browser to build patterns
interactively.

## Installation

None. Copy this directory (or clone the repository) and you are ready:

```bash
cd labs/sections/computing-foundations/day-038-regular-expressions
```

## File structure

```text
day-038-regular-expressions/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── regex_drills.sh             ← YOUR working file (4 exercises)
│   └── regex-worksheet.md          ← worksheet for the practice assignment
├── examples/
│   ├── regex_drills.sh             ← completed reference drills
│   └── samples/
│       └── data.txt                ← the synthetic sample you match against
├── tests/
│   └── run_tests.sh                ← automated checks against known counts
├── expected-output/
│   ├── drills-output.txt           ← real captured run of the example drills
│   ├── test-output.txt             ← real captured run of the tests
│   └── FIELDS.md                   ← the exact expected counts, all platforms
├── requirements/
│   └── README.md                   ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished drills first
bash examples/regex_drills.sh

# 2. Your task: fill in the 4 exercises in the starter, then run it
bash starter/regex_drills.sh

# 3. Check your work against the known counts
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/regex_drills.sh` — runs four worked drills against
  `examples/samples/data.txt`: extract emails (`grep -E -o`), count dated lines
  (`grep -E -c`), extract IP-ish addresses (`grep -E -o`), and reformat a date
  with `sed -E` backreferences. Each pattern is explained line by line in the
  script's comments.
- `bash starter/regex_drills.sh` — the same idea with four numbered exercises to
  complete: match phone-ish numbers, extract status codes from the log lines,
  count non-comment lines, and reorder a day-first date with capture groups.
  Each has a placeholder (`WRITE_YOUR_PATTERN_HERE`) and a hint.
- `bash tests/run_tests.sh` — runs the reference patterns against the sample and
  checks the counts (6 emails, 9 dated lines, 5 IPs, 5 status codes, 16
  non-comment lines) and the `sed` reformat, then confirms the example script
  exits cleanly.

## Expected output

See [`expected-output/drills-output.txt`](expected-output/drills-output.txt) — a
real captured run. The key numbers (exact, because the sample is fixed):

```text
emails extracted ............ 6
lines with a YYYY-MM-DD date . 9
IP-ish addresses ............ 5
status codes (log lines) .... 5   (200, 401, 200, 404, 500)
non-comment lines ........... 16
sed reformat 2026/07/12 ..... 2026-07-12
```

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the same counts
and confirms they are identical on macOS and Linux.

## Validation steps

1. Run `bash examples/regex_drills.sh` — it must print six emails, the number
   `9`, five IP addresses, and `2026-07-12`.
2. Complete the four exercises in `starter/regex_drills.sh` (replace every
   `WRITE_YOUR_PATTERN_HERE`) and run it — Exercise 1 should print 5 phone
   numbers, Exercise 2 the five status codes, Exercise 3 the count `16`, and
   Exercise 4 `2026-07-12`.
3. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `8 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It uses only the committed
sample and makes no network calls.

## Cleanup

Nothing to clean up: the scripts only read the sample and print to the terminal.
To reset your work, restore the starter files from git:
`git checkout -- starter/regex_drills.sh starter/regex-worksheet.md`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: missing `-E`,
BSD-vs-GNU `sed` differences on macOS/Linux, `\d` not matching, and patterns
that match too much.

## Security notes

See [security.md](security.md). Short version: the scripts read a synthetic
local file, make no network calls, need no elevated privileges, and never
execute matched text — a habit you should keep (never `eval` what a regex
extracts).

## Extension exercises

1. Replace a broad `.*` with a narrow class. On a line like
   `<a href="one"> and <b href="two">`, compare `grep -E -o '<.*>'` (one greedy
   match) with `grep -E -o '<[^>]*>'` (two tag matches) and explain the
   difference in terms of backtracking.
2. Write a single pattern that matches only *valid-looking* status codes in the
   200–599 range (`[2-5][0-9][0-9]`) and confirm it still finds all five.
3. Add a fifth drill that redacts every email address in the sample, replacing
   the local part with `***` using `sed -E` and a capture group for the domain.

## Navigation

- **Previous day:** Day 37 — Debuggers, Linters, and Formatters
  (`labs/sections/computing-foundations/day-037-debuggers-linters-and-formatters/`).
- **Next day:** Day 39 — Data Storage: Files, Databases, Object Storage, and
  Caches (`labs/sections/computing-foundations/day-039-data-storage-files-databases-object-storage/`).
