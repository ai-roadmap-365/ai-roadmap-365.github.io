# Expected output — Day 073 lab

These are real captured runs from the authoring machine (macOS 26.5.1, Apple
Silicon, Python 3.14.0, pytest 9.1.1, bash 3.2.57, 2026-07-19). Nothing in this
lab reads the clock, the network, or a random number, so the numbers below are
the same on every machine with Python 3 and pytest 9.

## Files

- `suite-run.txt` — `pytest` on the reference suite, then the same suite with
  `--collect-only -q` so you can see the nine test ids. Absolute paths appear
  as `<repo>`; on your machine that line shows your real repository path.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  untouched: 40 checks, 0 failures, exit 0. Completing the kata turns the last
  starter check into two graded checks, giving 41.
- The seventeen recorded cycle captures live in `../examples/cycles/`, not
  here, because they are teaching material rather than a description of the
  finished state. `../examples/cycles/README.md` indexes them.

## What varies between machines, and what does not

| Line | Varies? | Why |
| --- | --- | --- |
| `platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0` | yes | your platform, Python and pluggy versions; `pytest-9.1.1` is pinned by `requirements/requirements.txt` |
| `rootdir: ...` | yes | pytest reports the directory it started from |
| `plugins: cov-7.1.0, anyio-4.14.2` | yes | whatever plugins your environment has; the lab needs none of them |
| `collected 9 items` | no | the reference suite has exactly nine tests |
| `9 passed in 0.01s` | the time varies | the count does not |
| `<function score at 0x1072...>` in a failure | yes | a memory address, printed by pytest's assertion rewriting; the numbers on either side of `==` do not vary |
| every `assert N == M` pair in the cycle captures | no | they are computed from fixed lists of integers |

## Required behaviour of your `score(rolls)`

Your finished `starter/bowling.py` must satisfy exactly this. The test runner
grades it by running the *reference* suite against your module, so a weaker set
of tests cannot let a weaker implementation through.

| Call | Result | Arithmetic |
| --- | --- | --- |
| `score([0] * 20)` | `0` | ten open frames of nothing |
| `score([1] * 20)` | `20` | ten open frames of two |
| `score([10, 3, 4] + [0] * 16)` | `24` | frame 1 is 10 + 3 + 4 = 17, frame 2 is 3 + 4 = 7 |
| `score([5, 5, 3] + [0] * 17)` | `16` | frame 1 is 10 + 3 = 13, frame 2 is 3 + 0 = 3 |
| `score([10] * 12)` | `300` | ten frames of 10 + 10 + 10 |
| `score([1,4,4,5,6,4,5,5,10,0,1,7,3,6,4,10,2,8,6])` | `133` | 5 + 9 + 15 + 20 + 11 + 1 + 16 + 20 + 20 + 16 |
| `score([11] + [0] * 19)` | raises `ScoringError` | a roll knocks down 0 to 10 pins |
| `score([-1] + [0] * 19)` | raises `ScoringError` | same rule, other end |
| `score([7, 5] + [0] * 18)` | raises `ScoringError` | twelve pins in one frame |
| `score([0] * 19)` | raises `ScoringError` | frame 10 has only one roll |
| `score([0] * 21)` | raises `ScoringError` | one roll after the game ended |

`ScoringError` must be defined in your own module and must be a subclass of
`Exception`. The reference suite refers to it as `bowling.ScoringError`.

## Required shape of your recorded history

The runner reads `examples/cycles/` and checks the reference record, not
yours — it cannot see the blocks you paste into `starter/cycles.md`. Grade
those yourself against the same standard:

| Cycle | RED summary line must read | GREEN summary line must read |
| --- | --- | --- |
| 1 | `1 failed` | `1 passed` |
| 2 | `1 failed, 1 passed` | `2 passed` |
| 3 | `1 failed, 2 passed` | `3 passed` |
| 4 | `1 failed, 3 passed` | `4 passed`, and the refactor run also `4 passed` |
| 5 | `1 failed, 4 passed` | `5 passed` |
| 6 | `1 failed, 5 passed` | `6 passed` |
| 7 | `1 failed, 6 passed` | `7 passed` |
| 8 | (there is no red — that is the lesson) | `9 passed`, then `3 failed, 6 passed` against the broken copy |

If any RED block of yours shows more than one failing test, you wrote two tests
in one cycle. If any RED block shows zero failing tests, you wrote the code
first — which is allowed in life, but not in this kata, and not without then
proving the test can fail.
