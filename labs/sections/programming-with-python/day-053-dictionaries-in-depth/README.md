# Day 053 lab — Word Frequency & Records

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dictionaries in Depth
- **Day number:** 53 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-053-dictionaries-in-depth
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-053-dictionaries-in-depth` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 53's lesson teaches dictionaries in depth. This lab makes the idioms
concrete: you build **Word Frequency & Records**, a small program that
(a) counts word frequencies from text using the `d.get(key, 0) + 1` idiom and
finds the most common word, and (b) stores small records as a list of
dictionaries, then groups them with `setdefault` and filters them with a dict
comprehension. You build it from a starter, one exercise at a time, then run an
automated test suite that checks real behaviour — including safe access, the
insertion-order guarantee, and tie-breaking. The word counter is the exact
machinery underneath text search and the term-frequency features of classical
language models.

## Learning objectives

- Count word frequencies with the `.get()`-with-default idiom, never a
  `KeyError`.
- Find the most common item, breaking ties toward the first-seen key.
- Store structured data as a list of dictionaries and group it with
  `setdefault`.
- Build a filtered view with a dict comprehension.
- Validate input at the boundary and fail with a clear message and a non-zero
  exit code.
- Prove a function is importable and testable — the payoff of the main guard
  from Day 49.

## Prerequisites

- The Day 53 lesson (read it first — it explains every pattern this lab uses).
- Days 43-52: a working Python 3 install plus variables, strings, numbers,
  input/output, reading errors, assembling a small program, and lists.
- A text editor and a terminal. No programming experience beyond this course is
  assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14).
- **Linux** — fully supported (any distribution with Python 3.7+ and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` if that is how Python is exposed. The program is pure
  standard-library Python and behaves identically everywhere Python 3.7+ runs.

## Hardware requirements

Any computer that runs Python 3. The program builds a few small dictionaries in
memory; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.7 or newer; tested on 3.14). Version 3.7+ matters: the lab
  relies on the dictionary insertion-order guarantee introduced then.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — the `sys` module ships with Python. No packages to
  install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-053-dictionaries-in-depth
python3 --version   # confirm Python 3.7+ is available
```

## File structure

```text
day-053-dictionaries-in-depth/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   └── wordstats.py                ← YOUR working file (4 numbered exercises)
├── examples/
│   └── wordstats.py                ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (counting, records, imports)
├── expected-output/
│   ├── sample-run.txt              ← real captured run of the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3.7+ only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished program first: counting, then records
python3 examples/wordstats.py "the cat sat on the mat the cat"
python3 examples/wordstats.py --records
python3 examples/wordstats.py                 # no argument: prints an error, exits non-zero

# 2. Your task: complete the four exercises in the starter, then run it
python3 starter/wordstats.py "one two two three three three"

# 3. Prove the module is importable (the payoff of the main guard)
python3 -c "import sys; sys.path.insert(0, 'examples'); from wordstats import count_words; print(count_words('a b a'))"

# 4. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/wordstats.py "the cat sat on the mat the cat"` — runs the
  complete reference: it counts the words with `count_words` (the
  `get()`-with-default idiom), prints each word with its count in insertion
  order, and prints the most common word (`most_common`, ties going to the
  first seen).
- `python3 examples/wordstats.py --records` — runs the records half: it groups
  the built-in `PEOPLE` records by role with `group_by_role` (using
  `setdefault`) and builds a filtered, sorted view of names with a dict
  comprehension (`names_up_to_m`).
- `python3 examples/wordstats.py` with no argument — prints a clear usage error
  to standard error and exits with code 1.
- `python3 starter/wordstats.py ...` — runs your version. The starter ships
  with four exercises stubbed out (each raising `NotImplementedError` until you
  finish it): count with `.get()`, find the top word, group with `setdefault`,
  and build a dict comprehension.
- `python3 -c "...count_words..."` — imports one function from the module and
  calls it, without running the whole program. This works only because the main
  guard holds `main` back on import.
- `bash tests/run_tests.sh` — runs the reference on counting and records inputs
  (checking output *and* exit code), imports two functions to check their
  return values, and checks your starter (structurally until you finish,
  strictly afterwards). Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run:

```text
$ python3 examples/wordstats.py "a a b"
a: 2
b: 1
most common: a (2)

$ python3 examples/wordstats.py --records
engineers: ['Ada', 'Alan']
admirals: ['Grace']
names A-M: ['Ada', 'Alan', 'Grace']
```

The counts print in **insertion order** (the order each word first appeared),
not alphabetically — the Python 3.7+ guarantee. The program is deterministic,
so your output will match exactly.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
behaviour for every input on every platform.

## Validation steps

1. Run `python3 examples/wordstats.py "a a b"` — it must print `a: 2`, `b: 1`,
   and `most common: a (2)`.
2. Run `python3 examples/wordstats.py --records` — it must print the two role
   groups and the `names A-M` line.
3. Run `python3 examples/wordstats.py; echo $?` — it must print a usage error
   and then `1`.
4. Complete the four exercises in `starter/wordstats.py`, then run it on the
   same inputs and confirm it matches the reference.
5. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `12 checks, 0
failure(s).` Once you complete all four starter exercises, six more checks run
your version through the same counting and records inputs plus the main-guard
check, giving `18 checks, 0 failure(s).` The command exits 0 on success and
non-zero on any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the program and tests read only their command-line
arguments and write nothing outside their own console output (no files, no
network, no settings). To reset your work, restore the starter from git:
`git checkout -- starter/wordstats.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the deliberate `NotImplementedError` stubs, `KeyError` while
counting, `unhashable type` on a bad key, insertion order versus sorting,
tie-breaking, and importing vs running.

## Security notes

See [security.md](security.md). Short version: the program makes no network
calls, writes no files, and needs no privileges. It validates input at the
boundary, never `eval()`s it, and relies on Python's default hash randomisation
(leave it on) to resist hash-flooding attacks.

## Extension exercises

1. Rewrite the counting and grouping with `collections.Counter` and
   `collections.defaultdict` and confirm the output is identical; note in a
   comment what each helper removed (`Counter(...).most_common(1)` should
   replace your top-word logic).
2. Add a timing experiment that counts a large repeated string with a
   dictionary versus scanning a list of `[word, count]` pairs, and record the
   two timings — you should see the list version grow far slower as the
   vocabulary grows (the O(1)-versus-O(n) difference made visible).
3. Build a toy **vocabulary**: a dict comprehension mapping each distinct word
   to a unique integer id, then use it to turn a sentence into a list of ids —
   the token-to-id step that turns text into the numbers a language model
   consumes.

## Navigation

- **Previous day:** Day 52 — Lists in Depth
  (`labs/sections/programming-with-python/day-052-lists-in-depth/`).
- **Next day:** Day 54 — continues Week 8, Data Structures
  (`labs/sections/programming-with-python/day-054-.../`, to be written).
- **Week 8 project:** builds on the collection idioms of this week — counting,
  grouping, and querying structured data with dictionaries.
