# Features That Do Not Cheat — the exercise brief

A feature encodes a hypothesis about what matters. The dangerous ones
quietly encode the answer, and they announce themselves by making your
results look excellent. **A result that looks too good is a bug report.**

Nine exercises. Each one is a measurement: you assert on numbers the code
actually produced, not on numbers you hoped for. Everything is seeded, so
the same numbers come back on every machine.

## Before you start

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest starter -v          # 9 skipped, on an untouched checkout
```

Run `pytest starter` and `pytest examples` as **two separate commands**.
Both directories hold a module called `test_features.py`, and pytest
collects by dotted module name, so a combined invocation aborts.

## What is where

| File | What it holds |
| --- | --- |
| `data.py` | Seven seeded generators, one per experiment. Each docstring says where a leak was planted. |
| `features.py` | Every encoder, split into `fit` and `transform`, plus the leakage audit |
| `models.py` | A logistic regression trained by gradient descent and a nearest-centroid classifier, both in NumPy |
| `experiments.py` | The nine measurements; each returns a dictionary of numbers |
| `conftest.py` | One session-scoped fixture per experiment, so each runs once |
| `test_features.py` | Your nine exercises |

scikit-learn is **not** installed, which is why every model here is
written out. You have not met a model API yet, and you do not need one:
the whole point of the day is that the feature table decides the score
long before the model does.

## The nine exercises

1. **Target leakage, measured.** Score the same task with and without a
   column derived from the outcome. Report both numbers. The leaking one
   is 1.00, which is your bug report.
2. **Fitting before the split.** Two statistics fitted on all the data:
   a scaler and a group-mean imputer. One of them buys almost nothing
   and one buys a lot. Measure both and work out why they differ.
3. **Target encoding.** Replace a city with the mean outcome for that
   city, three ways: over everything, over training rows, and
   out-of-fold. Measure the gap the first one buys.
4. **Temporal leakage.** Split time-ordered rows at random, then by
   time. One number is trustworthy. Report both.
5. **Cyclical encoding.** Hour 23 and hour 0 are one hour apart in the
   world and 23 apart as integers. Prove that sine and cosine fix it,
   with exact distances.
6. **An ordinal code imposes an order.** Six paint colours with no
   order and a deliberately non-monotone return rate. Show that the
   model given a code can only move monotonically with it.
7. **An interaction.** Neither spend nor income separates the classes.
   Their ratio separates them perfectly. Report all three.
8. **Vocabulary fitted on training only.** Choosing which words become
   features by their association with the label is a fitted statistic,
   so it belongs on the training side of the line.
9. **A leakage audit.** Write the check once and run it on any table.
   Then be honest in your own words about what it cannot see.

## How to work

Delete the `pytest.skip(...)` line, write the assertions the docstring
describes, and run `pytest starter -v` again. When an assertion fails,
print the dictionary the fixture handed you and look at the number before
you change the assertion — the measurement is the thing you are learning
from, and moving a band to make a test pass throws it away.
