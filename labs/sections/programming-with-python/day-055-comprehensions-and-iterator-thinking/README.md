# Day 055 lab — Comprehensions & Generators

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Comprehensions and Iterator Thinking
- **Day number:** 55 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-055-comprehensions-and-iterator-thinking
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-055-comprehensions-and-iterator-thinking` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 55's lesson teaches two idioms at once: comprehensions (the everyday
one-line transform) and iterator thinking (processing a stream lazily, one
item at a time). This lab makes both concrete. You build **list, dict, and
set comprehensions** that map and filter a small set of records, then a
**lazy generator pipeline** that streams those records through a reader and a
filter and computes an aggregate — and you prove the lazy pipeline returns
exactly the same answer as a plain `for` loop. It is the shape every AI data
loader, streaming tokenizer, and batch pipeline is built on, shrunk to six
rows you can read.

## Learning objectives

- Write list, dict, and set comprehensions that map and filter in one line.
- Write a `yield`-based generator function and explain why it is lazy.
- Assemble a generator pipeline (reader → filter → aggregate) that holds only
  one record in memory at a time.
- Prove a lazy pipeline is equivalent to an eager loop with an `assert`.
- Use `itertools` (`count`, `islice`) to take a slice of an endless stream.

## Prerequisites

- The Day 55 lesson (read it first — it explains every part this lab builds).
- Days 51-54: loops, and lists, dictionaries, tuples, and sets.
- A text editor and a terminal. No experience beyond this week is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The program is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The program transforms six small records in
memory; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — the `sys` and `itertools` modules ship with Python.
  No packages to install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.
Comprehensions, generators, and `itertools` are core language features.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-055-comprehensions-and-iterator-thinking
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-055-comprehensions-and-iterator-thinking/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── pipeline.py                 ← YOUR working file (5 numbered exercises)
│   └── pipeline-worksheet.md       ← design a second pipeline before coding it
├── examples/
│   └── pipeline.py                 ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← assert-based checks (comprehensions + pipeline)
├── expected-output/
│   ├── sample-run.txt              ← real captured run of the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished program first
python3 examples/pipeline.py

# 2. Your task: complete the five exercises in the starter, then run it
python3 starter/pipeline.py

# 3. Prove laziness: pull ONE record from the reader without consuming the rest
python3 -c "import sys; sys.path.insert(0, 'examples'); from pipeline import read_records, RECORDS; g = read_records(RECORDS); print(next(g))"

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/pipeline.py` — runs the complete reference: it prints the
  results of the list, dict, and set comprehensions, the first three ids from
  an `itertools` counter, and the engineering average computed two ways — a
  lazy generator pipeline and an explicit loop — then asserts the two match
  and prints `match: lazy pipeline == loop baseline`.
- `python3 starter/pipeline.py` — runs your version. The starter ships with
  five exercises stubbed out (each raising `NotImplementedError` until you
  finish it): a list comprehension, a dict comprehension, a set
  comprehension, a `yield`-based generator, and the assembled lazy pipeline.
- `python3 -c "... next(g) ..."` — pulls a single record from the reader
  generator with `next()`, printing just one record dict. This proves the
  generator produces items on demand rather than building them all first.
- `bash tests/run_tests.sh` — imports the reference module and asserts the
  return values of every comprehension and generator, runs the whole program
  and confirms its self-check, and checks your starter (structurally until
  you finish, strictly afterwards). Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run:

```text
$ python3 examples/pipeline.py
high scorers (list):   ['ALICE', 'CAROL', 'FRANK']
name -> score (dict):  {'alice': 88, 'bob': 72, 'carol': 95, 'dave': 60, 'erin': 79, 'frank': 84}
distinct teams (set):  ['design', 'engineering', 'marketing']
first 3 ids (itertools): [1000, 1001, 1002]
engineering average (lazy pipeline): 87.3
engineering average (loop baseline): 87.3
match: lazy pipeline == loop baseline
```

The program is deterministic, so your output will match exactly (the set is
printed sorted so it is stable).
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every line on every platform.

## Validation steps

1. Run `python3 examples/pipeline.py` — it must print the three comprehension
   results and end with `match: lazy pipeline == loop baseline`.
2. Complete the five exercises in `starter/pipeline.py`, then run it and
   confirm it matches the reference.
3. Run the `next(g)` one-liner — it must print exactly one record dict.
4. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `12 checks, 0 failure(s).` The checks are assert-based:
they import the module and assert the return value of each comprehension and
generator, run the whole program, and check your starter. The command exits 0
on success and non-zero on any failure, so it can run in CI. A full captured
run is in [`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read only their own in-memory data
and write nothing outside their console output (no files, no network, no
settings). To reset your work, restore the starter from git:
`git checkout -- starter/pipeline.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the deliberate `NotImplementedError` stubs, indexing a generator,
unordered sets, exhausted generators, and keeping `only_team` lazy.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. A comprehension runs real
code for every item, so keep its output expression a plain transform and
never `eval()` untrusted text — the same rule you learned for input handling.

## Extension exercises

1. Write a generator `batched(iterable, size)` that yields tuples of up to
   `size` items — the exact shape of a model's data loader — and confirm it
   streams without building the full list.
2. Put a `print(f"reading {r['name']}")` inside the reader, wrap it in
   `itertools.islice(reader, 2)`, and confirm only two "reading" lines
   appear — proving records beyond the second were never read.
3. Use `itertools.chain` to splice two record streams into one and run a
   single comprehension over the combined stream, showing the consumer
   neither knows nor cares that the data came from two sources.

## Navigation

- **Previous day:** Day 54 — Tuples, Sets, and Choosing a Collection
  (`labs/sections/programming-with-python/day-054-tuples-sets-and-choosing-a-collection/`).
- **Next day:** Day 56 — Building a Data-Driven CLI
  (`labs/sections/programming-with-python/day-056-building-a-data-driven-cli/`, to be written).
- **Week 8 project:** the Terminal Task Manager, a to-do CLI built on lists
  and dictionaries — the same transform-and-filter habits you practise here.
