# Day 065 lab — Wrangling Messy Data

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** CSV and JSON in the Real World
- **Day number:** 65 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-065-csv-and-json-in-the-real
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-065-csv-and-json-in-the-real` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 64 taught you to open a file and read its bytes. Today the bytes have
to *mean* something to a program that did not write them. This lab hands
you a deliberately messy CSV — one that carries a byte-order mark, a comma
inside a quoted field, a newline inside a quoted field, doubled quotes, an
empty field, and a ragged row — plus a small JSON config, and asks you to
get every record out intact.

You will first prove that the obvious approach, `line.split(',')`, mangles
the file (and, more unsettling, that it mangles one line while still
producing the right number of fields). Then you will parse it properly
with `csv.DictReader`, clean it against the config, and round-trip it to
JSON, to JSON Lines, and back to a well-formed CSV, asserting at each step
that nothing was lost. Finally you will build the quoting state machine
from scratch — about fifty lines — and check that it agrees with the
standard library on every row, including a European semicolon dialect.

That last step is the point of the day. CSV and JSON stop being magic once
you have implemented the rule that makes them work.

## Learning objectives

- Demonstrate concretely why splitting a CSV line on commas is a bug, and
  recognise the case where it silently produces wrong data.
- Read a real-world CSV correctly with `csv.DictReader`, using
  `encoding='utf-8-sig'` and `newline=''`, and explain what each does.
- Handle the ragged row, the empty field, and the missing value honestly
  rather than by accident.
- Serialize records to JSON and to JSON Lines, and prove the round trip is
  lossless with an assertion rather than by eye.
- Implement the RFC 4180 quoting state machine from first principles and
  verify it against the standard library.

## Prerequisites

- The Day 65 lesson (read it first — it walks these exact traps).
- Day 64: opening files with `open()` and `pathlib`, reading and writing
  text, and encodings.
- Days 57–63: functions, dicts and lists, comprehensions, modules and
  imports, the standard library, and small-program design.
- A text editor and a terminal. No experience beyond this course is
  assumed; classes, exceptions in depth, and type hints are not needed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3`. Windows is where the `newline=''` argument stops being
  theoretical: without it you get a blank line between every written
  record. Every file here passes it, so behaviour is identical everywhere.

## Hardware requirements

Any computer that runs Python 3. The input file is 288 bytes; the whole
lab reads and writes about two kilobytes. No special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `csv`, `json`, `pathlib`, and `io`. Nothing to
  install. See [`requirements/README.md`](requirements/README.md).
- Optional: `xxd` (or `od`) to look at the byte-order mark as raw bytes.

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed. The
`csv` and `json` modules are part of Python itself — the same code that
`pandas` and every data tool ultimately sit on top of or reimplement.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-065-csv-and-json-in-the-real
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-065-csv-and-json-in-the-real/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── data/
│   ├── messy_orders.csv            ← the messy input (byte-order mark and all)
│   └── config.json                 ← columns, defaults, encoding, output names
├── starter/
│   ├── wrangle.py                  ← YOUR working file (exercises 1–4)
│   └── csv_field_parser.py         ← YOUR working file (exercise 5: the state machine)
├── examples/
│   ├── wrangle.py                  ← complete reference pipeline
│   └── csv_field_parser.py         ← complete reference parser
├── tests/
│   └── run_tests.sh                ← behaviour checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt              ← real captured session with the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

Running the pipeline also creates `out/` with the three generated files.
It is safe to delete at any time.

## How to run

From this directory:

```bash
# 1. Look at the enemy. Three invisible bytes, then a 7-line file of 6 records.
head -c 3 data/messy_orders.csv | xxd
cat data/messy_orders.csv

# 2. See the finished pipeline: naive split failing, csv.DictReader working,
#    cleaning, and three lossless round trips.
python3 examples/wrangle.py

# 3. See the from-scratch quoting state machine agree with the csv module.
python3 examples/csv_field_parser.py

# 4. Inspect what was written.
cat out/orders.jsonl
cat out/orders-clean.csv

# 5. Your task: complete exercises 1-4 in starter/wrangle.py, then run it.
python3 starter/wrangle.py

# 6. Then complete exercise 5 in starter/csv_field_parser.py and run it.
python3 starter/csv_field_parser.py

# 7. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `head -c 3 data/messy_orders.csv | xxd` — prints the first three bytes as
  hex. You should see `efbb bf`: the UTF-8 byte-order mark that Excel
  writes and that silently corrupts your first column name if you decode
  the file as plain `utf-8`.
- `python3 examples/wrangle.py` — runs the whole reference pipeline in four
  labelled stages: naive splitting (and its failures), `csv.DictReader`
  (and its successes), cleaning against `config.json`, then writing
  JSON / JSON Lines / CSV and asserting each reads back equal to what went
  in. It creates `out/`.
- `python3 examples/csv_field_parser.py` — parses the messy file twice,
  once with the from-scratch state machine and once with `csv.reader`, and
  prints each row plus whether the two agree. It exits 0 only if they do.
- `cat out/orders.jsonl` — five lines, one self-contained JSON object each.
  Notice the newline inside order 1002's notes appears as `\n`, an escape
  *inside* the line, which is exactly why JSON Lines is safe.
- `python3 starter/wrangle.py` and `python3 starter/csv_field_parser.py` —
  the same programs, driven by the functions you write.
- `bash tests/run_tests.sh` — 26 behaviour checks: the input file really
  has the traps described, the reference handles every one of them, the
  round trips really are lossless, and your from-scratch parser really
  agrees with the standard library. Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session. The heart of it:

```text
$ python3 examples/wrangle.py
=== 1. naive line.split(',') ===
lines whose field count is not 5: 3
  line 2: 6 fields
  line 4: 2 fields
  line 7: 3 fields
naive row for order 1001: ['1001', '"Ada Lovelace"', '"widget', ' large"', 'Priority shipping', '49.50']
naive row for order 1003: ['1003', '"Alan ""Turing"" Jr."', 'monitor', 'Fragile', '240.00']
(order 1003 has 5 fields, so the count check passes — and the data is still wrong)

=== 2. csv.DictReader ===
records parsed: 5
first key is 'order_id' (byte-order mark stripped): True
order 1002 notes: 'Leave at door.\nRing the bell twice.'
order 1003 customer: 'Alan "Turing" Jr.'
order 1005 (ragged) total: None
```

and, at the end:

```text
round trip lossless: JSON yes, JSONL yes, CSV yes
```

Everything is deterministic, so your output will match.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour of every function on every platform.

## Validation steps

1. `head -c 3 data/messy_orders.csv | xxd` prints `efbb bf` — the file
   really does begin with a byte-order mark.
2. `python3 examples/wrangle.py` exits 0 and ends with
   `round trip lossless: JSON yes, JSONL yes, CSV yes`.
3. `python3 examples/csv_field_parser.py` ends with `agree on every row: True`
   and exits 0.
4. `wc -l data/messy_orders.csv` reports 7 lines while the pipeline reports
   5 records — the quoted newline accounts for the difference.
5. `cat out/orders.jsonl` shows exactly 5 lines, each a complete JSON
   object, with order 1002's newline written as the escape `\n`.
6. Complete exercises 1–5 in `starter/`, run both starter programs, and
   confirm they match the reference output.
7. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished:
`26 checks, 0 failure(s).` Once you complete all five exercises, the suite
holds your files to the same strict standard as the reference, giving
`34 checks, 0 failure(s).` The command exits 0 on success and non-zero on
any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The lab writes only into `out/` inside this directory:

```bash
rm -rf out
```

To reset your work, restore the starter from git:
`git checkout -- starter/`. The test runner removes its own temporary
directory automatically.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: the
`KeyError` caused by a byte-order mark, blank lines between written
records, a record split in two by a quoted newline, `TypeError: Object of
type ... is not JSON serializable`, `'NoneType' object has no attribute
'strip'` on the ragged row, `JSONDecodeError` on a blank JSON Lines line,
and the three usual reasons a hand-built parser disagrees with the `csv`
module.

## Security notes

See [security.md](security.md). Short version: parsed data is **data,
never code** — use `float()` and `int()`, never `eval()`; `json.loads` is
safe by design while `pickle` is not. A field can contain a comma, a
newline, a quote, or a megabyte of text, so escape properly at every
downstream boundary (parameterised SQL, `subprocess` argument lists,
HTML escaping), watch for spreadsheet formula injection in exported
fields, and keep real personal data out of version control.

## Extension exercises

1. **Sniff the dialect.** Write a small script that uses `csv.Sniffer` to
   detect the delimiter of a file, then run it on `data/messy_orders.csv`
   and on a semicolon-delimited copy you make yourself. Note where the
   sniffer guesses well and where it needs a bigger sample.
2. **Break the round trip on purpose.** Add a record whose `total` is
   `0.1` and one whose `order_id` is a 20-digit number, then re-run the
   assertions. Explain in a comment what survives, what does not, and why
   the CSV round trip is the one that needs `float()` on the way back in.
3. **Stream instead of loading.** Rewrite the JSON Lines reader so it
   yields one record at a time instead of building a list, and describe in
   a comment what changes for a 10 GB file. This is the reason training
   and evaluation data ships as JSONL.
4. **Extend the state machine.** Add support for a `quoting=NONE` style
   backslash escape (`\,` meaning a literal comma) as a fifth state, and
   add a test that your version and the `csv` module still agree on files
   that use no backslashes at all.

## Navigation

- **Previous day:** Day 64 — Reading and Writing Files
  (`labs/sections/programming-with-python/day-064-reading-and-writing-files/`).
- **Next day:** Day 66 — Exceptions and Error Handling Strategy
  (`labs/sections/programming-with-python/day-066-exceptions-and-error-handling-strategy/`,
  to be written).
- **Week 10 project:** the Expense Tracker — an expense tool with CSV
  import and export, category handling, and monthly summary reports. The
  import path you build there is exactly the parsing and cleaning you
  practise here.
