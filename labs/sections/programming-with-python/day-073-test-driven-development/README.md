# Day 073 lab — The bowling kata, one failing test at a time

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Test-Driven Development
- **Day number:** 73 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-073-test-driven-development
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-073-test-driven-development` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 73 is about the *order* in which you write things, and there is only one
way to learn it: perform the loop yourself, eight times, and keep the
evidence.

This lab hands you an empty module. `starter/bowling.py` contains a docstring
and nothing else — no function signature, no stub, nothing to fill in. That is
deliberate. In test-driven development the implementation does not exist until
a failing test asks for it, so the file you are meant to grow starts genuinely
empty rather than pretending to.

`starter/cycles.md` is the kata sheet. It gives you eight cycles in order,
each with the exact test function to add, a blank RED block, a blank GREEN
block, and one question to answer in a sentence. Your job for each cycle is
the whole discipline in five moves: add **one** test, run the suite, watch it
fail, paste the failure, write the least code that passes, run again, paste
the pass.

Cycle 8 is the point of the day. Two tests — a perfect game and a real
133-point scorecard — are added together and both pass on the first run. That
is not a victory; it is an unanswered question, because a test that has never
been seen to fail has never been shown to be connected to anything. You then
break the implementation on purpose in a throwaway copy and watch both tests
go red, which is the only thing that makes them worth keeping.

The test runner takes the same view of your work that the lesson takes of
yours: it does not trust a stored result. It re-runs the reference suite from
source, breaks the reference implementation four different ways to prove the
suite can actually fail, and reads all seventeen recorded captures in
`examples/cycles/` to check that their pass counts chain the way a genuine
red-green sequence would.

## Learning objectives

- Perform eight red-green-refactor cycles end to end, adding exactly one test
  per cycle and never two.
- Read a pytest failure well enough to say whether it failed for the reason
  you predicted, and distinguish that from a boring failure such as a typo or
  a wrong import.
- Recognise five distinct kinds of red — a missing function, a wrong number, a
  missing exception class, a refusal that did not happen, and a crash that
  should have been a refusal — and say what each one tells you.
- Use `fake it till you make it` at cycle 1 and triangulation at cycle 2 as
  deliberate techniques, and watch the second remove the first.
- Perform a refactor and prove it was one, by showing the identical passing
  count on either side of it.
- Specify a refusal from the caller's side: decide in a test that bad input
  raises a module-specific `ScoringError`, before any implementation exists to
  influence the decision.
- Test a test that has never been red, by mutating the code it covers and
  confirming it goes red.
- Judge your own recorded history against the same standard the runner applies
  to the reference: one failure per red, the earlier cycles still green, and a
  refactor that moves no count.

## Prerequisites

- The Day 73 lesson (read it first — it walks the same kata with the real
  captures, and this lab is where you reproduce them yourself).
- Day 72: fixtures, parametrization, and designing a test with one clear
  reason to fail.
- Day 71: pytest discovery and naming, plain `assert`, `pytest.raises`, and
  the always-passing-test anti-pattern this lab is the answer to.
- Day 66: raising exceptions on purpose and defining your own exception class.
- Day 43: creating a virtual environment with `python3 -m venv` and installing
  a pinned dependency into it.
- A text editor and a terminal. Nothing beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3, pytest and
  bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3` and `.venv\Scripts\pytest.exe` for `.venv/bin/pytest`. The test
  runner is a bash script, so it needs WSL, Git Bash, or another bash. Nothing
  about the kata itself is platform-specific.

## Hardware requirements

Any computer that runs Python 3. The whole lab is two small Python files, a
kata sheet, and seventeen short text captures; the reference suite finishes in
about a hundredth of a second. No special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `pytest` — one pinned third-party package, `pytest==9.1.1`. See
  [`requirements/README.md`](requirements/README.md).
- `bash`, `sed` and `cmp` for the test runner (preinstalled on macOS and
  Linux).

The implementation under test imports nothing at all. That is not an accident:
a pure function over a list of integers is the easiest thing in the world to
drive test-first, which is exactly why this kata was chosen to teach the
technique. Day 74 takes on the harder case, where the code you are testing
talks to something outside itself.

## Free and open-source options

Everything here is free and open source: Python, bash, and pytest (MIT
licence). No account, API key, or purchase is needed at any point. The
lesson's Alternatives section names `pytest-bdd`, `behave`, Hypothesis and
mypy as neighbouring approaches — all of them free and open source too, all
installable with `pip`, and none of them required to complete this lab.

## Installation

One third-party package, installed once into a lab-local virtual environment:

```bash
cd labs/sections/programming-with-python/day-073-test-driven-development
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

That `pip install` is the only moment this lab touches the network.
Afterwards the kata, the suite and the test runner all run fully offline.
`.venv/` is ignored by version control; never commit it.

If you would rather not create a lab-local environment, point the runner at a
pytest you already have:
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## File structure

```text
day-073-test-driven-development/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── cycles.md                   ← THE KATA SHEET: eight cycles, blank RED and GREEN blocks
│   ├── bowling.py                  ← YOUR implementation — deliberately empty
│   └── test_bowling.py             ← YOUR suite — imports only, one test per cycle
├── examples/
│   ├── bowling.py                  ← reference implementation (do not read until you have finished)
│   ├── test_bowling.py             ← reference suite: the nine tests, in cycle order
│   └── cycles/
│       ├── README.md               ← what each cycle added, and the honest limits of a recorded history
│       ├── cycle-1-red.txt … cycle-7-green.txt   ← fourteen real captures, one per red and green
│       ├── cycle-4-refactor.txt    ← the refactor that moved no count
│       ├── cycle-8-passed-immediately.txt        ← nine passed, no red at all
│       └── cycle-8-mutant.txt      ← the same nine tests against a deliberately broken copy
├── tests/
│   └── run_tests.sh                ← 40 checks; exits 0 only if all pass
├── expected-output/
│   ├── suite-run.txt               ← real captured run of the reference suite, plus its collected ids
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour of your score(), and of your recorded history
├── requirements/
│   ├── requirements.txt            ← pytest==9.1.1
│   └── README.md                   ← what the dependency is for, and the one-time install
├── troubleshooting.md
└── security.md
```

## How to run

From this directory, after the install above:

```bash
# 1. Read the kata sheet. This is your only specification.
cat starter/cycles.md

# 2. Cycle 1: add ONE test to starter/test_bowling.py, then run this BEFORE
#    writing any implementation. It must fail. Paste the failure into cycles.md.
.venv/bin/pytest starter/test_bowling.py

# 3. Write the least code in starter/bowling.py that passes, and run again.
#    Paste that run into the GREEN block. Repeat for cycles 2 through 8.
.venv/bin/pytest starter/test_bowling.py

# 4. Only after you have finished all eight cycles: the reference suite.
.venv/bin/pytest examples/test_bowling.py
.venv/bin/pytest examples/test_bowling.py -q --collect-only

# 5. The recorded history of someone else performing the same kata.
cat examples/cycles/cycle-1-red.txt
cat examples/cycles/cycle-7-red.txt
cat examples/cycles/README.md

# 6. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `cat starter/cycles.md` — prints the kata sheet: the rules of bowling you
  need and no more, how to run a cycle, and the eight cycles in order with the
  exact test function for each and blank blocks for your captures.
- `.venv/bin/pytest starter/test_bowling.py` — runs *your* suite against *your*
  module. Naming the file matters: a bare `.venv/bin/pytest` would try to
  collect `starter/test_bowling.py` and `examples/test_bowling.py`, two
  same-named modules with no package around them, and refuse with an
  `import file mismatch`.
- `.venv/bin/pytest examples/test_bowling.py` — runs the reference suite: nine
  tests, all passing, in about 0.01 seconds. This is what your finished work
  should be equivalent to.
- `.venv/bin/pytest examples/test_bowling.py -q --collect-only` — lists the
  nine test ids without running them, so you can see the cycle order preserved
  in the file: gutter game, all ones, strike, spare, then the three refusals,
  then the perfect game and the real game.
- `cat examples/cycles/cycle-1-red.txt` — the first red of the whole kata:
  `AttributeError: module 'bowling' has no attribute 'score'`. Compare it with
  your own cycle 1 red; they should say the same thing.
- `cat examples/cycles/cycle-7-red.txt` — the most instructive capture in the
  set. The short game does not fail politely, it crashes with
  `IndexError: list index out of range` from inside the loop, and pytest
  prints the whole function with an arrow at the offending line.
- `cat examples/cycles/README.md` — what each cycle actually added, plus an
  honest section on why a recorded history is easy to fake and what the runner
  can and cannot prove about one.
- `bash tests/run_tests.sh` — 40 checks while the starter is untouched, 41
  once you have completed the kata. Exits 0 only if all of them pass.

## Expected output

The reference suite, captured on the authoring machine — the full session is
in [`expected-output/suite-run.txt`](expected-output/suite-run.txt):

```text
$ .venv/bin/pytest examples/test_bowling.py
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
rootdir: <repo>/labs/sections/programming-with-python/day-073-test-driven-development/examples
plugins: cov-7.1.0, anyio-4.14.2
collected 9 items

test_bowling.py .........                                                [100%]

============================== 9 passed in 0.01s ===============================
```

Your own cycle 1, before any implementation exists, should read like
[`examples/cycles/cycle-1-red.txt`](examples/cycles/cycle-1-red.txt):

```text
    def test_a_gutter_game_scores_zero():
>       assert bowling.score([0] * 20) == 0
               ^^^^^^^^^^^^^
E       AttributeError: module 'bowling' has no attribute 'score'

test_bowling.py:9: AttributeError
=========================== short test summary info ============================
FAILED test_bowling.py::test_a_gutter_game_scores_zero - AttributeError: modu...
============================== 1 failed in 0.01s ===============================
```

Nothing in this lab reads the clock, the network, or a random number, so every
count above is identical on any machine with Python 3 and pytest 9. Only the
timings, the `rootdir` line, the plugin list and the memory address printed in
an assertion diff vary.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly what
your finished `score(rolls)` must do for all eleven inputs the reference suite
uses, and exactly which summary line each of your eight cycles must show.

## Validation steps

1. `.venv/bin/pytest examples/test_bowling.py` reports `9 passed` and exits 0.
2. Every cycle in `starter/cycles.md` has a RED block containing a real
   failure and a GREEN block containing a real pass.
3. Each RED block shows exactly **one** failing test. Two means you wrote two
   tests in one cycle, which is the one rule of this lab.
4. Each RED block from cycle 2 onward shows the earlier cycles still green —
   cycle 5's red must read `1 failed, 4 passed`.
5. Each GREEN block for cycle N reads exactly `N passed`.
6. Cycle 4 has three blocks: red, green, and a refactor run showing the same
   `4 passed` as its green. A refactor that moves the count is not a refactor.
7. Cycle 8 has a run showing `9 passed` **and** a run against a deliberately
   broken copy in which both new tests fail.
8. You answered all four questions at the bottom of `cycles.md` in your own
   words, before opening `examples/cycles/README.md`.
9. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is untouched:

```text
40 checks, 0 failure(s).
```

A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt). The 40 checks
fall into four groups, and the third belongs to this day and no other:

1. **The reference suite passes** — pytest exits 0 with nine tests, and six
   named test ids are actually collected.
2. **The suite has teeth** — the reference implementation is copied to a
   directory made with `mktemp -d`, broken by a single `sed` substitution, and
   pytest must exit non-zero. Four different mutations are tried: an
   off-by-one in the total, removing the frame-size refusal, removing the
   per-roll refusal, and disabling the strike branch. A test suite that cannot
   fail is not a test suite.
3. **The recorded history is genuine** — every RED capture in
   `examples/cycles/` must really report one failure, every GREEN capture must
   really report the exact number of passes that cycle should have reached,
   and the counts must chain. Cycle 5's red can only say `4 passed` if cycles
   1 to 4 really were written first and really ended green.
4. **The starter is in a sensible state** — both starter files are valid
   Python and the kata sheet still dictates all eight cycles.

Once `starter/bowling.py` defines `score`, the runner stops checking that the
module is empty and starts grading it: it runs *your* module against the
*reference* suite, so a weaker set of tests of your own cannot let a weaker
implementation through, and separately runs your own suite. That gives
`41 checks, 0 failure(s).`

## Cleanup

The lab writes nothing into its own directory. To remove the environment and
Python's bytecode cache:

```bash
rm -rf .venv
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
```

To reset your work, restore the starter from git: `git checkout -- starter/`.
The test runner makes its own temporary directories with `mktemp -d` and
removes each one as that check finishes, and sets `PYTHONDONTWRITEBYTECODE=1`
so its own runs leave no cache behind.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `pytest not
found` and the three places the runner looks for it; the `no tests ran` with
exit code 5 that is expected before cycle 1; `ModuleNotFoundError: No module
named 'bowling'`; the `import file mismatch` you get from running bare
`pytest`; the `AttributeError` that is the correct first red; `Failed: DID NOT
RAISE ScoringError` and what it means when it appears *after* you wrote the
check; the `IndexError` that is cycle 7's whole point; why `from bowling
import score, ScoringError` turns a clean `1 failed, 4 passed` into a single
collection error; what to do when your RED block shows two failures or your
GREEN block shows too few passes; and the macOS `sed -i` difference.

## Security notes

See [security.md](security.md). Short version: the only network moment is the
pinned `pip install`, which lands in a lab-local `.venv/` you can delete; a
test suite is executable code you are inviting in, so read an unfamiliar one
before you run it; writing the refusal first is a security practice, because
most missing input validation is missing because nobody ever wrote the
sentence "this input must be refused" anywhere; `assert` is stripped by
Python's `-O` flag, which is why a production refusal belongs in an explicit
`raise`; and the most common way a vulnerability ships is a red test that was
adjusted until it passed.

## Extension exercises

1. **Find a mutation the suite misses.** The runner tries four mutations and
   the suite catches all four. Find a fifth that changes behaviour and leaves
   all nine tests green — a comparison operator, a boundary constant, a `+ 1`.
   One exists. Then write the test that kills it, watch it go red against the
   mutant and green against the original, and you will have added a genuinely
   new specification rather than a tenth restatement of an old one.
2. **Do the kata again, from scratch, in twenty minutes.** Delete your
   `starter/` work, restore it with `git checkout -- starter/`, and repeat.
   The second performance is where the rhythm stops being a procedure you are
   following and starts being how you work. Note which cycle you were tempted
   to skip; that is the one to watch.
3. **Drive the tenth-frame rules properly.** The reference treats bonus rolls
   with a `bonus_rolls` counter. Write a new failing test for a tenth-frame
   spare followed by a strike, work the arithmetic by hand first, and see
   whether the existing implementation already satisfies it. If it does, you
   have found an unspecified behaviour that happens to be right — which is
   worth exactly as much as cycle 8's two immediate greens until you mutate
   the code and watch your new test fail.
4. **Add a property.** Install Hypothesis into your `.venv` and write one
   property the nine examples do not state: a game with no strike and no spare
   scores exactly the sum of its rolls. Generating only frames that total
   under ten is the interesting part of that exercise.
5. **Break the record on purpose.** Edit one capture in `examples/cycles/` so
   its pass count no longer chains — change cycle 5's red to say `3 passed` —
   and run the suite. Watch which check catches it, then restore the file with
   `git checkout -- examples/cycles/`. Knowing exactly which check catches a
   forged history is worth more than being told the record is verified.

## Navigation

- **Previous day:** Day 72 — Fixtures, Parametrization, and Test Design
  (`labs/sections/programming-with-python/day-072-fixtures-parametrization-and-test-design/`).
- **Next day:** Day 74 — Mocking and Testing Boundaries
  (`labs/sections/programming-with-python/day-074-mocking-and-testing-boundaries/`),
  which takes on the case this lab deliberately avoided: code that talks to
  something outside itself.
- **Week 11 project:** the Tested Utility Library
  (`labs/sections/programming-with-python/projects/week-11/`), where the loop
  practised here is applied to a module you will keep.
