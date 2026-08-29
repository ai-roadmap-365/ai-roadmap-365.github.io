# Day 074 lab — Test the Logic, Stub the World

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Mocking and Testing Boundaries
- **Day number:** 74 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-074-mocking-and-testing-boundaries
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-074-mocking-and-testing-boundaries` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 74 is the day the week's testing techniques meet code that is not a pure
function. You are given a function that cannot be tested. `write_daily_report` reads the
clock, calls a remote service, computes a summary, and writes a file — four
responsibilities inside one body, three of them boundaries. There is no way to
check the summary without also paying for the other three.

You will fix it twice, and compare.

**First the painful way.** Leave the function exactly as it is and test it with
`unittest.mock.patch`: two patched names, a stubbed module object, a temporary
directory, and one string target that must be exactly right or the test
silently tests nothing. Along the way you will meet the rule that trips
everybody — **patch where the name is looked up, not where it was defined** —
and you will watch the wrong target fail in front of you rather than being told
about it.

**Then the real way.** Refactor until the clock and the client are *arguments*.
Write six test doubles by hand — a dummy, two stubs, two spies and a fake, none
longer than fifteen lines — and test the same behaviour with no patching at
all, no temporary directory, and nothing to undo. The suite proves the result
by running your core from a directory containing no files, exactly as Day 70
proved its domain core did no input or output.

Along the way the lab demonstrates, with real captured failures, the single
most expensive mistake in this whole subject: **an un-specced `Mock()` accepts
a misspelled method name**, so a test can be green while production raises
`AttributeError` on its first request. You will see the naive test pass, the
autospec'd test fail, and the real object break — three runs, same bug.

The last piece is the one that pays off later. A language model call is a
boundary with all three bad properties at once: slow, metered, and different
every time. `examples/model_boundary.py` puts one behind an injected interface
and tests the prompt building, the parsing, the retries and the failure path
deterministically, in milliseconds, for nothing.

## Learning objectives

- Name the six boundaries a unit test must not cross — the network, the clock,
  the filesystem, randomness, the environment, and other processes — and say
  which of slow, flaky or non-deterministic each one makes a test.
- Distinguish the five kinds of test double (dummy, stub, spy, mock, fake) and
  write one of each by hand in under fifteen lines.
- Use `unittest.mock` properly: `Mock`, `MagicMock`, `return_value`,
  `side_effect` for both sequences and exceptions, `assert_called_once_with`,
  and `call_args`.
- Demonstrate why an un-specced `Mock()` is dangerous, and fix it with `spec=`
  and `create_autospec` — including the case only autospec catches, a call with
  arguments the real method does not accept.
- Aim `patch` at the name a module **looks up**, explain why
  `from x import y` changes the target, and prove that a patch is undone on
  exit from its block.
- Refactor a function so its boundaries arrive as parameters, and test the
  result with hand-written fakes instead of patches.
- Assert on a retry schedule and a backoff without any test ever waiting.
- Test code that calls a language model without calling one, and explain what
  belongs in an evaluation suite instead.
- Judge, in writing, which of the two approaches each of your own tests should
  use.

## Prerequisites

- Day 71: what a test is, `assert`, running `pytest`, reading its output.
- Day 72: fixtures and `@pytest.mark.parametrize`; `tmp_path` in particular.
- Day 73: writing the failing test first — the discipline this lab assumes.
- Day 70: the pure domain core, the adapter ring, and the proof by running the
  core from an empty directory. Today is that idea applied to testing.
- Day 66: raising exceptions on purpose and designing a small exception family.
- Day 69: dataclasses, `frozen=True`, and type hints.
- Day 43: creating a virtual environment with `python3 -m venv`.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.10+ and bash).
- **Windows** — use WSL and follow the Linux path. Several headings and the
  report's first line contain an em dash, so a UTF-8 terminal is needed for
  them to render; the numbers, the exit codes and the assertions are unaffected.

## Hardware requirements

Any computer that runs Python 3. The whole lab is a few hundred lines of code,
the test suite finishes in a couple of seconds, and the only files written are
inside temporary directories. No special memory, disk, GPU, or network at test
time.

## Required software

- `python3` (3.10 or newer; tested on 3.14.0).
- `pytest` 9.1.1 — the one dependency, installed below.
- `bash` for the test runner (preinstalled on macOS and Linux).
- `unittest.mock` — already present. It is part of the standard library and
  needs no installation.

## Free and open-source options

Everything here is free and open source: Python, bash, the standard library,
and pytest (MIT — see [`requirements/README.md`](requirements/README.md)). No
account, no API key, no purchase, and no network access at any point after the
one-time install.

The lesson's Alternatives section discusses `pytest-mock`, `responses`,
`requests-mock` and `freezegun`. All four are free and open source, and **none
of them is used here** — the lab's argument is that hand-written doubles beat
all of them for a program this size, and it would be strange to make that
argument while depending on one.

## Installation

```bash
cd labs/sections/programming-with-python/day-074-mocking-and-testing-boundaries
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

That last command should print `pytest 9.1.1`. `.venv/` is ignored by version
control — never commit it. If you already have pytest elsewhere, skip the
virtual environment and run the suite as
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## File structure

```text
day-074-mocking-and-testing-boundaries/
├── README.md                        ← you are here
├── metadata.yml                     ← machine-readable lab metadata
├── examples/
│   ├── sensor_service.py            ← the "world": slow and flaky on purpose, no sockets
│   ├── sensor_client.py             ← the same boundary as an object (used for spec=/autospec)
│   ├── report_v1.py                 ← BEFORE: clock, network and filesystem hard-coded
│   ├── report_v2.py                 ← AFTER: a pure core, boundaries as parameters
│   ├── adapters.py                  ← the adapter ring: system clock, live client, file writer
│   ├── fakes.py                     ← the six hand-written doubles, plus a scripted model
│   ├── model_boundary.py            ← a language-model call behind an injected interface
│   ├── typo_under_test.py           ← production code with a real typo in it
│   ├── demo.py                      ← the whole story in one run
│   ├── doubles_demo.py              ← the five kinds of double, demonstrated
│   ├── autospec_demo.py             ← why an un-specced Mock is dangerous
│   ├── test_patch_right_target.py   ← passes
│   ├── test_patch_wrong_target.py   ← FAILS on purpose
│   ├── test_autospec_naive.py       ← passes on purpose, and is worthless
│   ├── test_autospec_specced.py     ← FAILS on purpose, and is right
│   ├── test_report_v2_fakes.py      ← passes, with no patching anywhere
│   └── test_model_boundary.py       ← passes, without calling a model
├── starter/
│   ├── sensor_service.py            ← provided, identical to the example
│   ├── report_v1.py                 ← provided complete; this is what you test
│   ├── test_report_v1.py            ← YOUR working file (exercises 1-2)
│   ├── report_v2.py                 ← YOUR working file (exercise 3)
│   ├── fakes.py                     ← YOUR working file (exercise 4)
│   ├── test_report_v2.py            ← YOUR working file (exercise 5)
│   └── NOTES.md                     ← YOUR written comparison (exercise 6)
├── tests/
│   └── run_tests.sh                 ← 49 checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt               ← real captured runs of the three demos
│   ├── pytest-runs.txt              ← real captured runs of all six example suites
│   ├── test-run.txt                 ← real captured run of the test suite
│   └── FIELDS.md                    ← required behaviour, and what varies between runs
├── requirements/
│   ├── requirements.txt             ← pytest==9.1.1
│   └── README.md                    ← what each dependency is for, and what is stdlib
├── troubleshooting.md
└── security.md
```

## How to run

From this directory. `pt` below is your pytest: `.venv/bin/pytest` after the
install above.

```bash
# 1. See what a boundary costs, and what removing it buys. One run, six parts.
python3 examples/demo.py

# 2. Meet the five kinds of test double, each in a few real lines.
python3 examples/doubles_demo.py

# 3. Watch an un-specced Mock accept everything, and autospec refuse.
python3 examples/autospec_demo.py

# 4. The suites that pass.
.venv/bin/pytest examples/test_patch_right_target.py examples/test_report_v2_fakes.py examples/test_model_boundary.py -q

# 5. The suite that passes and should not. Read it — it is four lines.
.venv/bin/pytest examples/test_autospec_naive.py -q

# 6. The two suites that FAIL on purpose. Read the failures; that is the point.
.venv/bin/pytest examples/test_autospec_specced.py -q
.venv/bin/pytest examples/test_patch_wrong_target.py -q

# 7. Prove the refactored core needs no patching, from a directory with no files.
cd "$(mktemp -d)" && PYTHONPATH=$OLDPWD/examples python3 -c "
import datetime
from report_v2 import build_report
from fakes import StubSensorClient, frozen_clock
day = datetime.date(2026, 4, 12)
print(build_report('ALPHA', clock=frozen_clock(day),
                   client=StubSensorClient([12.0, 14.0, 20.0, 22.0] * 6)).render())
" && cd -

# 8. Your task: exercises 1-2 in starter/test_report_v1.py, 3 in
#    starter/report_v2.py, 4 in starter/fakes.py, 5 in
#    starter/test_report_v2.py, 6 in starter/NOTES.md.
.venv/bin/pytest starter -q

# 9. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/demo.py` — the whole lab in one run. Section 1 calls the
  stand-in service twice and times it, so you can see latency and randomness
  rather than read about them. Section 2 runs the same patch test against the
  right target and the wrong one, printing the mean each produced and how long
  it took — the wrong target takes 0.4 s because the real function ran.
  Section 3 builds a report with fakes in a fraction of a millisecond. Section
  4 proves a retry schedule without anything waiting. Section 5 shows the model
  boundary. Section 6 prints the imports of both versions side by side.
- `python3 examples/doubles_demo.py` — dummy, stub, spy, mock and fake, each
  exercised against the same `build_report`, then a short demonstration that a
  single `Mock()` can play all five roles depending on which of its features
  you use. That ambiguity is why the five names are worth keeping.
- `python3 examples/autospec_demo.py` — the most important twenty lines in the
  lab. A bare `Mock()` invents `fetch_radings` and accepts a call with a
  keyword the real method has never heard of. `Mock(spec=SensorClient)` refuses
  the invented attribute but still accepts the bad signature.
  `create_autospec(SensorClient, instance=True)` refuses both. Then the same
  buggy function is called three ways: with a bare Mock it returns `20.0`, with
  autospec it raises `AttributeError`, and with the real `SensorClient` it
  raises the same `AttributeError` — which is what production would have done.
- The pytest commands — six suites. Four pass; two fail on purpose. The two
  failures are not defects in the lab, and the test suite asserts that they
  happen. A suite that could not tell `test_autospec_naive.py` from
  `test_autospec_specced.py` would be proving nothing.
- The `mktemp -d` one-liner — imports the refactored core from a directory
  containing no files at all and prints a complete report. Nothing is patched,
  nothing is stubbed by a library, and no fixture exists. This is Day 70's
  proof, applied to testing.
- `bash tests/run_tests.sh` — 49 checks while the starter is unfinished,
  39 once you complete every exercise. Exits 0 only if all of them pass.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) and
[`expected-output/pytest-runs.txt`](expected-output/pytest-runs.txt) — real
captured sessions. The heart of it:

```text
$ python3 examples/demo.py

2. report_v1 under patch — target matters
=========================================
  report_v1.py says: from sensor_service import fetch_readings
  so the name lives in report_v1's namespace, not sensor_service's.
  patch('report_v1.fetch_readings')
      -> mean     17.0   [0.00s — the stub was used]
  patch('sensor_service.fetch_readings')
      -> mean     8.6   [0.40s — the REAL service was used]
  the second target is not an error. It patches something nobody looks at.
```

```text
$ python3 examples/autospec_demo.py

The bug this hides, in three lines
==================================
  typo_under_test.latest_average calls client.fetch_radings(...)
  with a bare Mock (this is what the green test does)
      -> 20.0
  with create_autospec (this is what a good test does)
      -> AttributeError: Mock object has no attribute 'fetch_radings'
  with the REAL SensorClient (this is production)
      -> AttributeError: 'SensorClient' object has no attribute 'fetch_radings'
```

Only two things vary between runs, and both are the lesson rather than a
defect: the readings and timings in section 1 of `demo.py` (that section calls
the real stand-in service on purpose) and the object ids inside Mock reprs.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the exact
required behaviour of every double, the core, and the model boundary.

## Validation steps

1. `python3 examples/demo.py` exits 0, and section 2 shows the right target at
   about `0.00s` and the wrong target at about `0.40s`.
2. In `examples/autospec_demo.py`, the bare Mock returns `20.0` for a function
   whose call is misspelled, while the real `SensorClient` raises
   `AttributeError`. Those two lines are the whole argument for `autospec`.
3. `pytest examples/test_autospec_naive.py -q` reports `1 passed`, and
   `pytest examples/test_autospec_specced.py -q` reports `2 failed`. Both are
   correct.
4. `pytest examples/test_patch_wrong_target.py -q` reports `1 failed` in about
   0.4 s. Change its one patch target to `report_v1.fetch_readings`, rerun, and
   watch it pass in about 0.01 s. Change it back.
5. `pytest examples/test_report_v2_fakes.py -q` reports `10 passed` in under
   0.05 s and contains no `patch` call at all — check with
   `grep -cE 'patch\(' examples/test_report_v2_fakes.py`, which prints `0`.
   (Plain `grep -c patch` prints `2`: the word appears twice in the file's
   opening comment, which is a small lesson in why the test suite parses these
   files instead of searching their text.)
6. The `mktemp -d` one-liner in step 7 of "How to run" prints a five-line
   report from a directory containing no files.
7. `grep -nE '^\s*(import|from) (pathlib|time|random|os|json)' examples/report_v2.py`
   finds nothing. The suite checks this too, by parsing the file rather than
   grepping it.
8. In `examples/test_report_v2_fakes.py`, the backoff test asserts
   `waits.waits == [0.5, 1.0]` and the whole file still runs in hundredths of a
   second — nothing waited.
9. Every exercise in `starter/` is complete, `starter/NOTES.md` is filled in
   with sentences rather than single words, and
   `.venv/bin/pytest starter -q` passes.
10. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished:
`49 checks, 0 failure(s).` Once you complete every exercise, ten structural
checks are replaced by four behavioural ones and the line becomes
`39 checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in continuous integration. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

Four of the checks assert that a test suite **fails**, which is unusual enough
to be worth reading the runner for. They are the autospec pair, the
patch-target pair, and one more that matters just as much: the suite copies the
examples to a temporary directory, breaks exactly one line of `report_v2.py`
with `sed` so the mean is always zero, and asserts that
`test_report_v2_fakes.py` then fails. A test suite that stays green against a
broken implementation is not a test suite.

## Cleanup

The lab writes nothing into your working directory. Every file it creates goes
into a directory made with `mktemp -d` or pytest's `tmp_path`, and is removed
when that check or test finishes. The runner passes `-p no:cacheprovider`, so
pytest leaves no cache directory behind either.

```bash
rm -rf .venv                 # remove the virtual environment when you are done
git checkout -- starter/     # optional: reset your work
```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list. The five you
are most likely to meet: a patch that appears to do nothing (you aimed it at
where the function was defined); `AttributeError: <module> does not have the
attribute` from `patch` (a typo in the target string, which is the good case —
`patch` checks the attribute exists); a test that passes for a minute and then
fails (something real is still being called); `ModuleNotFoundError: No module
named 'report_v2'` (pytest was pointed at a file outside the directory holding
the modules); and `NotImplementedError` from the starter, which is expected
until you finish that exercise.

## Security notes

See [security.md](security.md). Short version: nothing here opens a socket —
`sensor_service.py` simulates latency and failure with `time.sleep` and
`random`, and contacts nothing. Patching is a run-time modification of another
module's namespace and is undone on exit; a patch that escapes its block
corrupts every test after it, which is why `with` and the decorator form are
safer than manual `start()`/`stop()`. And the day's real security point: a test
suite full of mocks can be green while the system is broken, so mock-heavy
suites are a poor place to put your confidence about anything that matters.

## Extension exercises

1. **Make the naive test fail honestly.** Add `spec=SensorClient` to the bare
   `Mock()` in `examples/test_autospec_naive.py` and rerun. Then change it to
   `create_autospec` and add a call with a keyword argument the real method
   does not take. Note which of the two levels caught which mistake.
2. **Change the import style and watch the target move.** In
   `examples/report_v1.py`, replace `from sensor_service import fetch_readings`
   with `import sensor_service`, and change the call to
   `sensor_service.fetch_readings(...)`. Now run both patch tests again. They
   swap places: the "wrong" target becomes the right one. Write down, in one
   sentence, the rule that explains both results. Then put the file back.
3. **Add a boundary and remove it again.** Give the report a `generated_by`
   field filled from an environment variable. First test it with
   `monkeypatch.setenv`, then refactor so the value is a parameter and test it
   with neither. Compare the two tests line for line.
4. **Write a contract test.** `LiveSensorClient` in `adapters.py` and
   `FakeSensorClient` in `fakes.py` both claim to implement the same interface.
   Write one parametrized test that runs the same assertions against both, so
   the fake cannot drift away from the real thing unnoticed. Mark the live case
   so it is skipped by default — the point is that it *can* be run, not that it
   runs on every commit.
5. **Break the boundary on purpose.** Add `import time` and `time.sleep(0.1)`
   to `examples/report_v2.py`, then run `bash tests/run_tests.sh`. Watch the
   purity check fail, and note that it fails by parsing the file rather than by
   searching its text. Remove it again.
6. **Replace a mock with a fake.** Rewrite one test in
   `examples/test_patch_right_target.py` so it uses `create_autospec` and
   `assert_called_once_with` instead of a plain patch, then rewrite it a third
   time against `report_v2` with `FakeSensorClient`. Three versions of one
   test; decide which you would want to read in two years.

## Navigation

- **Previous day:** Day 73 — Test-Driven Development
  (`labs/sections/programming-with-python/day-073-test-driven-development/`).
- **Next day:** Day 75 — Static Typing with mypy
  (`labs/sections/programming-with-python/day-075-static-typing-with-mypy/`).
- **Week 11 project:** the Tested Utility Library
  (`labs/sections/programming-with-python/projects/week-11/`), which expects
  the discipline practised here: a core with its boundaries as parameters, and
  a suite that is fast because nothing in it reaches the world.
