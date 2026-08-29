# Day 072 lab — A Suite That Scales

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Fixtures, Parametrization, and Test Design
- **Day number:** 72 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-072-fixtures-parametrization-and-test-design
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-072-fixtures-parametrization-and-test-design` when the site is running.
<!-- generated-links:end -->

## Purpose

You have inherited a test suite. It passes. Thirteen tests, green, no
warnings — and eight copies of the same six lines of setup, plus five tests
that differ only in one value each.

Nobody would reject that suite in review on correctness grounds. It is still
the suite that stops a team from adding tests, because the cost of a new test
is now "find the nearest similar one and copy it", and every copy is another
place that has to be edited when the constructor gains an argument.

Your job in this lab is to fix it without losing a single assertion, and to
**measure** the difference rather than assert it. You will extract fixtures
built on pytest's `tmp_path`, choose a scope for each one and prove that
choice with a run that counts how many times each fixture body executes,
collapse five near-identical tests into one parametrized test that still
reports as five independent items, build a nine-item cross product from two
stacked decorators, register a marker, select subsets with `-m` and `-k`, and
record a known gap as an `xfail` instead of deleting the test.

The check that matters most is the one at the end: the harness copies the
finished suite, damages one comparison in the code under test, and requires
the suite to go red. A suite that stays green against broken code is not a
suite. It is decoration with a green tick.

## Learning objectives

- Recognise the two distinct kinds of duplication in a test suite — repeated
  *arrangement* and repeated *assertion shape* — and apply the right tool to
  each: a fixture for the first, parametrization for the second.
- Write a `@pytest.fixture`, request it by parameter name, and explain why
  pytest resolves fixtures by argument name rather than by import.
- Build a fixture on top of other fixtures, and read the resulting dependency
  chain as the replacement for a page of copy-pasted setup.
- Choose a fixture scope deliberately, and verify the choice by counting how
  many times each fixture body actually runs in a real captured run.
- Use `yield` for teardown, and prove that the teardown half runs even when
  the test it served has failed.
- Place fixtures in `conftest.py` and predict, from the directory layout
  alone, which test files can see them.
- Use the built-in `tmp_path`, `capsys` and `monkeypatch` fixtures, and say
  what each one guarantees that a hand-rolled equivalent does not.
- Convert repetitive tests to `@pytest.mark.parametrize`, give the cases
  readable `ids=`, and confirm with `--collect-only -q` that N cases really
  became N independent test items.
- Register markers, select with `-m` and `-k`, and record a known gap with
  `pytest.param(..., marks=pytest.mark.xfail)`.
- Judge when a plain helper function is the better answer than a fixture.

## Prerequisites

- The Day 72 lesson, and Day 71 before it — why we test, arrange-act-assert,
  reading a pytest report, and proving a test can fail.
- Day 69: dataclasses, `frozen=True`, `__post_init__` and type hints. The
  code under test is one of these.
- Days 64–65: reading and writing files, and the `csv` module. The store this
  lab tests is a CSV file with a header row.
- Day 66: raising exceptions on purpose, which is what the validation tests
  assert on.
- Day 43: `python3 -m venv`. This is the first lab in the course with a
  third-party dependency, and that is how you install it.
- A text editor and a terminal.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path. In a native Windows shell
  the bash harness will not run, but every `pytest` command in this README
  works unchanged in PowerShell after activating the virtual environment with
  `.venv\Scripts\activate`. All the counts are identical.

## Hardware requirements

Any computer that runs Python 3. The suites here finish in well under a
second, the largest file the lab writes is a four-line CSV, and pytest itself
is a few megabytes. No special memory, disk, GPU, or accelerator.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `pytest` version 9.1.1, pinned in
  [`requirements/requirements.txt`](requirements/requirements.txt).
- `bash` for the outer test harness (preinstalled on macOS and Linux).

See [`requirements/README.md`](requirements/README.md) for the full
dependency statement, including what to do if you cannot install anything.

## Free and open-source options

Everything here is free and open source. pytest is distributed under the MIT
licence; Python under the Python Software Foundation Licence. There is no
account to create, no key to obtain, and no paid tier involved at any point.

The lesson's Alternatives section covers the other ways to do what this lab
does — `unittest` with `setUp`/`tearDown` (in the standard library, so already
installed), plain factory functions (no dependency at all), `factory_boy` with
`pytest-factoryboy`, and Hypothesis for generating cases instead of listing
them. All of those are free and open source too. None is needed here.

## Installation

The install is the only step in this lab that uses the network. Run it once:

```bash
cd labs/sections/programming-with-python/day-072-fixtures-parametrization-and-test-design
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

That last line should print `pytest 9.1.1`. Everything after this point runs
fully offline.

Throughout this README, `pytest` means `.venv/bin/pytest` (or `../.venv/bin/pytest`
when you are inside `starter/` or `examples/`). If you prefer, activate the
environment once with `source .venv/bin/activate` and type `pytest` plainly.

## File structure

```text
day-072-fixtures-parametrization-and-test-design/
├── README.md                        ← you are here
├── metadata.yml                     ← machine-readable lab metadata
├── starter/
│   ├── practice_store.py            ← the code under test (complete, working)
│   ├── test_practice_store.py       ← the suite you inherited: 13 tests, 8 copies of the setup
│   ├── pytest.ini                   ← marks the root of the starter suite
│   └── refactoring-worksheet.md     ← YOUR work: exercises 0-7 and the measurement table
├── examples/
│   ├── practice_store.py            ← identical copy of the code under test
│   ├── conftest.py                  ← the five shared fixtures
│   ├── pytest.ini                   ← registered markers + --strict-markers
│   ├── test_sessions.py             ← the parametrized value rules (21 items from 4 functions)
│   ├── test_store.py                ← store behaviour, entirely fixture-driven (10 items)
│   ├── test_builtin_fixtures.py     ← tmp_path, capsys, monkeypatch, and one honest helper
│   └── scopes/
│       ├── conftest.py              ← a second conftest layer, visible only here
│       ├── test_scopes_first.py     ← three tests requesting all three scopes
│       └── test_scopes_second.py    ← a second module, plus a test that fails on purpose
├── tests/
│   └── run_tests.sh                 ← the outer harness; exits 0 only if all 38 checks pass
├── expected-output/
│   ├── sample-run.txt               ← real captured runs of both suites
│   ├── test-run.txt                 ← real captured run of the harness
│   ├── broken-run.txt               ← what the suite does when the code is damaged
│   └── FIELDS.md                    ← every number that is required, and why
├── requirements/
│   ├── requirements.txt             ← pytest==9.1.1
│   └── README.md                    ← dependency statement
├── troubleshooting.md
└── security.md
```

The lab writes no files into your working directory. Everything the tests
create goes into a directory pytest makes for them under the system
temporary area, and the harness cleans up after itself.

## How to run

From this directory, after the install:

```bash
# 1. Meet the suite you inherited. It passes. Count the duplication.
cd starter
../.venv/bin/pytest -q
../.venv/bin/pytest --collect-only -q | tail -2
grep -c 'store = PracticeStore(path)' test_practice_store.py
cd ..

# 2. Read the worksheet. Exercises 0 to 7, in order.
cat starter/refactoring-worksheet.md

# 3. Do the work in starter/. Create conftest.py, extract the fixtures,
#    parametrize the five rejection tests, register a marker.

# 4. See the finished reference and how many items it collects.
cd examples
../.venv/bin/pytest -q
../.venv/bin/pytest --collect-only -q | tail -2

# 5. The check that proves parametrization expanded: read the ids.
../.venv/bin/pytest --collect-only -q test_sessions.py

# 6. Select subsets two ways — by marker, and by substring.
../.venv/bin/pytest --collect-only -q -m validation | tail -2
../.venv/bin/pytest --collect-only -q -k refuses | tail -2

# 7. Watch fixture scope happen. -s stops pytest swallowing print output.
../.venv/bin/pytest scopes -s -q
cd ..

# 8. Run the outer harness, which checks all of the above and more.
bash tests/run_tests.sh
```

## What the commands do

- `pytest -q` in `starter/` — runs the inherited suite. `13 passed`. Quiet
  mode prints one character per test and the summary line; that is all you
  need until something breaks.
- `pytest --collect-only -q` — collects tests without running any of them and
  lists their ids. This is the single most useful pytest flag for today: it
  answers "what does pytest think my suite contains?", which is exactly the
  question parametrization makes non-obvious.
- `grep -c 'store = PracticeStore(path)' test_practice_store.py` — counts the
  copies of the setup. It prints `8`. That number is the lab's premise, and
  the first row of your measurement table.
- `pytest -q` in `examples/` — runs the refactored suite: `39 passed, 2
  xfailed`. The two `xfailed` are deliberate and explained below.
- `pytest --collect-only -q test_sessions.py` — shows the expansion. Four
  test functions become twenty-one items, each with the readable id its
  `ids=` argument gave it. Compare `[minutes-zero]` with what you would get
  without `ids=`: `[minutes4]`.
- `pytest --collect-only -q -m validation` — selects by **marker**, a label
  attached to a test in code. `21/41 tests collected (20 deselected)`.
- `pytest --collect-only -q -k refuses` — selects by **substring of the test
  id**, parameter ids included. `11/41 tests collected (30 deselected)`. Note
  that `-k` needs no code changes at all, which makes it the flag you reach
  for while debugging and `-m` the one you put in a configuration file.
- `pytest scopes -s -q` — the scope demonstration. Each fixture prints when
  its body runs, and `-s` (short for `--capture=no`) stops pytest from
  swallowing that output. Across two modules and five tests you will see the
  session fixture run **once**, the module fixture **twice**, and the
  function fixture **four times**, each with a matching teardown.
- `bash tests/run_tests.sh` — 38 checks covering every claim above, plus the
  conftest-scoping rule, `--strict-markers`, and the deliberate break.

## Expected output

Full captures are in [`expected-output/`](expected-output/). The two most
important extracts:

**Parametrization expanded — one function, six independently reported cases:**

```text
$ cd examples && pytest --collect-only -q test_sessions.py
test_sessions.py::test_accepts_a_valid_session[shortest-allowed]
test_sessions.py::test_accepts_a_valid_session[typical]
test_sessions.py::test_accepts_a_valid_session[longest-allowed]
test_sessions.py::test_refuses_a_bad_value[ref-without-prefix]
test_sessions.py::test_refuses_a_bad_value[ref-too-short]
test_sessions.py::test_refuses_a_bad_value[topic-not-lower-case]
test_sessions.py::test_refuses_a_bad_value[topic-padded-with-spaces]
test_sessions.py::test_refuses_a_bad_value[minutes-zero]
test_sessions.py::test_refuses_a_bad_value[minutes-over-the-cap]
test_sessions.py::test_every_topic_accepts_every_legal_duration[1-python]
...
21 tests collected in 0.00s
```

**Scope is a number of executions, not a comment:**

```text
$ cd examples && pytest scopes -s -q

    [session] body ran

    [module ] body ran

    [funct  ] body ran
.
    [funct  ] teardown ran
...
    [funct  ] body ran
x
    [funct  ] teardown ran

    [module ] teardown ran

    [session] teardown ran

4 passed, 1 xfailed in 0.01s
```

Read the last few lines carefully. The `x` is the test that fails on purpose,
and the `[funct  ] teardown ran` line comes *after* it. That is the guarantee
`yield` gives you and a `try`/`finally` in every test does not.

[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists every number
that is required on every platform, and the one field (elapsed time) that is
allowed to differ.

## Validation steps

1. `cd starter && ../.venv/bin/pytest -q` reports `13 passed` before you
   start and `13 passed` after your refactor. Same assertions, fewer lines.
2. `grep -c 'store = PracticeStore(path)' starter/test_practice_store.py`
   prints `8` before your refactor and `0` after it.
3. `cd examples && ../.venv/bin/pytest --collect-only -q | tail -2` reports
   exactly `41 tests collected`.
4. `../.venv/bin/pytest --collect-only -q -k refuses | tail -2` reports
   exactly `11/41 tests collected (30 deselected)`.
5. `../.venv/bin/pytest --collect-only -q -m validation | tail -2` reports
   exactly `21/41 tests collected (20 deselected)`.
6. In `pytest scopes -s -q`, count the lines yourself:
   `grep -c '\[funct  \] body ran'` gives `4` and
   `grep -c '\[session\] body ran'` gives `1`.
7. Every test id in `pytest --collect-only -q test_sessions.py` ends in a
   name a human chose. If you see `[ref0]`, an `ids=` list is missing.
8. Break it on purpose and watch it go red — the most important check in the
   lab, and the one you should run by hand at least once:
   copy `examples/` somewhere temporary, change `if self.minutes <= 0:` to
   `if self.minutes < 0:` in the copy, and run the suite there. You must see
   `1 failed, 38 passed, 2 xfailed` and the failing case named as
   `test_refuses_a_bad_value[minutes-zero]`.
9. Every row of `starter/refactoring-worksheet.md` is filled in, including
   the measurement table and the closing design question, in sentences.
10. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `38 checks, 0 failure(s).` and exit code 0. A full
capture is in [`expected-output/test-run.txt`](expected-output/test-run.txt).

On the authoring machine the harness is run with an explicit pytest path; if
you installed the lab-local virtual environment above, it finds
`.venv/bin/pytest` on its own. To point it somewhere else:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The suite is worth reading before you run it, because its nine sections are
the lesson's claims turned into assertions. Three deserve attention:

- **Section 2** asserts exact collected counts. This is the only check that
  can tell the difference between "six independent test items" and "one test
  with a loop in it", and it is why `--collect-only` is in this lab at all.
- **Section 6** creates a test file that asks for a fixture defined in
  `examples/scopes/conftest.py` and requires pytest to refuse it. Conftest
  visibility flows downward only, and this proves it rather than asserting it.
- **Section 8** copies `examples/` into a temporary directory, changes one
  comparison with `sed`, and requires the suite to fail — with exactly one
  failure, naming exactly one parametrized case. The copy is deleted
  immediately; your files are never touched.

## Cleanup

```bash
rm -rf .venv                 # remove the virtual environment
git checkout -- starter/     # optional: reset your work
```

The tests write nothing into this directory. `tmp_path` directories live under
the system temporary area and pytest removes all but the last few runs
automatically; the harness deletes its own `mktemp -d` directories as each
check finishes.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `pytest not
found`, `fixture 'empty_store' not found` and its three usual causes, the
`--strict-markers` error on a mistyped marker, a `parametrize` that did not
expand, ids that look like `[ref0]`, a `[audit]` print you cannot see without
`-s`, `ModuleNotFoundError: No module named 'practice_store'`, and the classic
"passes alone, fails in the suite" — which is shared mutable state, and is
worth understanding rather than working around.

## Security notes

See [security.md](security.md). Short version: the only networked moment in
this lab is `pip install`, and it is worth treating as a real trust decision —
install into a virtual environment, pin the version, read the package name
before you run the command. `tmp_path` is a security feature, not a
convenience: a test that writes to a hard-coded path can clobber real data.
`monkeypatch` undoes itself, which is containment rather than tidiness. Never
put a credential in a test or a `conftest.py`, and remember that a
`conftest.py` is executable code that runs automatically before any test does.

## Extension exercises

1. **Delete a fixture on purpose.** Pick the fixture used by the fewest
   tests, inline it as a plain helper function, and read both versions. Which
   one lets a stranger see what the test sets up without opening another
   file? Write down your answer — "always use a fixture" is not a design
   position, it is a habit.
2. **Make a scope wrong and watch it bite.** Change `empty_store` in
   `examples/conftest.py` to `scope="module"` and run
   `pytest -q test_store.py`. Tests will start failing, and the failures will
   depend on order. Then explain, in one sentence, why `sample_sessions` is
   safe at session scope while `empty_store` is not. (The answer is one word,
   and the word is not "speed".)
3. **Parametrize the store tests.** `test_total_minutes_adds_the_right_sessions`
   is already parametrized over three topics. Add a fourth case for a topic
   that is not in the log at all, predict the expected value before you run
   it, and check the collected count went from 41 to 42.
4. **Add an indirect parametrization.** Look up `indirect=True` in the pytest
   documentation and use it to parametrize the `loaded_store` fixture itself,
   so the same test runs against an empty store and a full one. Then decide
   whether the result is clearer than two separate fixtures. Often it is not,
   and knowing when a feature is not worth it is the point of the day.
5. **Turn a marker into a workflow.** Add `-m "not slow"` to `addopts` in a
   second configuration file, so the default local run skips the file-reading
   test and a full run needs an explicit `-m slow`. Then write two sentences
   on what you have just traded away, because a test that never runs by
   default is a test that will eventually stop working without anyone noticing.

## Navigation

- **Previous day:** Day 71 — Why Test, and pytest Basics
  (`labs/sections/programming-with-python/day-071-why-test-and-pytest-basics/`).
- **Next day:** Day 73 — Test-Driven Development
  (`labs/sections/programming-with-python/day-073-test-driven-development/`),
  which takes today's suite design and inverts the order: the test first, the
  code second.
- **Week 11 project:** the Tested Utility Library
  (`labs/sections/programming-with-python/projects/week-11/`). Every fixture
  and every parametrized case you write there starts from what you built here.
