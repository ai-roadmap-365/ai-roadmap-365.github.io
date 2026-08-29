# Day 075 lab — Catch the Bug the Tests Missed

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Static Typing with mypy
- **Day number:** 75 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-075-static-typing-with-mypy
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-075-static-typing-with-mypy` when the site is running.
<!-- generated-links:end -->

## Purpose

You spent four days learning to write tests that pass. This lab is about what
a passing test suite does not tell you.

`starter/catalog.py` is a small, fully annotated module: a catalogue of model
records, a lookup, a cost estimate, a formatter, a settings loader. It ships
with `starter/test_catalog.py`, eight tests, all green. It also contains two
real bugs. The tests do not find them, because a test only exercises the paths
it walks, and neither bug is on one of those paths.

Then you run mypy over the same file and get three errors in under a second,
each naming a file, a line, and an error code. One of them, `[union-attr]`,
is the bug that would crash in production the first time somebody asked for a
model that is not in the catalogue.

Over seven exercises you run both tools, learn to read an error by its code
rather than its prose, fix the code, turn strictness up and handle what that
adds, and finish by proving mechanically that adding `Any` to one signature
makes a caught error disappear while the code stays exactly as broken.

Day 69 introduced type annotations and had to be honest that no checker was
installed, so it proved Python ignores annotations at runtime by inspecting
`__annotations__` instead. This lab is the other half of that story: the tool
that reads them.

## Learning objectives

- Run a pytest suite and a type checker over the same module and describe, in
  your own words, which bug class each one catches.
- Read a mypy error properly: file, line, message, and the bracketed error
  code — and explain why the code is the part that matters.
- Recognise the `Optional` bug (`X | None` used without a guard) and fix it
  with narrowing rather than with an ignore comment.
- Explain why mypy is silent on a fully unannotated file, and what `--strict`
  changes about that.
- Configure mypy with a real `[tool.mypy]` table in `pyproject.toml`,
  including per-module overrides.
- Demonstrate that `Any` disables checking, and that a `# type: ignore`
  carrying the wrong error code suppresses nothing.
- State the honest limits: what mypy cannot check, and why the tests from
  Days 071–074 are not replaced by any of this.

## Prerequisites

- The Day 75 lesson (read it first — it walks these exact error codes).
- Day 69: type annotations, `X | None`, builtin generics, and the fact that
  Python stores annotations without enforcing them.
- Days 071–074: pytest, writing and running a test suite.
- Day 43: `python3 -m venv` and installing packages with `pip`.
- Day 66: raising exceptions deliberately; Day 65: `json.load`.
- A text editor, a terminal, and one-time network access to install two
  packages.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, mypy 2.3.0, pytest 9.1.1).
- **Linux** — fully supported (any distribution with Python 3.10+, bash, and
  `pip`).
- **Windows** — use WSL and follow the Linux path. Native Windows works too:
  substitute `python` for `python3` and `.venv\Scripts\` for `.venv/bin/`.
  Nothing in this lab depends on path separators or line endings, and mypy's
  error text is identical on all three.

## Hardware requirements

Any computer that runs Python 3. The source files total a few kilobytes; mypy
analysing them takes well under a second and a few tens of megabytes. No GPU,
no special memory, no large downloads beyond the two packages themselves.

## Required software

- `python3` — **3.10 or newer**. The lab uses `X | None` union syntax in
  annotations. Tested on 3.14.0.
- `mypy` **2.3.0** and `pytest` **9.1.1**, installed from
  [`requirements/requirements.txt`](requirements/requirements.txt).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only in the lab code itself: `json`, `dataclasses`,
  `typing`, `pathlib`.

## Free and open-source options

Everything here is free and open source. Python, bash and the standard
library cost nothing. mypy and pytest are both MIT-licensed, developed in the
open, and free for personal and commercial use with no account and no key.

If you would rather not install anything at all, two free alternatives check
the same annotations: **Pyright**, Microsoft's checker, which is free and open
source and can be installed separately from any editor; and the Pylance
extension for Visual Studio Code, which is free to use and runs Pyright for
you as you type. The lesson's Alternatives section compares them. This lab
pins mypy because it is the reference implementation and because its error
codes are the ones the exercises teach you to read.

## Installation

```bash
cd labs/sections/programming-with-python/day-075-static-typing-with-mypy
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/mypy --version
.venv/bin/pytest --version
```

Expect `mypy 2.3.0 (compiled: yes)` and `pytest 9.1.1`. The install needs the
network once; nothing after it does.

If you already have both tools available on your `PATH`, you can skip the
virtual environment — the test runner finds them either way.

## File structure

```text
day-075-static-typing-with-mypy/
├── README.md                    ← you are here
├── metadata.yml                 ← machine-readable lab metadata
├── starter/
│   ├── catalog.py               ← YOUR working file: annotated, tested, and wrong
│   ├── test_catalog.py          ← the green suite that misses both bugs
│   ├── untyped_first_run.py     ← exercise 0: what mypy says about unannotated code
│   ├── any_demo.py              ← exercise 7: Any switching the checker off
│   └── settings.json            ← sample data for the settings loader
├── examples/
│   ├── catalog.py               ← the fixed module: clean under --strict
│   ├── test_catalog.py          ← the same suite, plus the test the bug suggested
│   ├── typing_tour.py           ← every construct in the lesson, strict-clean
│   ├── demo.py                  ← deterministic tour of the fixed module
│   ├── pyproject.toml           ← a real [tool.mypy] table with per-module overrides
│   └── settings.json            ← sample data
├── tests/
│   └── run_tests.sh             ← 33 behaviour checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt           ← real captured output of every command below
│   └── test-run.txt             ← real captured run of the test suite
├── requirements/
│   ├── requirements.txt         ← mypy==2.3.0, pytest==9.1.1
│   └── README.md                ← what each dependency is for, and the licences
├── troubleshooting.md
└── security.md
```

This lab writes no data files. mypy may leave a `.mypy_cache/` directory if you
run it by hand; see [Cleanup](#cleanup).

## How to run

From the lab directory. Replace `.venv/bin/` with nothing if the tools are
already on your `PATH`.

```bash
# 0. What does a checker say about code with no annotations at all?
#    The first answer is "success". Read untyped_first_run.py to see why
#    that is the most misleading result mypy can give you.
.venv/bin/mypy starter/untyped_first_run.py
.venv/bin/mypy --strict starter/untyped_first_run.py

# 1. Run the tests on the buggy module. Eight tests, all green.
PYTHONPATH=starter .venv/bin/pytest -q starter/test_catalog.py

# 2. Run mypy on the same file. Three errors, none of which the tests found.
.venv/bin/mypy starter/catalog.py

# 3. Read the errors: file, line, message, code. Write down the three codes.

# 4-5. Fix bug A and bug B in starter/catalog.py, then re-run step 2
#      until it prints "Success".

# 6. Turn strictness up and handle what it adds.
.venv/bin/mypy --strict starter/catalog.py

# 7. Prove the Any point for yourself.
.venv/bin/mypy starter/any_demo.py
#    Now edit the return annotation of lookup() to `-> Any:` and run again.

# See the finished reference at any point.
PYTHONPATH=examples python3 examples/demo.py
PYTHONPATH=examples python3 examples/typing_tour.py
.venv/bin/mypy --strict examples/catalog.py examples/typing_tour.py
.venv/bin/mypy --config-file examples/pyproject.toml examples/catalog.py

# Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `mypy starter/untyped_first_run.py` — reports `Success: no issues found in
  1 source file` on a module with no annotations whatsoever. That is gradual
  typing working as designed: an unannotated function is one mypy declines to
  check. The same command with `--strict` reports six errors on the same
  unchanged file. Meeting that contrast first is what stops you reading a
  clean run as a clean bill of health.
- `pytest starter/test_catalog.py` — eight tests, all passing, over a module
  with two real bugs. Read each test and ask which line it never reaches.
- `mypy starter/catalog.py` — three errors in the same file the tests just
  blessed: two `[union-attr]` on line 63, where `describe()` reads attributes
  off a value that may be `None`, and one `[arg-type]` on line 85, where a
  float produced by `/` is handed to a parameter annotated `int`.
- `mypy --strict starter/catalog.py` — the same three plus
  `[no-untyped-def]` for the unannotated `format_price`, `[no-untyped-call]`
  for the typed function that calls it, and `[no-any-return]` for the loader
  that hands `json.load`'s `Any` straight out under a `dict[str, float]`
  promise.
- `mypy starter/any_demo.py` — one `[union-attr]`. Change the one annotation
  the file's docstring names, and the error vanishes without a single line of
  logic changing. That is the cautionary demonstration of the day.
- `python3 examples/demo.py` — a deterministic tour of the fixed module,
  showing the `None` path handled, floor division keeping a token count an
  integer, and a settings loader that checks values at the boundary rather
  than merely annotating them.
- `python3 examples/typing_tour.py` — runs one worked example of every
  construct the lesson covers: `Optional` narrowing, `isinstance` narrowing,
  unions, `Literal`, `TypedDict`, `Final`, `NewType`, a `TypeVar` generic, a
  `Protocol` satisfied without inheritance, and `cast`. Every line of that
  file also passes `mypy --strict`, which is the real proof it is correct.
- `mypy --config-file examples/pyproject.toml examples/catalog.py` — runs the
  checker from a real configuration file instead of command-line flags, which
  is how a project actually does it.
- `bash tests/run_tests.sh` — 33 checks. It asserts pytest passes on the
  buggy code, that mypy exits non-zero on it and emits the specific bracketed
  codes, that strict mode adds exactly the codes default settings let through,
  that `examples/` is clean under both `--strict` and the config file, that
  the buggy `describe()` genuinely raises at runtime, that the `Any` edit
  makes the error vanish while the crash remains, and that a `type: ignore`
  with the wrong code suppresses nothing. Every code assertion greps for the
  bracketed code rather than the message text, so a future release rewording a
  message will not break the suite.

## Expected output

Captured from a real run on the authoring machine; the full session is in
[`expected-output/sample-run.txt`](expected-output/sample-run.txt).

The contrast the whole lab is built around — the same file, two tools:

```text
$ python3 -m pytest starter/test_catalog.py
........                                                                 [100%]
8 passed in 0.00s
(exit 0)

$ python3 -m mypy starter/catalog.py
starter/catalog.py:63: error: Item "None" of "Model | None" has no attribute "name"  [union-attr]
starter/catalog.py:63: error: Item "None" of "Model | None" has no attribute "context_tokens"  [union-attr]
starter/catalog.py:85: error: Argument 2 to "estimate_cost" has incompatible type "float"; expected "int"  [arg-type]
Found 3 errors in 1 file (checked 1 source file)
(exit 1)
```

What strict mode adds to the same unchanged file:

```text
$ python3 -m mypy --strict starter/catalog.py
starter/catalog.py:63: error: Item "None" of "Model | None" has no attribute "name"  [union-attr]
starter/catalog.py:63: error: Item "None" of "Model | None" has no attribute "context_tokens"  [union-attr]
starter/catalog.py:85: error: Argument 2 to "estimate_cost" has incompatible type "float"; expected "int"  [arg-type]
starter/catalog.py:88: error: Function is missing a type annotation  [no-untyped-def]
starter/catalog.py:103: error: Call to untyped function "format_price" in typed context  [no-untyped-call]
starter/catalog.py:117: error: Returning Any from function declared to return "dict[str, float]"  [no-any-return]
Found 6 errors in 1 file (checked 1 source file)
(exit 1)
```

And the result that surprises people most — an entirely unannotated module,
default settings:

```text
$ python3 -m mypy starter/untyped_first_run.py
Success: no issues found in 1 source file
(exit 0)

$ python3 -m mypy --strict starter/untyped_first_run.py
starter/untyped_first_run.py:25: error: Function is missing a type annotation  [no-untyped-def]
starter/untyped_first_run.py:33: error: Function is missing a type annotation  [no-untyped-def]
starter/untyped_first_run.py:37: error: Function is missing a return type annotation  [no-untyped-def]
starter/untyped_first_run.py:37: note: Use "-> None" if function does not return a value
starter/untyped_first_run.py:38: error: Call to untyped function "load_prices" in typed context  [no-untyped-call]
starter/untyped_first_run.py:39: error: Call to untyped function "total" in typed context  [no-untyped-call]
starter/untyped_first_run.py:43: error: Call to untyped function "main" in typed context  [no-untyped-call]
Found 6 errors in 1 file (checked 1 source file)
(exit 1)
```

The fixed reference, and the tests still green:

```text
$ python3 -m mypy --strict examples/catalog.py examples/typing_tour.py
Success: no issues found in 2 source files
(exit 0)

$ python3 -m pytest examples/test_catalog.py
.........                                                                [100%]
9 passed in 0.00s
(exit 0)
```

Everything except pytest's timing line is deterministic, so your output will
match character for character. The timing (`in 0.00s`) depends on your
machine.

## Validation steps

1. `.venv/bin/mypy --version` prints `mypy 2.3.0 (compiled: yes)` and
   `.venv/bin/pytest --version` prints `pytest 9.1.1`.
2. `PYTHONPATH=starter .venv/bin/pytest -q starter/test_catalog.py` reports
   `8 passed` and exits 0 — before you change anything.
3. `.venv/bin/mypy starter/catalog.py` reports exactly three errors and exits
   1. Two carry the code `[union-attr]` and one `[arg-type]`.
4. You can state, for each error, the file, the line, and the code, without
   reading the message text.
5. After fixing bug A, the `[union-attr]` errors are gone and the tests still
   report `8 passed` — the fix changed nothing on any tested path.
6. After fixing bug B, `.venv/bin/mypy starter/catalog.py` prints `Success`.
7. `.venv/bin/mypy --strict starter/catalog.py` still reports
   `[no-untyped-def]`, `[no-untyped-call]` and `[no-any-return]`; after you
   annotate `format_price` and check the loaded object in `load_settings`,
   strict mode prints `Success` too.
8. `.venv/bin/mypy starter/any_demo.py` reports `[union-attr]`; after
   changing `lookup`'s return annotation to `Any` it prints `Success`, and
   `python3 -c "import any_demo; any_demo.shout('zzz')"` still raises
   `AttributeError`. Nothing got safer.
9. `PYTHONPATH=examples python3 examples/demo.py` exits 0 and section 2 shows
   `describe('enormous'): enormous: unknown model`.
10. `bash tests/run_tests.sh` ends with `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `33 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in continuous integration. A full
captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

The suite finds both tools the same way the rest of Week 11 does: an explicit
override first, then this lab's `.venv/`, then your `PATH`. If neither is
available it fails loudly with install instructions rather than skipping
quietly. To point it at specific binaries:

```bash
MYPY=/path/to/mypy PYTEST=/path/to/pytest bash tests/run_tests.sh
```

These are behaviour checks, not file-existence checks. Delete the `None` guard
from `examples/catalog.py` and six of the 33 fail.

## Cleanup

The lab writes no data files. Three kinds of cache may appear:

```bash
rm -rf .mypy_cache examples/.mypy_cache starter/.mypy_cache
rm -rf .pytest_cache examples/__pycache__ starter/__pycache__
```

`.mypy_cache/` is mypy's incremental cache — it appears in whatever directory
you ran mypy from, it is excluded from version control, and deleting it only
costs you a slightly slower next run. The test suite never creates one: it
points mypy at a temporary cache directory and removes it on exit.

To remove the virtual environment: `rm -rf .venv`.
To reset your work: `git checkout -- starter/`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `mypy: command
not found`, `Cannot find implementation or library stub for module`,
`ModuleNotFoundError: No module named 'catalog'` when running pytest, mypy
reporting nothing at all on an unannotated file, `X | None` failing on older
Python versions, a `type: ignore` that does not suppress what you expected,
`unused-ignore` errors appearing after you fix code, stale results from the
incremental cache, and what to do when mypy and your editor disagree.

## Security notes

See [security.md](security.md). Short version: a type checker reads your
source, it does not run it, so checking a file is a safe operation — but the
result is a claim about your code, never about the data that will arrive.
`name: str` does not mean the string is a safe filename, a valid email, or
free of injection; `--ignore-missing-imports` and `Any` are the two settings
that silently turn checking off, and both deserve a comment saying why. mypy
runs entirely on your machine and sends nothing anywhere.

## Extension exercises

1. **Type the untyped module.** Annotate every function in
   `starter/untyped_first_run.py` until `mypy --strict` reports `Success`.
   `load_prices` is the interesting one: what type is `rows`, and what does
   the function really return?
2. **Write the `Protocol` version of a dependency.** Day 74 injected a clock
   and a repository to make code testable. Take the `Clock` protocol from
   `examples/typing_tour.py`, add a `Repository` protocol with `get` and
   `save` methods, write a real and a fake implementation of each, and check
   that both satisfy the protocol with no inheritance anywhere.
3. **Make an ignore rot.** Add `# type: ignore[arg-type]` to a line in
   `examples/catalog.py` where nothing is wrong, then run
   `mypy --strict`. You get `[unused-ignore]`. Now delete the
   `warn_unused_ignores` line from `examples/pyproject.toml` and run again
   with `--config-file`. Silence. That is how a codebase accumulates hundreds
   of ignores nobody can safely remove.
4. **Find a limit.** Write a function annotated `def send(to: str) -> None`
   that is meant to take an email address, and call it with `send("not an
   email")`. mypy is perfectly happy. Then write the check that would catch it
   — a validation, at runtime, of the kind Day 70 pointed at pydantic for —
   and write one sentence on why no type system was ever going to do that job.
5. **Adopt mypy on your own code.** Take any Python file you have written
   since Day 43, run `mypy` on it, then `mypy --strict`, and fix what you
   find. Record how many errors each mode reported and how many were real
   bugs rather than missing annotations.

## Navigation

- **Previous day:** Day 74 — Mocking and Testing Boundaries
  (`labs/sections/programming-with-python/day-074-mocking-and-testing-boundaries/`).
- **Next day:** Day 76 — Linting and Formatting with Ruff
  (`labs/sections/programming-with-python/day-076-linting-and-formatting-with-ruff/`).
- **Week 11 project:** the Tested Utility Library. The `[tool.mypy]` table you
  read here is one of the gates that project assembles.
