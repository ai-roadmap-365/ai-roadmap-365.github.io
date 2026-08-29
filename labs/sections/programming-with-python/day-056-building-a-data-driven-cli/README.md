# Day 056 lab — Records CLI

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building a Data-Driven CLI
- **Day number:** 56 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-056-building-a-data-driven-cli
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-056-building-a-data-driven-cli` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 56's lesson is the Week 8 capstone: it brings control flow and every
collection together into one real command-line tool. This lab makes that
concrete. You build **Records CLI** — a small, data-driven tool with
`argparse` subcommands (`add`, `list`, `find`, `delete`) that persists a
list of dictionaries to a JSON file, validates input, prints results, and
returns proper exit codes. You build it from a starter, one exercise at a
time, then run an automated test suite that checks real behaviour: output
*and* exit codes, persistence to disk, and error handling. This is a
scaled-down rehearsal for the Week 8 project, the **Terminal Task Manager**
(a to-do CLI with add/list/complete/delete over a JSON file) — the same
skeleton you will reach for later to wrap models, datasets, and agents as
command-line tools.

## Learning objectives

- Parse command-line arguments with `argparse`: a global option, subcommands,
  required options, typed options, and choices.
- Read and write structured data as JSON with `json.load` and `json.dump` so
  it survives between runs.
- Model records as a list of dictionaries and run the command → load →
  mutate → save → report loop.
- Return meaningful exit codes and send error messages to standard error.
- Keep the tool testable by taking all input from arguments (never an
  interactive prompt), and prove a function is importable and testable.

## Prerequisites

- The Day 56 lesson (read it first — it explains every part this lab builds).
- Days 50–55: conditionals and loops, lists, dictionaries, sets and tuples,
  and comprehensions.
- Day 49: the shape of a real program — named functions, a `main()`, the
  `if __name__ == "__main__":` guard, and input validation.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The tool is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The tool reads and writes a tiny JSON file
and does no heavy computation; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `argparse`, `json`, and `sys` all ship with
  Python. No packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed. The
`argparse` and `json` modules are part of Python itself.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-056-building-a-data-driven-cli
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-056-building-a-data-driven-cli/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── records.py                  ← YOUR working file (5 numbered exercises)
│   └── cli-worksheet.md            ← design the CLI before coding it
├── examples/
│   └── records.py                  ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (output, exit codes, persistence)
├── expected-output/
│   ├── sample-run.txt              ← real captured session with the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory. The global `--store` option always comes **before** the
subcommand:

```bash
# 1. See the finished tool first. Start empty, then add and inspect.
python3 examples/records.py --store demo.json list
python3 examples/records.py --store demo.json add --name "Ada Lovelace" --email ada@example.com
python3 examples/records.py --store demo.json add --name "Alan Turing" --email alan@example.com
python3 examples/records.py --store demo.json list

# 2. Search and delete; watch the exit codes.
python3 examples/records.py --store demo.json find --field name --query ada
python3 examples/records.py --store demo.json find --field name --query zoe   ; echo "exit: $?"
python3 examples/records.py --store demo.json delete --id 1

# 3. See the persisted JSON, then clean it up.
cat demo.json
rm -f demo.json

# 4. Your task: complete the five exercises in the starter, then run it.
python3 starter/records.py --store mine.json add --name "Grace Hopper" --email grace@example.com

# 5. Prove a function is importable (the payoff of the main guard).
python3 -c "import sys; sys.path.insert(0, 'examples'); from records import next_id; print(next_id([]))"

# 6. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `add --name X --email Y` — loads the store, validates the input, appends a
  new record with the next id, saves the whole list back to JSON, and prints
  a confirmation. This is the command → load → mutate → save → report loop.
- `list` — loads the store and prints every record, or `no records` when the
  store is empty or absent.
- `find --field name --query ada` — loads the store and prints records whose
  chosen field contains the query (case-insensitive substring). Exit code 0
  if at least one matches, 1 if none do — so a script can branch on the
  result.
- `delete --id 1` — loads the store, removes the record with that id, and
  saves. If no record has that id, it prints an error to standard error and
  exits 1.
- `python3 -c "...next_id..."` — imports one function from the module and
  calls it without running the whole tool, which works only because the main
  guard holds `main` back on import.
- `bash tests/run_tests.sh` — drives the reference tool through good and bad
  inputs against a throwaway store, checks output and exit codes, verifies
  persistence, exercises corrupt-store handling, imports two functions to
  check their return values, and checks your starter. Exits 0 only if every
  check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session:

```text
$ python3 examples/records.py --store demo.json add --name "Ada Lovelace" --email ada@example.com
added #1: Ada Lovelace <ada@example.com>

$ python3 examples/records.py --store demo.json find --field name --query zoe   ; echo "exit: $?"
no records match name='zoe'
exit: 1
```

Successful results print to standard output; errors print to standard error
and set a non-zero exit code. The tool is deterministic, so your output will
match. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the
required behaviour for every input on every platform.

## Validation steps

1. `python3 examples/records.py --store demo.json add --name "Ada Lovelace" --email ada@example.com`
   prints `added #1: Ada Lovelace <ada@example.com>`.
2. `python3 examples/records.py --store demo.json list` shows the record; run
   `cat demo.json` and confirm the JSON persisted to disk.
3. `python3 examples/records.py --store demo.json find --field name --query zoe; echo $?`
   prints a "no records match" line and then `1`.
4. `python3 examples/records.py --store demo.json add --name X --email noatsign; echo $?`
   is rejected with a clear error and exits `1`.
5. Complete the five exercises in `starter/records.py`, run it on the same
   inputs, and confirm it matches the reference.
6. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `19 checks, 0
failure(s).` Once you complete all five starter exercises, the suite runs
your version through the same good/bad inputs plus the main-guard check,
giving `31 checks, 0 failure(s).` The command exits 0 on success and
non-zero on any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The tool writes only the JSON store you name with `--store`. Remove any you
created:

```bash
rm -f demo.json mine.json records.json
```

To reset your work, restore the starter from git:
`git checkout -- starter/records.py`. The test runner cleans up its own
temporary store automatically.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, why `--store` goes before the subcommand, argparse's exit code 2
versus the tool's exit code 1, why `find` can exit 1 on purpose, corrupt
stores, importing vs running, and permissions.

## Security notes

See [security.md](security.md). Short version: the tool makes no network
calls and needs no privileges; it reads and writes only the store you name.
Its central habit is to **validate input and parse with `json`, never
`eval()` it** — JSON parsing turns text into data and cannot execute code.

## Extension exercises

1. Add an `update` subcommand that changes the email of a record by id,
   reusing `load_records`/`save_records` and the same validation.
2. Make `delete` idempotent: add a `--force` flag under which deleting a
   missing id prints a notice and exits 0 instead of 1, and explain in a
   comment when each behaviour is the right default.
3. Add a global `--format` option (`plain` or `json`) so `list` and `find`
   can print machine-readable JSON to standard output, ready to pipe into
   another tool.
4. Write your own `tests/test_records.py` that imports `next_id`,
   `validate_new`, and `load_records` and asserts their behaviour, printing
   `all tests passed` only if every assertion holds.

## Navigation

- **Previous day:** Day 55 — Comprehensions and Iterator Thinking
  (`labs/sections/programming-with-python/day-055-comprehensions-and-iterator-thinking/`).
- **Next day:** Day 57 — begins Week 9, Functions and Program Design
  (`labs/sections/programming-with-python/day-057-.../`, to be written).
- **Week 8 project:** the Terminal Task Manager, a to-do CLI with
  add/list/complete/delete persisting to JSON — the same argparse + JSON +
  dispatch skeleton you build here, one job larger.
