# Day 144 lab brief — Three Sets, and Why

Everybody knows you hold out a test set. Rather fewer people can say why
there are supposed to be *three* sets rather than two, and almost nobody
has seen the number that justifies the third one.

This lab measures it.

## The claim you are here to measure

> A validation set you select on is a set you have fitted to.

Exercise 1 does it with candidates that have exactly zero skill. Each one
is a coin flip: a fixed vector of random predictions, scored on a 500-row
validation set and a 500-row test set. Pick whichever scores best on
validation, then look at what it scores on test:

| candidates considered | best validation | its test score | optimism |
| --- | --- | --- | --- |
| 1 | 0.4984 | 0.5011 | −0.0028 |
| 10 | 0.5331 | 0.4999 | +0.0332 |
| 100 | 0.5567 | 0.4992 | +0.0575 |
| 1000 | 0.5720 | 0.4992 | +0.0728 |

Read the test column first. **It never moves.** It sits at chance for
every K, because it was never selected on. That is the control, and it is
what makes the validation column mean something.

Now read the validation column. It climbs, steadily, all the way to
0.5720 — on candidates that are coin flips. Try a thousand things and the
best of them will look seven points better than chance, every time,
whether or not any of them is any good.

That is why there are three sets. Not convention. Arithmetic.

## The part that is genuinely satisfying

Exercise 1c checks the optimism against theory. Express it in standard
errors — the standard error of an accuracy on 500 rows is 0.0224 — and
compare it to the expected maximum of K standard normal draws:

| K | measured, in SEs | E max of K normals | sqrt(2 ln K) |
| --- | --- | --- | --- |
| 10 | 1.48 | 1.54 | 2.15 |
| 100 | 2.57 | 2.50 | 3.03 |
| 1000 | 3.26 | 3.24 | 3.72 |

The measurement tracks the simulated expectation closely — and the
familiar closed-form `sqrt(2 ln K)` sits above the truth at every K here.
It is an asymptotic, and it is loose at any K you will actually use. The
lab asserts the inequality rather than a gap size.

## The four ways a split goes wrong

| # | The mistake | What it costs, measured |
| --- | --- | --- |
| 2 | not stratifying a rare class | 21 of 500 random splits had a test half with **no positives at all** |
| 3 | splitting rows when the unit is a person | **+0.5648** — 0.9760 against 0.4112, and all 50 people were in both halves |
| 4 | shuffling data that has a direction in time | +0.0728 on average, and shuffling won in **20 of 20** constructions |
| 5 | reading a trend off one holdout | one holdout swung **0.19** across seeds; 5-fold swung 0.0325 |

Exercise 3 is the one that should alarm you. Fifty people, twenty rows
each, and each person's label is a coin flip — there is nothing
generalisable in that dataset whatsoever. A row-wise random split reports
**97.6 percent accuracy**. A group-aware split reports 0.4112, which is
chance. Fifty-six points, and the mechanism is one line: with twenty rows
each, a random quarter cannot miss anybody, so every test person is
already in training.

## The honesty call in exercise 4

The temporal effect is real: shuffling beat chronology in all twenty
constructions. But its **size varies by a factor of sixteen**, from +0.016
to +0.2557.

The first construction tried while building this lab gave +0.1428.
Reporting that one number would have been the forking-paths problem inside
a lab about not committing it. So exercise 4 splits in two: 4 asserts the
direction, which held every time, and 4b asserts the whole distribution —
mean, standard deviation, minimum and maximum — and the fact that the
chronological score is statistically indistinguishable from the majority
baseline.

Not every split mistake costs the same. Group leakage cost fifty-six
points. Temporal leakage, here, cost seven on average. Both are real; only
one is an emergency.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_splits_lib.py`) and fourteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `splits_lib.py`, `test_splits_lib.py` and `test_splits_claims.py`;
pytest aborts on the module-name collision. Run them separately, always.

## And the rule, made mechanical

Exercise 7 wraps the test set in a `GatedTestSet` that permits exactly one
evaluation and raises `TestSetTouchedTwice` on the second, with a message
saying what the second number actually is: a validation score.

That is not a substitute for discipline. It is the discipline made
mechanical, in the same spirit as Day 143's stage contract — a rule that
lives in code is a rule somebody can check.
