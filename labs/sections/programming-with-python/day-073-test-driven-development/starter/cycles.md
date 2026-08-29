# The kata sheet — score a game of ten-pin bowling, one cycle at a time

You are writing `score(rolls)`: given the pins knocked down by every roll of a
completed ten-frame game, in order, return the total score. Nothing else.

**The rules of bowling you need, and no more.** A game is ten frames. In each
frame you get two rolls to knock down ten pins. Knock all ten down with the
first roll and that is a **strike**: the frame scores ten plus your next two
rolls, and you do not roll again in that frame. Knock all ten down across both
rolls and that is a **spare**: the frame scores ten plus your next one roll.
Otherwise the frame scores the pins you knocked down. If the tenth frame is a
strike or a spare you roll the bonus balls at the end of the list, and they
count only as bonus — they are not an eleventh frame.

**The one rule of this lab.** One test per cycle. Run it. Watch it fail. Read
the failure. Only then write code, and only enough code to make it pass.

---

## How to run a cycle

From the lab directory (the one containing `starter/` and `examples/`):

```bash
.venv/bin/pytest starter/test_bowling.py
```

Every cycle below has three parts.

- **The test** — the one test function to add to `starter/test_bowling.py`.
  Add it at the bottom. Never add two at once.
- **RED** — run the suite before touching `bowling.py`, and paste the output
  into the RED block. Then answer the question under it in one sentence.
- **GREEN** — write the least code that passes, run again, paste that output
  into the GREEN block.

Your GREEN block for cycle N must say `N passed`. If it says anything else you
have either skipped a cycle or written more than one test.

---

## Cycle 1 — a gutter game scores zero

Twenty rolls, no pins.

```python
def test_a_gutter_game_scores_zero():
    assert bowling.score([0] * 20) == 0
```

RED — run it now, before writing any code at all.

```text

```

Which line of the failure tells you the test reached your module and found
nothing there?

GREEN — the least code. Yes, `return 0` is allowed here; it is the technique
called **fake it till you make it**, and cycle 2 is what removes the fake.

```text

```

## Cycle 2 — a game of all ones scores twenty

Twenty rolls, one pin each.

```python
def test_a_game_of_all_ones_scores_twenty():
    assert bowling.score([1] * 20) == 20
```

RED — the fake from cycle 1 dies here. That is the whole point of a second
example: **triangulation**, two data points that no constant can satisfy.

```text

```

GREEN — now the constant has to become an expression. Resist writing frames:
`sum(rolls)` passes both tests and no test yet asks for more.

```text

```

## Cycle 3 — a strike adds the next two rolls

A strike in the first frame, then a 3 and a 4, then nothing.
Work the arithmetic by hand before you run anything: frame 1 scores
10 + 3 + 4 = 17, frame 2 scores 3 + 4 = 7, frames 3 to 10 score 0.
Total 24. Note that the 3 and the 4 are counted twice, on purpose.

```python
def test_a_strike_adds_the_next_two_rolls():
    assert bowling.score([10, 3, 4] + [0] * 16) == 24
```

RED — `sum` returns 17. The failure message shows you both numbers.

```text

```

GREEN — this is the cycle where the design has to change: you can no longer
add rolls, you must walk frames. Introduce a roll index and a ten-frame loop,
with one branch for a strike. Do not write the spare branch yet; no test asks
for it.

```text

```

## Cycle 4 — a spare adds the next roll

Five and five, then a 3.
Frame 1 scores 10 + 3 = 13, frame 2 scores 3 + 0 = 3, the rest score 0.
Total 16.

```python
def test_a_spare_adds_the_next_roll():
    assert bowling.score([5, 5, 3] + [0] * 17) == 16
```

RED — your frame walker treats 5 and 5 as an ordinary open frame worth 10, so
it reports 13.

```text

```

GREEN — add the spare branch between the strike branch and the open frame.

```text

```

REFACTOR — the safety net is now four tests wide, so use it. Pull the two
conditions out into `_is_strike(rolls, roll)` and `_is_spare(rolls, roll)`,
change nothing about the behaviour, and run again. A refactor that changes a
single character of output is not a refactor; it is an untested edit.

```text

```

## Cycle 5 — a roll outside zero to ten is refused

Bowling has ten pins. Eleven is not a score, it is bad data, and a scorer that
quietly totals bad data is worse than one that stops. Refuse it with a
`ScoringError` your own module defines.

```python
def test_a_roll_outside_zero_to_ten_is_refused():
    with pytest.raises(bowling.ScoringError):
        bowling.score([11] + [0] * 19)
    with pytest.raises(bowling.ScoringError):
        bowling.score([-1] + [0] * 19)
```

RED — read this failure especially carefully. It is an `AttributeError`, not a
scoring mistake, because `bowling.ScoringError` does not exist yet. That is
still the right reason to fail: the test is asking for a name the module has
not got.

```text

```

GREEN — define `class ScoringError(Exception)` and check every roll before
scoring anything.

```text

```

## Cycle 6 — a frame of more than ten pins is refused

Seven pins then five pins is twelve pins in one frame, from ten pins on the
deck. Impossible.

```python
def test_a_frame_of_more_than_ten_pins_is_refused():
    with pytest.raises(bowling.ScoringError):
        bowling.score([7, 5] + [0] * 18)
```

RED — this one fails with `Failed: DID NOT RAISE ScoringError`, which is the
message you get when the code sails past something it should have refused.

```text

```

GREEN — check the pair inside the open-frame branch. Careful: the check has to
sit where it can see both rolls of the frame, and it must not fire on the
bonus rolls after a tenth-frame strike.

```text

```

## Cycle 7 — a game with the wrong number of rolls is refused

Nineteen gutter balls is not a game; neither is twenty-one.

```python
def test_a_game_with_the_wrong_number_of_rolls_is_refused():
    with pytest.raises(bowling.ScoringError):
        bowling.score([0] * 19)
    with pytest.raises(bowling.ScoringError):
        bowling.score([0] * 21)
```

RED — the short game does not fail politely, it explodes with an `IndexError`
from deep inside your loop. An unhandled `IndexError` is a bug leaking through
your interface, and this test is what turns it into a stated refusal.

```text

```

GREEN — this is the largest cycle, and the one worth thinking about before
typing. You need to know, at the end of frame ten, how many bonus rolls the
game is entitled to: two after a strike, one after a spare, none otherwise.
Anything else left over is an extra roll. Anything missing is a short game.

```text

```

## Cycle 8 — the two tests that pass immediately

Now add both of these at once, on purpose, and run.

```python
def test_a_perfect_game_scores_three_hundred():
    assert bowling.score([10] * 12) == 300


def test_a_real_game_scores_133():
    rolls = [1, 4, 4, 5, 6, 4, 5, 5, 10, 0, 1, 7, 3, 6, 4, 10, 2, 8, 6]
    assert bowling.score(rolls) == 133
```

They pass on the first run. Nine passed, nothing red.

```text

```

That is not a victory, it is an unanswered question: **a test that has never
been seen to fail has never been shown to be connected to anything.** So make
it fail on purpose. Copy `bowling.py` somewhere temporary, replace
`if _is_strike(rolls, roll):` with `if False:`, run the suite against the
broken copy, and confirm both new tests go red.

```text

```

Put the good file back. You have now done, by hand, exactly what the test
runner in `tests/run_tests.sh` does automatically — and what you must do every
single time you write a test after the code it tests.

---

## After the kata — write down what you learned

Answer these in your own words, in this file, before you look at
`examples/cycles/README.md`.

1. Which cycle changed the *shape* of your implementation rather than adding to
   it, and what did the test that forced it look like?

```text

```

2. In cycle 2, was `sum(rolls)` the right amount of code, or too little? Give
   the argument for the other side too.

```text

```

3. Cycle 5 and cycle 7 both failed for reasons that were not scoring mistakes
   (a missing name, a leaked `IndexError`). Explain why each was nonetheless
   the right reason to fail.

```text

```

4. Name one thing about this kata that test-first made harder rather than
   easier.

```text

```
