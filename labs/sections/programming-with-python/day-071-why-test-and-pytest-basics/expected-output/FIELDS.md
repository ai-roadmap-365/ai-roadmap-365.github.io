# Expected output — Day 071 lab

These are real captured runs from the authoring machine (macOS 26.5.1, Apple
Silicon, Python 3.14.0, pytest 9.1.1, bash 3.2.57, 2026-07-19). Nothing in this
lab reads the clock, the network, or a random number, so the same commands
produce the same counts on any machine with the same pytest version.

## Files

- `sample-run.txt` — thirteen captured sections: the reference suite in full,
  quiet and verbose; collection only; `-k` selection; a full failure report;
  the same failures under `--tb=short`, `--tb=line` and `-x`; the same three
  failures under `unittest`; the starter before you write anything; the four
  exit codes; a one-line break making the suite fail; the vacuous-test
  demonstration; `unittest`, `doctest` and bare `assert` runs; and the
  collection error you get from running two directories at once.
- `test-run.txt` — a full run of `bash tests/run_tests.sh`: 47 checks, 0
  failures, exit 0.

## Two sanitizations, so you know what you are looking at

1. Absolute paths appear as `<repo>`. On your machine they are your real
   repository path.
2. In `-v` output pytest prints the interpreter it is running under. That path
   appears as `<venv>/bin/python3.14`. On your machine, having followed
   `requirements/README.md`, it is this lab's `.venv/bin/python3.14`.

Nothing else is edited. Every count, every dot, every exit code below is what
the command actually printed.

## What varies between machines, and what does not

| Line | Varies? | Why |
| --- | --- | --- |
| `platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0` | Yes | Your platform, Python and pluggy versions. `pytest-9.1.1` must match, because `requirements.txt` pins it |
| `rootdir: .../examples` | Path only | The rootdir is always the directory holding the `pytest.ini` that was found |
| `configfile: pytest.ini` | No | This lab ships that file on purpose |
| `plugins: cov-7.1.0, anyio-4.14.2` | Yes | Whatever plugins happen to be installed alongside pytest. A clean lab `.venv` shows no plugins line at all |
| `19 passed in 0.01s` | Duration only | The count 19 is fixed; the seconds are not |
| Every exit code | No | Exit codes are a contract, not a report |

## Required counts and exit codes

Your finished work must reproduce exactly this:

| Command | Result |
| --- | --- |
| `pytest examples` | `19 passed`, exit `0` |
| `pytest examples --collect-only -q` | `19 tests collected`, exit `0` |
| `pytest examples -k reading_time` | `5 passed, 14 deselected`, exit `0` |
| `pytest examples -k "top_words or TestTopWords"` | `5 passed, 14 deselected`, exit `0` |
| `pytest examples/failure-demo` | `5 failed`, exit `1` |
| `pytest examples/failure-demo -x` | `1 failed`, exit `1` |
| `pytest examples/vacuous-demo` | `5 passed`, exit `0` (all five pass; four of them are worthless anyway) |
| `pytest starter` (exercises unfinished) | `1 passed, 9 skipped`, exit `0` |
| `pytest starter --collect-only -q` | `10 tests collected` |
| `pytest .` in an empty directory | `no tests ran`, exit **`5`** |
| `pytest starter examples` | collection error, exit `2` — two files named `test_textstats.py` |
| `python3 examples/plain_asserts.py` | `all plain assertions held`, exit `0` |
| `python3 examples/unittest_demo.py` | `Ran 6 tests`, `OK`, exit `0` |
| `python3 examples/doctest_demo.py` | `doctest: 8 examples attempted, 0 failed`, exit `0` |
| `python3 -m doctest examples/doctest_demo.py` | no output at all, exit `0` |
| `python3 examples/failure-demo/unittest_failure.py` | `FAILED (failures=3)`, exit `1` |
| `bash examples/vacuous-demo/prove_it.sh` | `4 passed` then `1 failed`, exit `0` |
| `bash tests/run_tests.sh` | `47 checks, 0 failure(s).`, exit `0` |

## pytest's exit codes, which is what CI reads

| Code | Meaning | Seen in this lab |
| --- | --- | --- |
| 0 | All collected tests passed | `pytest examples` |
| 1 | Tests ran and at least one failed | `pytest examples/failure-demo` |
| 2 | The run was interrupted — including a collection error | `pytest starter examples` |
| 3 | An internal error happened while running tests | not triggered here |
| 4 | pytest was used wrongly on the command line | not triggered here |
| 5 | No tests were collected | `pytest .` in an empty directory |

Code 5 is the one that matters most in practice, and the reason a build script
must never be written as "if pytest did not print FAILED, ship it". A typo in a
path collects nothing, prints no failure, and returns 5. Anything that treats
"not 1" as success ships on a suite that never ran.

## Required behaviour of the module under test

The docstrings in `starter/textstats.py` are the specification. Restated as a
table, with every number checkable by hand:

| Call | Result |
| --- | --- |
| `words("The cat. The hat!")` | `['the', 'cat', 'the', 'hat']` |
| `words("don't stop")` | `["don't", 'stop']` — an apostrophe stays inside a word |
| `words("3 apples & 4 pears")` | `['apples', 'pears']` — digits and symbols separate |
| `words("")` | `[]` |
| `word_count(SAMPLE)` | `12` (the sample sentence, counted by hand in `conftest.py`) |
| `word_count("")` | `0` |
| `average_word_length("the cat")` | `3.0` |
| `average_word_length(SAMPLE)` | `3.83` — 46 characters over 12 words |
| `average_word_length("")` | `0.0` — **bug 1**: the starter raises `ZeroDivisionError` |
| `top_words("a b a c a b", 2)` | `[('a', 3), ('b', 2)]` — **bug 2**: the starter returns `[('a', 3)]` |
| `top_words("a b a c a b", 9)` | `[('a', 3), ('b', 2), ('c', 1)]` |
| `top_words("a b a c a b", 0)` | `[]` — the starter returns two items, because `ranked[:-1]` |
| `top_words("", 5)` | `[]` |
| `top_words(SAMPLE, 3)` | `[('the', 3), ('dog', 2), ('barks', 1)]` — ties broken alphabetically |
| `reading_time_minutes("hello there")` | `1` |
| `reading_time_minutes("word " * 500)` | `3` — 500/200 is 2.5, always rounded up |
| `reading_time_minutes("word " * 500, 100)` | `5` |
| `reading_time_minutes("")` | `0` |
| `reading_time_minutes(SAMPLE, 0)` | raises `ValueError("words_per_minute must be positive, got 0")` |

## The two bugs, stated plainly

1. `average_word_length` divides by `len(found)` without checking whether
   `found` is empty, so empty text raises `ZeroDivisionError` instead of
   returning `0.0`. Caught by
   `test_average_word_length_of_empty_text_is_zero`.
2. `top_words` slices `ranked[: n - 1]`, off by one, because a slice already
   stops *before* its end index. Asking for two gives one; asking for zero
   gives everything but the last. Caught by three of the five `TestTopWords`
   tests.

Running the reference suite against the buggy module gives exactly
`4 failed, 15 passed` — one failure for bug 1 and three for bug 2. The test
runner asserts that count, so if you change either module the count has to be
updated with it.
