# Day 045 lab — Build a Text Report

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Strings and Text Processing
- **Day number:** 45 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-045-strings-and-text-processing
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-045-strings-and-text-processing` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 45's lesson explains how Python treats text: strings as immutable
sequences, slicing, the essential methods, and f-strings. This lab makes it
concrete. You take a fixed block of sample text and, using only string methods
and f-strings, produce a clean **text report**: a title-cased heading, line and
word and character counts, the number of unique words, the single most common
word, and a neatly aligned statistics table. It is the shape of nearly every
text-cleaning task you will ever write — count, normalize, summarize, format.

## Learning objectives

- Read a text file into a string with an explicit UTF-8 encoding.
- Split text into words and count them with a plain dictionary.
- Normalize words with `strip`, `lower`, and friends (methods return new
  strings; the original is never changed).
- Slice strings with positive and negative indices, including reversal
  (`s[::-1]`).
- Build formatted output with f-strings and format specs (`:<20`, `:>10`,
  `:.1f`).
- Run an automated test script and read its pass/fail output.

## Prerequisites

- The Day 45 lesson (read it first — it explains every string feature this lab
  uses).
- Python 3 installed (`python3 --version` reports a 3.x version).
- No prior text-processing experience; every step is spelled out.

## Supported operating systems

- **macOS** — fully supported (captured on macOS with Python 3.14).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — run inside WSL for the `bash` test step, or run the Python
  program directly in PowerShell and check the numbers against
  `expected-output/FIELDS.md`.

## Hardware requirements

Any computer that can run Python 3. The program reads one small text file and
prints a report; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; standard library only — `pathlib`).
- `bash` for the test runner (preinstalled on macOS and Linux).

## Free and open-source options

Everything here is free and open source: Python and its standard library ship
at no cost, and no account, API key, or third-party package is required.

## Installation

None. Clone the repository (or copy this directory) and change into it:

```bash
cd labs/sections/programming-with-python/day-045-strings-and-text-processing
```

## File structure

```text
day-045-strings-and-text-processing/
├── README.md                      ← you are here
├── metadata.yml                   ← machine-readable lab metadata
├── starter/
│   ├── text_report.py             ← YOUR working file (5 exercises)
│   └── strings-worksheet.md       ← record a word count, a slice, an f-string
├── examples/
│   ├── text_report.py             ← completed reference implementation
│   └── sample.txt                 ← the fixed text the report is built from
├── tests/
│   └── run_tests.sh               ← automated checks (exact counts + assertions)
├── expected-output/
│   ├── sample-run.txt             ← a real captured run
│   └── FIELDS.md                  ← what a correct run prints, line by line
├── requirements/
│   └── README.md                  ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
python3 examples/text_report.py

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/text_report.py

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/text_report.py` — runs the reference program: reads
  `examples/sample.txt`, title-cases the first line, splits the text into
  words, counts them in a dictionary, finds the most common word, and prints
  an aligned statistics table using f-string format specs.
- `python3 starter/text_report.py` — the same program with five pieces left as
  numbered exercises (read the file, build the heading, count words, find the
  most common word, print the table). Each exercise comment names the exact
  method or expression to use. Edit only those lines.
- `bash tests/run_tests.sh` — runs the reference program and checks the exact
  counts (9 lines, 105 words, 556 characters, 66 unique words, `"river"` 11
  times), then confirms a set of slicing and string-method facts directly with
  `python3`, and finally checks that the starter still runs.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run:

```text
============================================
          The River And The Reader          
============================================

Preview:  the river and the reader A river starts ...
Heading reversed:  redaeR ehT dnA reviR ehT
First / last body word:  'river' / 'you'

Statistic                Value
------------------------------
Lines                        9
Words                      105
Characters                 556
Unique words                66

Most common word:  "river" (11 times, 10.5% of words)
```

Because the program reads a fixed sample and does no other I/O, this output is
the same on every platform. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
describes each line.

## Validation steps

1. Run `python3 starter/text_report.py` after finishing the exercises — it must
   print the full report with no error.
2. Confirm the four counts match the reference: 9 lines, 105 words, 556
   characters, 66 unique words.
3. Confirm the most common word line reads `"river" (11 times, 10.5% of words)`.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `9 checks, 0 failure(s).` The script exits 0 on success
and non-zero on any failure, so it can run in CI. It uses no network.

## Cleanup

Nothing to clean up: the program only reads the local sample and prints to the
terminal. To reset your work, restore the starter from git:
`git checkout -- starter/text_report.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — Python not found, encoding
errors, f-string quoting problems, off-by-one slices, and mis-aligned columns.

## Security notes

See [security.md](security.md). Short version: the program reads one local
file, makes no network calls, writes nothing, and needs no elevated
privileges.

## Extension exercises

1. Add a **line-length** stat: the longest line and its length, found with
   `max(lines, key=len)` and an f-string that prints both.
2. Print the **top three** words instead of just the most common one (sort
   `counts.items()` by count, then slice `[:3]`).
3. Add a `--upper` style toggle by reading `sys.argv`: when present, print the
   heading with `.upper()` instead of `.title()`, and note in the worksheet how
   the two methods differ.

## Navigation

- **Previous day:** Day 44 — Variables and Types
  (`labs/sections/programming-with-python/day-044-variables-and-types/`,
  to be written).
- **Next day:** Day 46 — Numbers, Math, and Precision
  (`labs/sections/programming-with-python/day-046-numbers-math-and-precision/`,
  to be written).
