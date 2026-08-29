# Day 071 lab — Your First Real Test Suite

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Why Test, and pytest Basics
- **Day number:** 71 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-071-why-test-and-pytest-basics
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-071-why-test-and-pytest-basics` when the site is running.
<!-- generated-links:end -->

## Purpose

You are handed a small module called `textstats`: five functions that split
text into words, count them, average their length, rank the most frequent, and
estimate reading time. It was written quickly, checked by eye on one paragraph
of English prose, and shipped. **Two of its five functions are wrong**, and
neither is wrong in a way you notice by reading the code once.

Your job is not to read the code until you spot the bugs. Your job is to write
tests against the docstrings — which are the specification — and let the tests
find them. That distinction is the whole lab. A test whose expected value came
out of the code it is testing agrees with the bug and proves nothing.

Around that central task the lab makes four things visible that you cannot
learn from prose:

- **What a test actually is.** `examples/plain_asserts.py` is a working test
  suite with no test runner at all — bare `assert` statements and a process
  exit code. Run it, break the module, watch it exit 1. pytest is an amplifier
  for that idea, not a replacement for it.
- **What a failure report contains.** `examples/failure-demo/` holds five tests
  that fail on purpose — a number, a list, a dict, a string, and a missing
  exception — so you can read five kinds of explanation side by side, and then
  see the same failures under `unittest`, which does no assertion rewriting.
- **That a green suite is a claim, not a fact.** `examples/vacuous-demo/` holds
  four tests that pass no matter what the code does, plus one honest test.
  `prove_it.sh` breaks `top_words` in a temporary copy and runs both halves.
  The four stay green.
- **That testing predates pytest and survives without it.**
  `examples/unittest_demo.py` and `examples/doctest_demo.py` run the same ideas
  on the standard library alone, so you can still write tests on a machine
  where you cannot install anything.

The lab's own test suite is unusual and worth knowing about before you start:
it is a test suite *about* a test suite. Three of its checks copy the code to a
temporary directory, break exactly one line, and demand that pytest exits
non-zero. That is the check that proves the rest mean anything.

## Learning objectives

- Install a pinned third-party tool into a lab-local virtual environment and
  verify the version you got.
- Write tests as plain functions in arrange-act-assert form, with names that
  describe the behaviour being pinned rather than the function being called.
- Use `pytest.approx` for a floating-point comparison and
  `pytest.raises(..., match=...)` for an expected exception with a pinned
  message.
- Group related tests in a `Test*` class and recognise that this adds nothing
  but organisation — no base class, no setup method, no framework.
- Read a pytest failure report: the `>` line, the `E   assert ...` explanation,
  the `where` clause, the short test summary, and the final counts.
- Drive a run with `-q`, `-v`, `-x`, `-k` and `--tb=short`, and read
  `--collect-only` output to see exactly what was found.
- Name pytest's exit codes from observation, including the one that means "no
  tests ran" — and check them yourself with `echo $?`.
- Prove your own suite is not vacuous by breaking the implementation on purpose
  and confirming the suite goes red.

## Prerequisites

- The Day 71 lesson (read it first — this lab is its exercise).
- Day 70: the domain model whose rules you could not re-check by hand, which is
  why today exists.
- Day 66: raising exceptions on purpose — `pytest.raises` asserts about exactly
  that.
- Day 43: `python3 -m venv`. This lab uses it; it does not re-teach it.
- Days 57–62: functions, modules, imports, and reading a traceback.
- A text editor, a terminal, and one network connection for the single install
  step.

## Supported operating systems

- **macOS** — fully supported (authored and executed on macOS 26.5.1, Apple
  Silicon, Python 3.14.0, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.9+ and bash).
- **Windows** — use WSL and follow the Linux path. Without WSL the virtual
  environment's tools live at `.venv\Scripts\pytest` rather than
  `.venv/bin/pytest`, `python` may be spelled `python` rather than `python3`,
  and `tests/run_tests.sh` needs a bash (Git Bash or WSL). The pytest commands
  themselves are identical.

## Hardware requirements

Any computer that runs Python 3. The module under test is under a hundred
lines, the reference suite is nineteen tests, and a full run takes about a
hundredth of a second. The virtual environment created by the install step is a
few tens of megabytes. No GPU, no special memory, no disk to speak of.

## Required software

- `python3`, version 3.9 or newer (authored on 3.14.0). Check with
  `python3 --version`.
- `pytest==9.1.1`, installed into a lab-local virtual environment by the
  Installation step below. This is the first lab in the course with a real
  dependency.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Everything else the lab uses — `unittest`, `doctest`, `re`, `math` — ships
  with Python.

Full detail, including the licence and the four packages pytest pulls in, is in
[`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source. pytest is distributed under the MIT
licence, with no paid tier, no account, and no telemetry — and you do not have
to take that on trust, because the package will tell you itself once installed:

```bash
.venv/bin/pip show pytest
```

which reports `Version: 9.1.1`, `License-Expression: MIT`, and
`Requires: iniconfig, packaging, pluggy, pygments`.

If you cannot install anything at all — a locked-down machine, no network — the
lab still has something for you. `examples/plain_asserts.py`,
`examples/unittest_demo.py` and `examples/doctest_demo.py` need nothing beyond
Python itself, and between them they demonstrate the entire idea of testing.
The pytest-dependent parts are the reporting and the ergonomics, which are
worth a great deal but are not the concept.

## Installation

One command touches the network; everything after it runs offline.

```bash
cd labs/sections/programming-with-python/day-071-why-test-and-pytest-basics
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

The last command should print `pytest 9.1.1`. `.venv/` is ignored by version
control repository-wide; never commit it, and delete it whenever you like — it
rebuilds in seconds.

If you already have pytest 9.x elsewhere you do not need a second copy. The
test runner resolves the tool in three steps — an explicit `PYTEST` override,
then this lab's `.venv/bin/pytest`, then whatever is on `PATH` — so both of
these work:

```bash
bash tests/run_tests.sh
PYTEST=/full/path/to/pytest bash tests/run_tests.sh
```

If none of the three finds a pytest, the runner stops with these instructions
rather than quietly reporting success on nothing. A suite that skips itself and
exits 0 is the exact failure this lab teaches you to distrust.

## File structure

```text
day-071-why-test-and-pytest-basics/
├── README.md                            ← you are here
├── metadata.yml                         ← machine-readable lab metadata
├── examples/
│   ├── textstats.py                     ← the FIXED reference module (both bugs repaired)
│   ├── test_textstats.py                ← the worked reference suite, 19 tests
│   ├── conftest.py                      ← SAMPLE constant and the sample_text fixture
│   ├── pytest.ini                       ← makes examples/ the rootdir
│   ├── plain_asserts.py                 ← a test suite with no runner at all
│   ├── unittest_demo.py                 ← the same tests under the stdlib runner
│   ├── doctest_demo.py                  ← tests living inside docstrings
│   ├── failure-demo/                    ← five tests that fail ON PURPOSE
│   │   ├── test_failure_report.py        ← number, list, dict, string, missing exception
│   │   ├── unittest_failure.py           ← the same failures without assertion rewriting
│   │   └── pytest.ini
│   └── vacuous-demo/                    ← four worthless tests and one honest one
│       ├── test_vacuous.py
│       ├── textstats.py
│       ├── prove_it.sh                   ← breaks the code and proves the point
│       └── pytest.ini
├── starter/
│   ├── textstats.py                     ← the BUGGY module (exercise 8 repairs it)
│   ├── test_textstats.py                ← YOUR suite: exercises 1-8
│   ├── conftest.py                      ← provided complete
│   └── pytest.ini                        ← makes starter/ the rootdir
├── tests/
│   └── run_tests.sh                     ← 47 checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt                   ← real captured session, thirteen sections
│   ├── test-run.txt                     ← real captured run of the test suite
│   └── FIELDS.md                        ← required counts, exit codes, and behaviour
├── requirements/
│   ├── requirements.txt                 ← pytest==9.1.1
│   └── README.md                        ← what it is, why, licence, install
├── troubleshooting.md
└── security.md
```

Both `pytest.ini` files exist for a reason explained inside them: they fix the
rootdir, so reports print short paths relative to a directory you chose rather
than one pytest wandered up to.

## How to run

From this directory, after the Installation step:

```bash
# 1. See the target: the finished reference suite, in full and quiet.
.venv/bin/pytest examples
.venv/bin/pytest examples -q

# 2. See what pytest FOUND, without running anything.
.venv/bin/pytest examples --collect-only -q

# 3. Select a subset by name.
.venv/bin/pytest examples -k reading_time

# 4. Read five deliberate failures, then the same run stopped at the first.
.venv/bin/pytest examples/failure-demo
.venv/bin/pytest examples/failure-demo -x --tb=short

# 5. Watch four green tests certify a broken function.
bash examples/vacuous-demo/prove_it.sh

# 6. Testing without pytest: bare asserts, unittest, doctest.
python3 examples/plain_asserts.py
python3 examples/unittest_demo.py -v
python3 examples/doctest_demo.py

# 7. Your work: open starter/test_textstats.py and complete exercises 1-8.
.venv/bin/pytest starter -v

# 8. Check everything.
bash tests/run_tests.sh
```

## What the commands do

- `.venv/bin/pytest examples` — runs the reference suite and prints the full
  report: the header naming the platform, versions, rootdir and config file;
  nineteen dots; and the summary line `19 passed in 0.01s`. Exit 0.
- `.venv/bin/pytest examples -q` — the same run without the header. This is
  what you will actually live in while working.
- `.venv/bin/pytest examples --collect-only -q` — performs collection and
  stops. Prints all nineteen test ids in the form
  `test_textstats.py::TestTopWords::test_returns_exactly_n_items`, then
  `19 tests collected`. This is the first diagnostic whenever pytest behaves
  unexpectedly, because half of all confusing sessions turn out to be "it never
  collected the file you thought it did".
- `.venv/bin/pytest examples -k reading_time` — collects all nineteen, then
  filters to the five whose ids contain that substring: `5 passed, 14
  deselected`. Deselected, not skipped — they never ran. `-k` also understands
  `and`, `or` and `not`.
- `.venv/bin/pytest examples/failure-demo` — five failures on purpose, each
  showing a different kind of explanation: an arithmetic comparison with a
  `where` clause naming the call, a list diff naming the index that differs, a
  dict diff naming the key, a character-aligned string diff, and
  `DID NOT RAISE ValueError` from a `pytest.raises` block that saw no
  exception. Ends with the short test summary and exit 1.
- `.venv/bin/pytest examples/failure-demo -x --tb=short` — the same suite,
  stopped after the first failure, with one-frame tracebacks. `1 failed`, exit
  1. Compare the two outputs; the difference is the entire skill of reading
  pytest.
- `bash examples/vacuous-demo/prove_it.sh` — copies that directory to a
  temporary one, breaks `top_words` with a single `sed`, and runs the suite
  twice: once with only the four vacuous tests selected (they pass), once with
  only the honest test (it fails). Nothing in your working tree is touched. The
  script itself exits 0 only if both halves behave as described.
- `python3 examples/plain_asserts.py` — a test suite made of nothing but
  `assert`. Prints `all plain assertions held` and exits 0. Break
  `examples/textstats.py` and it exits 1 with an `AssertionError` and no
  explanation whatsoever — which is precisely the gap assertion rewriting
  fills.
- `python3 examples/unittest_demo.py -v` — the same six behaviours under the
  standard library's runner: a `TestCase` subclass, `assertEqual`,
  `assertAlmostEqual`, `assertRaises`. `Ran 6 tests`, `OK`, exit 0. Nothing was
  installed to make this work.
- `python3 examples/doctest_demo.py` — runs the examples embedded in two
  docstrings and reports `doctest: 8 examples attempted, 0 failed`.
  `python3 -m doctest examples/doctest_demo.py` does the same and prints
  nothing at all on success.
- `.venv/bin/pytest starter -v` — your suite. Before you write anything it
  reports `1 passed, 9 skipped` and exits 0, because each unfinished exercise
  ends in a `pytest.skip(...)` line. Replace those with real assertions as you
  go.
- `bash tests/run_tests.sh` — the lab's own 47 checks: the tool version, the
  reference suite, collection and selection, failure reporting, exit codes, the
  break-it-on-purpose proofs, the starter, and the three standard-library
  runners. Exits 0 only if every check passes.

## Expected output

The full captured session — thirteen sections covering every command above,
all four exit codes, and the collision you get from running two directories at
once — is in [`expected-output/sample-run.txt`](expected-output/sample-run.txt).
The heart of it:

```text
$ pytest examples
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
rootdir: <repo>/labs/sections/programming-with-python/day-071-why-test-and-pytest-basics/examples
configfile: pytest.ini
plugins: cov-7.1.0, anyio-4.14.2
collected 19 items

examples/test_textstats.py ...................                           [100%]

============================== 19 passed in 0.01s ==============================
exit: 0
```

and the failure that explains why pytest needs no `assertEqual`:

```text
    def test_a_simple_number_comparison():
>       assert add(1, 2) == 3
E       assert 4 == 3
E        +  where 4 = add(1, 2)

examples/failure-demo/test_failure_report.py:20: AssertionError
```

and the demonstration the whole lab is built around:

```text
$ bash examples/vacuous-demo/prove_it.sh
Breaking top_words: ranked[:n] becomes ranked[: n - 1]

--- the four vacuous tests, on the BROKEN module ---
....                                                                     [100%]
4 passed, 1 deselected in 0.00s
exit: 0

--- the one honest test, on the same BROKEN module ---
F                                                                        [100%]
E   AssertionError: assert [('a', 3)] == [('a', 3), ('b', 2)]
E     Right contains one more item: ('b', 2)
1 failed, 4 deselected in 0.01s
exit: 1

Point made: four green tests, one broken function, zero warnings.
```

Two things in the captures are sanitized and nothing else is: absolute paths
appear as `<repo>`, and the interpreter path pytest prints under `-v` appears
as `<venv>/bin/python3.14`. The `plugins:` line lists whatever happens to be
installed alongside pytest — a clean lab `.venv` built from
`requirements.txt` shows no `plugins:` line at all. Every count, every dot, and
every exit code is exactly what the command printed.

Nothing in this lab reads the clock, the network, or a random number, so the
same commands produce the same counts on any machine with the same pytest
version. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the
required result of every command, pytest's six exit codes, the full
specification of the module under test, and the two bugs stated plainly.

## Validation steps

1. `.venv/bin/pytest --version` prints `pytest 9.1.1`.
2. `.venv/bin/pytest examples -q` reports `19 passed` and exits 0.
3. `.venv/bin/pytest examples --collect-only -q` ends with `19 tests
   collected`, and exactly five of the ids contain `::TestTopWords::`.
4. `.venv/bin/pytest examples -k reading_time` reports
   `5 passed, 14 deselected`.
5. `.venv/bin/pytest examples/failure-demo` exits 1 and its report contains
   `E       assert 4 == 3`, `At index 4 diff:`, and `DID NOT RAISE ValueError`.
6. In an empty directory, `pytest . -q` prints `no tests ran` and exits **5**.
   Check it yourself with `echo $?` — this is the number that makes naive build
   scripts ship untested code.
7. `bash examples/vacuous-demo/prove_it.sh` ends with `Point made: four green
   tests, one broken function, zero warnings.` and exits 0.
8. With exercises 1–7 written but `starter/textstats.py` not yet repaired,
   `.venv/bin/pytest starter -q` FAILS — exercise 4 and at least one
   `TestTopWords` method. That failure is the lab working, not you failing.
9. With exercise 8 finished, `.venv/bin/pytest starter -q` reports `10 passed`
   and exits 0.
10. Re-break one line of `starter/textstats.py`, run again, and confirm the
    suite goes red and exits 1. Then undo it. **Do not skip this step** — it is
    the only evidence that step 9 meant anything.
11. `bash tests/run_tests.sh` ends with `47 checks, 0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `47 checks, 0 failure(s).`, and the process exits 0. A
full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt). The checks are
grouped into nine sections, printed as they run:

| Section | What it proves |
| --- | --- |
| 1. The tool itself | `pytest --version` reports a pytest |
| 2. The reference suite passes | `pytest examples` exits 0 and reports 19 passed |
| 3. Collection | four specific test ids are collected, exactly 19 are found, `TestTopWords` contributes 5, and two different `-k` expressions each select 5 of 19 |
| 4. Failure reporting | the demo exits 1, assertion rewriting shows `assert 4 == 3` and its `where` line, a list diff names the index, `pytest.raises` reports a missing exception, the short summary lists every failure, and `-x` stops at the first |
| 5. Exit codes | a run that collects nothing exits 5, not 0 |
| 6. The suite tests something | the control run is green; one `sed` edit to `word_count` makes it fail; the reference suite rejects the buggy starter with exactly `4 failed, 15 passed`; both bugs are still present in `starter/` and both repairs present in `examples/`; and the vacuous demonstration behaves as claimed |
| 7. The starter | it runs before you start — `1 passed, 9 skipped`, 10 collected, exit 0 |
| 8. Without pytest | bare asserts pass and fail correctly, `unittest` passes, its failure demo reports both sides while a bare assert inside it reports nothing, and `doctest` runs all 8 documented examples |
| 9. Determinism | no network, clock or randomness anywhere in `examples/` or `starter/` |

Section 6 is the one to read before you run it. Its checks copy code into a
directory made with `mktemp -d`, break exactly one line with `sed`, and demand
a **non-zero** exit. A suite that stays green when the code is wrong is worse
than no suite at all, and these checks are the lab holding itself to the
standard it teaches. Nothing inside the lab directory is ever modified, so a
failing run cannot corrupt your work.

The runner needs no network and asks no questions, so it is safe to run in
continuous integration. It resolves pytest through `PYTEST`, then
`.venv/bin/pytest`, then `PATH`, and stops loudly if it finds none.

## Cleanup

```bash
# Remove Python's bytecode cache (always safe).
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +

# Optional: remove the installed pytest. It rebuilds in seconds.
rm -rf .venv

# Optional: reset your work on the exercises.
git checkout -- starter/
```

The lab writes nothing else. `prove_it.sh` and the test runner create their own
directories with `mktemp -d` and delete each one as that check finishes. This
lab disables pytest's cache via `addopts = -p no:cacheprovider` in both
`pytest.ini` files, so no `.pytest_cache` directory appears.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list — every symptom
in it was produced on purpose while building the lab, and the messages are
quoted from real runs. The ones you are most likely to meet:
`pytest: command not found` (you are not using `.venv/bin/pytest`);
`no tests ran` with exit code 5 (collection found nothing — wrong path, or a
file not named `test_*.py`); `ModuleNotFoundError: No module named 'textstats'`
(you ran pytest from inside `starter/` or from the repository root instead of
from this directory); `fixture 'sample_text' not found` (the parameter name and
the fixture name must match exactly — the match is by name and nothing else);
`ERROR collecting test_textstats.py` with `import file mismatch` (you ran
`pytest starter examples`, and the two identically named files collided — run
one directory at a time); and `ZeroDivisionError` from
`average_word_length("")`, which is not a problem but bug 1, caught.

## Security notes

See [security.md](security.md). Short version, and the security lesson of the
day: **test code is code**. pytest *imports* every file it collects, and
importing runs the module body — so a file named `test_anything.py` in a
directory you point pytest at executes with your privileges before a single
assertion is evaluated. `conftest.py` is imported automatically, without any
file naming it, which makes it the quietest place in a repository to hide code
that runs on every invocation; read its diff as carefully as you read the
source diff. Beyond that: install into a virtual environment and never with
`sudo`; pin versions and read the package name you are typing, because
typo-squatting is an ordinary attack; keep real credentials out of test files,
since a failing assertion prints both sides of the comparison straight into a
build log; and remember that `python -O` strips `assert` statements entirely,
which is fine for tests and disqualifying for runtime validation of untrusted
input.

## Extension exercises

1. **Write your own runner.** In about forty lines of standard-library Python
   and no pytest, walk a directory, import every `test_*.py`, call every
   module-level `test_*` callable inside a `try`/`except AssertionError`, print
   a `.` or an `F`, print the failures and a count, and exit 0 only if all
   passed. Run it against `examples/`. Two things will happen: the fixture
   tests will fail because you did not implement fixtures, and every failure
   will say `AssertionError` and nothing else because you did not rewrite the
   assertions. Write down in two sentences what fixing the second would take.
2. **Find a third bug.** The specification in the docstrings is more detailed
   than the reference suite checks. Read `examples/textstats.py` against its
   own docstrings and find a behaviour no test currently pins — then write the
   test, and decide whether the code or the docstring should change.
3. **Break each function in turn.** For each of the five functions, make one
   small edit to `examples/textstats.py` in a copy, run
   `.venv/bin/pytest . -q --tb=line`, and record which tests caught it. Any
   function you can break without turning the suite red has a coverage hole
   with your name on it.
4. **Make a test flaky on purpose.** Add a test that asserts something about
   the current second, run it in a loop with
   `for i in $(seq 60); do pytest -q -k flaky || break; done`, and watch it
   fail eventually. Then remove it. Knowing what a flaky failure looks and
   feels like is worth more than being warned about one.
5. **Compare the runners honestly.** Write the same three tests three times —
   as bare asserts, under `unittest`, and under pytest — break the module, and
   put the three failure reports side by side. Time yourself reading each one.
   That number is what pytest is actually selling.

## Navigation

- **Previous day:** Day 70 — Modeling a Domain with Objects
  (`labs/sections/programming-with-python/day-070-modeling-a-domain-with-objects/`).
- **Next day:** Day 72 — fixtures and parametrisation, which turn the
  `sample_text` fixture you used today into a subject of its own
  (`labs/sections/programming-with-python/`).
- **Week 11 project:** the Tested Utility Library
  (`labs/sections/programming-with-python/projects/week-11/`). It applies this
  week's tools — pytest, fixtures, mocking, type checking and linting — to a
  library you build and keep.
