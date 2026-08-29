# Day 010 lab — Pipelines on a Real Log

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Working with Text: cat, grep, sed, and Pipes
- **Day number:** 10 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-010-working-with-text-cat-grep-sed
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-010-working-with-text-cat-grep-sed` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 10's lesson teaches the Unix philosophy: small tools, each doing one job,
composed with pipes. This lab makes it concrete. You are handed a small web
**access log** and answer real questions about it — how much traffic, from
whom, how many errors, over how many pages — by building four **pipelines**
that chain `awk`, `grep`, `sort`, `uniq`, and `wc`. This is exactly the shape
of data-cleaning and log-analysis work you will do constantly.

## Learning objectives

- Read a pipeline left to right and name what each stage does.
- Extract a single column from structured text with `awk`.
- Count, sort, and de-duplicate lines with `sort`, `uniq -c`, and `wc`.
- Build the classic "top-N" pipeline: `sort | uniq -c | sort -rn | head`.
- Filter rows by a field value (all the 404 responses) and count them.
- Run an automated test script and interpret its pass/fail output.

## Prerequisites

- The Day 10 lesson (read it first — it explains every tool this lab uses).
- Day 8 (the terminal) and Day 9 (the filesystem) for basic command comfort.
- A terminal: Terminal.app (macOS), any terminal (Linux), or WSL (Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution; uses only standard tools).
- **Windows** — use **WSL** (`wsl --install`, then Ubuntu) and follow the
  Linux path. Native PowerShell is not covered — its text tools differ.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab reads one ~4 KB text
file; it needs no minimum RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard text tools: `cat`, `grep`, `sed`, `awk`, `sort`, `uniq`, `wc`,
  `head`, `tr`. All preinstalled on macOS and Linux.

## Free and open-source options

Everything here is free and open source or ships with your OS. No account, API
key, or purchase is needed. The lesson mentions `ripgrep` (`rg`) as a fast,
free alternative to `grep`, but this lab never requires it.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-010-working-with-text-cat-grep-sed
```

## File structure

```text
day-010-working-with-text-cat-grep-sed/
├── README.md                              ← you are here
├── metadata.yml                           ← machine-readable lab metadata
├── starter/
│   ├── analyze_log.sh                     ← YOUR working file (4 exercises)
│   └── text-pipelines-worksheet.md        ← record your findings here
├── examples/
│   ├── analyze_log.sh                     ← completed reference implementation
│   └── samples/
│       └── access.log                     ← the sample web log (40 lines, synthetic)
├── tests/
│   └── run_tests.sh                       ← automated checks (known-correct counts)
├── expected-output/
│   ├── analyze_log.txt                    ← real captured run of the reference script
│   ├── run_tests.txt                      ← real captured test run
│   └── FIELDS.md                          ← the known-correct answers + platform notes
├── requirements/
│   └── README.md                          ← dependency statement (none beyond the OS)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. Peek at the data (first few lines of the log)
head examples/samples/access.log

# 2. See the finished result first
bash examples/analyze_log.sh

# 3. Your task: complete the four pipelines in the starter, then run it
bash starter/analyze_log.sh

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `head examples/samples/access.log` — prints the first 10 lines so you can
  see the log's shape: `IP - - [timestamp] "METHOD path HTTP/1.1" status size`.
- `bash examples/analyze_log.sh` — runs the reference solution. It reports the
  total request count (`wc -l`), the top 5 client IPs
  (`awk | sort | uniq -c | sort -rn | head`), the number of 404 responses
  (`awk '$9 == 404' | wc -l`), and the number of unique paths
  (`awk '{print $7}' | sort -u | wc -l`).
- `bash starter/analyze_log.sh` — the same report with four pipelines left for
  you to build. Each exercise comment names the exact tools to use. Replace
  every `REPLACE_ME`.
- `bash tests/run_tests.sh` — recomputes the correct answers from the raw log,
  checks the reference script prints them, and — once your starter has no
  `REPLACE_ME` left — holds your script to the same known-good numbers.

## Expected output

Running the reference script prints (see
[`expected-output/analyze_log.txt`](expected-output/analyze_log.txt)):

```text
=== Log Analysis Report ===
Log file: examples/samples/access.log
Total requests: 40
Top 5 IP addresses (count  IP):
  10 10.0.0.14
   7 10.0.0.7
   6 10.0.0.99
   5 192.168.1.23
   5 192.168.1.10
404 responses: 7
Unique paths: 13
...
=== End of report ===
```

The counts are fixed because the sample log is committed and unchanging.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists every
known-correct answer and the one place output can differ between macOS and
Linux (the order of two IPs that tie at 5 requests each).

## Validation steps

1. Run `bash starter/analyze_log.sh` — it must exit without errors.
2. Confirm **no line prints `REPLACE_ME`**.
3. Confirm your numbers match: 40 requests, top IP `10.0.0.14`, 7 404s, 13
   unique paths.
4. Fill in [`starter/text-pipelines-worksheet.md`](starter/text-pipelines-worksheet.md).
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `16 checks, 0 failure(s).` while the starter is still
unfinished (the reference script is checked strictly; your starter is checked
for structure only until you complete it). Once you have replaced every
`REPLACE_ME`, the same command runs `20 checks, 0 failure(s).` The command
exits 0 on success and non-zero on any failure, so it can run in CI.

## Cleanup

Nothing to clean up: the scripts only read the sample log and print to the
console — no files are created or changed. To reset your work, restore the
starter from git: `git checkout -- starter/analyze_log.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (wrong field
number, `uniq` without `sort`, 404 miscounts, tie-order differences, WSL
notes).

## Security notes

See [security.md](security.md). Short version: the scripts run no network
calls, need no elevated privileges, and read only synthetic data invented for
this lab — the IPs are private-range addresses that never appear on the public
internet, and there is no personal data.

## Extension exercises

1. **Status breakdown.** Print how many responses had each status code:
   `awk '{print $9}' examples/samples/access.log | sort | uniq -c | sort -rn`.
   How many were successful (200) versus errors (4xx/5xx)?
2. **Busiest path.** Adapt the top-IP pipeline to field 7 to find the most
   requested path instead of the most active IP.
3. **Total bytes served.** The response size is field 10. Sum it with
   `awk '{sum += $10} END {print sum}'` — one line, no pipe needed.
4. **Substitution with `sed`.** Pipe the unique-paths list through
   `sed 's#^/##'` to strip the leading slash from each path, and notice how
   `sed` transforms a stream without touching the file.

## Navigation

- **Previous day:** Day 9 — Navigating the Filesystem: Paths, Files, and
  Permissions (`labs/sections/computing-foundations/day-009-navigating-the-filesystem-paths-files-and/`).
- **Next day:** Day 11 — Environment Variables and Shell Configuration
  (`labs/sections/computing-foundations/day-011-environment-variables-and-shell-configuration/`, to be written).
