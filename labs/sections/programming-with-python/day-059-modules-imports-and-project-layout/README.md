# Day 059 lab — Split into Modules

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Modules, Imports, and Project Layout
- **Day number:** 59 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-059-modules-imports-and-project-layout
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-059-modules-imports-and-project-layout` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 59's lesson teaches how to grow a program beyond one file: modules,
imports, packages and `__init__.py`, the `if __name__ == "__main__":` guard,
how Python finds modules, and a sane small-project layout. This lab makes that
concrete. You start from a **single-file** word-frequency tool
(`starter/single_file.py`) where tokenizing, counting, reporting, and
command-line handling are all tangled together — a working script that nothing
can import or test. You refactor it into a **package**, `wordstats/`, with one
responsibility per module: `tokens.py` (text to a list of words), `stats.py`
(words to frequency numbers), an `__init__.py` that defines the public API, and
a `__main__.py` entry point with the main guard so the package runs as
`python3 -m wordstats`. Then you run a test suite that **imports** your modules
and asserts their behaviour — the payoff of the split. This is the same layout,
one size down, that AI projects use to separate data, model, training, and
serving code so it can be reused, tested, and shipped.

## Learning objectives

- Turn a single-file script into a package: modules organized by
  responsibility, an `__init__.py`, and a `__main__.py` entry point.
- Use `import`, `from ... import`, and `import ... as`, and choose between
  absolute imports (from tests) and relative imports (inside the package).
- Add the `if __name__ == "__main__":` guard so a file can be both run and
  imported, and see why that is what makes the modules testable.
- Explain how Python finds a module (`sys.path`) and that it imports each
  module only once (the `sys.modules` cache).
- Keep module dependencies pointing one way to avoid circular imports.

## Prerequisites

- The Day 59 lesson (read it first — it explains every part this lab builds).
- Days 57–58: functions with arguments and return values, and scope.
- Day 56: a data-driven program with a `main()` and the main-guard idiom.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` if that is how Python is exposed. The package is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The tool reads a small text file and does no
heavy computation; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `re`, `collections`, and `sys` all ship with Python.
  No packages to install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed. The `re`
and `collections` modules are part of Python itself.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-059-modules-imports-and-project-layout
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-059-modules-imports-and-project-layout/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── single_file.py              ← the "before": one tangled script (provided)
│   ├── sample.txt                  ← input text used by the tool
│   ├── module-layout-worksheet.md  ← plan the split before you code it
│   └── wordstats/                  ← YOUR package to complete (6 exercises)
│       ├── __init__.py             ← Exercise 5: the public API
│       ├── tokens.py               ← Exercise 1: tokenize
│       ├── stats.py                ← Exercises 2-3: count_words, top_n
│       └── __main__.py             ← Exercises 4, 6: report + the main guard
├── examples/
│   ├── sample.txt
│   └── wordstats/                  ← complete reference package
│       ├── __init__.py
│       ├── tokens.py
│       ├── stats.py
│       └── __main__.py
├── tests/
│   └── run_tests.sh                ← imports the modules and asserts behaviour
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

The `-m` form must be run from the directory that *contains* the `wordstats/`
package, so `cd` into `examples/` (or `starter/`) first.

```bash
# 1. See the single-file "before" — a working but untestable script.
cd starter
python3 single_file.py sample.txt
cd ..

# 2. Run the finished reference package as a program (file argument).
cd examples
python3 -m wordstats sample.txt

# 3. Feed it standard input instead of a file.
printf 'red red blue green red blue\n' | python3 -m wordstats
cd ..

# 4. Import the package as a library — the payoff of the split.
python3 -c "import sys; sys.path.insert(0, 'examples'); from wordstats import tokenize, top_n; print(top_n(tokenize('a a b'), 2))"

# 5. Your task: complete the six exercises in starter/wordstats, then run it.
cd starter
python3 -m wordstats sample.txt
cd ..

# 6. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `python3 single_file.py sample.txt` — runs the monolith. It prints the same
  report as the package, but every line of real work is trapped inside its
  `if __name__ == "__main__":` block, so nothing in it can be imported or
  tested. This is the "before".
- `python3 -m wordstats sample.txt` — runs the package. Python finds
  `wordstats/` on the path (the current directory is first for `-m`), executes
  `wordstats/__main__.py`, which imports `tokens` and `stats` with relative
  imports, reads the file, and prints the report.
- `printf ... | python3 -m wordstats` — the same, reading standard input
  because no file argument is given.
- `python3 -c "... from wordstats import tokenize, top_n ..."` — imports the
  package's public API (defined by `__init__.py`) and calls the functions
  directly, with no file and no terminal. Only a package split into importable
  modules can be used this way.
- `bash tests/run_tests.sh` — imports the reference modules and asserts what
  each function returns, runs the package as `python3 -m wordstats`, proves each
  responsibility module loads on its own (no circular imports), checks that a
  module is imported only once (the `sys.modules` cache), and then checks your
  starter. Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured session. Running the reference from `examples/`:

```text
$ python3 -m wordstats sample.txt
19 words, 10 unique
1. the: 6
2. cat: 2
3. dog: 2
4. on: 2
5. sat: 2
```

`top_n` breaks ties alphabetically, so the tool is deterministic and your
output will match. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists the required behaviour for the program and for the imported API on every
platform.

## Validation steps

1. `cd examples && python3 -m wordstats sample.txt` prints `19 words, 10
   unique` followed by the five ranked lines above.
2. `python3 -c "import sys; sys.path.insert(0, 'examples'); from wordstats
   import tokenize; print(tokenize('Hello, HELLO world!'))"` prints
   `['hello', 'hello', 'world']`.
3. Complete the six exercises in `starter/wordstats`, then run `cd starter &&
   python3 -m wordstats sample.txt` and confirm it matches the reference.
4. From `starter`, `python3 -c "from wordstats import top_n"` succeeds (proves
   Exercise 5, the public API, is done).
5. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `18 checks, 0
failure(s).` Once you complete all six starter exercises, the suite runs your
package through the same strict import-and-run checks, giving `26 checks, 0
failure(s).` The command exits 0 on success and non-zero on any failure, so it
can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The tool writes no data files. Importing modules can create `__pycache__`
folders; remove them if you like:

```bash
find . -name __pycache__ -exec rm -rf {} +
```

To reset your work, restore the starter from git: `git checkout -- starter/`.
The test runner sets `PYTHONDONTWRITEBYTECODE=1` so it leaves nothing behind.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the `No module named wordstats` path error, why running a file
inside the package directly breaks relative imports, why `from wordstats
import ...` needs Exercise 5, circular imports, and `__pycache__` folders.

## Security notes

See [security.md](security.md). Short version: the package makes no network
calls and needs no privileges; it only reads the input you name. Its central
habits are that **importing a module runs its top-level code** (so read before
you import), that `sys.path` order is a trust decision (do not let a local file
shadow a standard-library module — this is why the module is `tokens.py`, not
`tokenize.py`), and that text is parsed as data with `re`, never executed.

## Extension exercises

1. Add a third responsibility module, `wordstats/report.py`, and move `report`
   into it; import it from `__main__.py` and re-export it from `__init__.py`.
   Notice how a new responsibility becomes one new file plus two import lines.
2. Add a `--top N` option (using `argparse`, from Day 56) so the number of
   ranked words is configurable, defaulting to 5.
3. Add a `tests/test_wordstats.py` that imports `tokenize`, `count_words`, and
   `top_n` and asserts their behaviour, printing `all tests passed` only if
   every assertion holds — a pure-Python test with no bash.
4. Deliberately create a circular import (make `tokens.py` do `from .stats
   import count_words` and `stats.py` do `from .tokens import tokenize`), run
   `python3 -m wordstats`, read the error, then fix it by removing one of the
   two imports. Write two sentences on what you saw and why.

## Navigation

- **Previous day:** Day 58 — Scope, Closures, and *args/**kwargs
  (`labs/sections/programming-with-python/day-058-scope-closures-and-args-kwargs/`).
- **Next day:** Day 60 — A Tour of the Standard Library
  (`labs/sections/programming-with-python/day-060-a-tour-of-the-standard-library/`).
- **Week 9 project:** the Flashcard Study App — a spaced-repetition flashcard
  tool organized into clean modules, the same package layout you build here
  scaled up to data, scheduling, and a command-line front end.
