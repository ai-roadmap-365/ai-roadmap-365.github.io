# The recorded history of this kata

Every `.txt` file beside this one is unedited output from a real `pytest` run
made while writing `../bowling.py` and `../test_bowling.py` one cycle at a
time. Nothing here was typed by hand or reconstructed afterwards, and the test
runner checks that: `tests/run_tests.sh` reads each file and refuses to pass
unless the RED capture really reports a failure and the GREEN capture really
reports the exact number of passing tests that cycle should have reached.

The runs were made in a scratch directory called `/private/tmp/bowling-kata`,
which is why that path appears on the `rootdir:` line. Your own runs will show
your lab directory there instead. Every other line will match.

| File | What it is | Summary line |
| --- | --- | --- |
| `cycle-1-red.txt` | one test, no implementation at all | `1 failed` |
| `cycle-1-green.txt` | after `return 0` | `1 passed` |
| `cycle-2-red.txt` | the constant meets a second example | `1 failed, 1 passed` |
| `cycle-2-green.txt` | after `return sum(rolls)` | `2 passed` |
| `cycle-3-red.txt` | summing rolls cannot score a strike | `1 failed, 2 passed` |
| `cycle-3-green.txt` | after the frame walk with a strike branch | `3 passed` |
| `cycle-4-red.txt` | the frame walk scores a spare as an open frame | `1 failed, 3 passed` |
| `cycle-4-green.txt` | after the spare branch | `4 passed` |
| `cycle-4-refactor.txt` | after extracting `_is_strike` and `_is_spare` | `4 passed` |
| `cycle-5-red.txt` | the module has no `ScoringError` yet | `1 failed, 4 passed` |
| `cycle-5-green.txt` | after the error class and the per-roll check | `5 passed` |
| `cycle-6-red.txt` | twelve pins in one frame sail through | `1 failed, 5 passed` |
| `cycle-6-green.txt` | after the per-frame check | `6 passed` |
| `cycle-7-red.txt` | a short game leaks an `IndexError` | `1 failed, 6 passed` |
| `cycle-7-green.txt` | after the length and bonus-roll rules | `7 passed` |
| `cycle-8-passed-immediately.txt` | two new tests, both green on the first run | `9 passed` |
| `cycle-8-mutant.txt` | the same nine tests against a deliberately broken copy | `3 failed, 6 passed` |

## What each cycle actually added

**Cycle 1 — a gutter game scores zero.** The red is an `AttributeError`:
`module 'bowling' has no attribute 'score'`. The module existed; the function
did not. The green was `return 0` — a fake, written knowingly, because one
example cannot distinguish a constant from a calculation.

**Cycle 2 — all ones scores twenty.** The red is
`AssertionError: assert 0 == 20`. Two examples now pin the behaviour down
enough that a constant cannot satisfy both. That is triangulation, and the
green is `return sum(rolls)` — still nowhere near a bowling scorer, but
exactly as much code as the two tests demand.

**Cycle 3 — a strike adds the next two rolls.** The red is
`assert 17 == 24`. This is the cycle that changed the *shape* of the code:
adding rolls cannot express "the next two rolls count twice", so the
implementation became a ten-iteration loop over frames with a roll index that
advances by one after a strike and two otherwise. Notice what did not happen:
no spare branch appeared, because nothing yet asked for one.

**Cycle 4 — a spare adds the next roll.** The red is `assert 13 == 16` — the
frame walker scores the 5 and 5 as an ordinary open frame worth ten. The green
inserted one `elif`. Then, with four tests green, `_is_strike` and `_is_spare`
were extracted and the suite re-run unchanged: `cycle-4-refactor.txt` is the
proof that the refactor changed nothing.

**Cycle 5 — a roll outside zero to ten.** The red is another `AttributeError`,
this time for `bowling.ScoringError`. A test may legitimately demand a name
that does not exist yet; that is the test specifying an interface. The green
added the exception class and a `_check_pins` pass over the rolls.

**Cycle 6 — a frame of more than ten pins.** The red is
`Failed: DID NOT RAISE ScoringError`, pytest's way of saying the code sailed
straight past something it should have stopped at. The green put the check in
the open-frame branch, which is the only place that can see both rolls of a
frame.

**Cycle 7 — the wrong number of rolls.** The red is the most interesting one
in the set: the call does not fail politely, it raises `IndexError: list index
out of range` from inside the loop, and pytest prints the whole function with
an arrow at the offending line. An unhandled `IndexError` is a bug escaping
through a public interface. The green replaced it with three stated refusals —
rolls that run out mid-game, a tenth-frame strike or spare with no bonus rolls
behind it, and extra rolls after frame ten — and added the `bonus_rolls`
bookkeeping that makes a perfect game twelve rolls long rather than ten.

**Cycle 8 — the two tests that passed immediately.** A perfect game and a real
133-point game were added together and both passed on the first run. That is
not evidence the tests work; it is evidence of nothing at all until the tests
have been seen to fail. So `if _is_strike(rolls, roll):` was replaced with
`if False:` in a copy, and the suite was run again: three tests went red,
including both new ones. `cycle-8-mutant.txt` is that run. Only after seeing
it were the two tests worth keeping.

## The honest part

Two things in this record are worth being sceptical about, and both are
deliberate.

The first is that a recorded history is easy to fake, and a suite of tests that
were all written after the fact would look identical in the finished
repository. That is precisely why the runner checks the pass counts: cycle 5's
red must show four other tests already passing, which is only true if the
earlier cycles really happened first and really ended green. It is not
proof — nothing short of watching over your shoulder is — but reconstructing
seventeen consistent captures is more work than doing the kata.

The second is that this kata is unusually well-suited to test-first work.
`score` is a pure function over a list of integers with a knowable contract,
which is the easiest possible case. Day 73's lesson is explicit about where
this technique stops paying: exploratory work, code whose shape you genuinely
do not know yet, user interfaces, and anything where writing the assertion is
the hard part.
