# Your brief — Which Question Are You Asking?

Day 99 taught you to measure how far apart two vectors are. Today you find out
that "how far apart" is usually the wrong question about text, write the
measure that asks the right one, and prove three things about it that most
people who use it every day have never checked.

There are two files to edit and one command to run.

## The command

From the **lab directory** — one level up from here:

```bash
.venv/bin/pytest starter -q
```

Anything you have not written yet is **skipped**, not failed. On an untouched
checkout you should see `1 passed, 51 skipped`. That is your running score:
every exercise you finish turns a skip into a pass, and a wrong answer fails
loudly with both numbers printed.

## The files

| File | What you do in it |
| --- | --- |
| `similarity.py` | Write seven functions. Pure Python; `import math` is the only import allowed. |
| `answers.py` | Replace 24 `None` values with predictions you make **before** running anything. |

## Exercise 1 — the toolkit (7 functions)

| # | Function | One-line summary |
| --- | --- | --- |
| 1.1 | `dot` | Multiply component by component, then add. |
| 1.2 | `l2_norm` | `sqrt(dot(a, a))` — a vector's length is the square root of it dotted with itself. |
| 1.3 | `normalise` | Divide by the length. Refuse the zero vector. |
| 1.4 | `euclidean_distance` | The length of the difference. Day 99's measure. |
| 1.5 | `cosine_similarity` | `dot(a, b) / (|a| * |b|)`, clamped to -1..1, refusing the zero vector. |
| 1.6 | `cosine_distance` | `1 - cosine_similarity(a, b)`. |
| 1.7 | `rank_by_cosine` | Score every item, sort best first, break ties by label. |

Three of them have a trap in them, and each trap has its own test:

- **1.3 and 1.5 must refuse the zero vector** with `ValueError`. It has no
  direction, so there is no angle to it. Returning `NaN` is the tempting
  shortcut; a `NaN` sorts unpredictably and poisons every average downstream.
- **1.5 must clamp.** Three of this lab's six articles, compared with
  themselves through the unguarded formula, come out at something other than
  exactly 1.0 — one of them at `1.0000000000000002`, which `math.acos` refuses
  outright. This is measured on the authoring machine, not hypothetical.
- **1.7 must break ties deterministically.** Two articles score exactly 0.0
  against the cooking query. A ranking that orders them differently between
  runs makes a test suite that fails at random.

## Exercises 2 to 6 — predict, then check

Twenty-four predictions in `answers.py`, grouped by theme:

| Exercise | Theme | What you are predicting |
| --- | --- | --- |
| 2 | The length confound | Two distances, one cosine, and the general fact behind them |
| 3 | The sign | Three dot products, one angle, and which articles are orthogonal |
| 4 | Not a metric | Two cosine distances, and whether the triangle inequality survives |
| 5 | The unit sphere | The identity `sqrt(2 - 2cos)`, two distances, two ranking questions |
| 6 | Search and the curse | Four retrieval outcomes and one limit |

Write the predictions **first**. That is not a study tip, it is the design of
the exercise: the entire day is about two measures that feel like they should
agree and do not, and the only way to find out whether your intuition is right
is to commit to an answer while it can still be wrong.

Several tests then check that your predictions and your own implementation
agree with **each other**, so a lucky guess with broken code still fails.

## When you are done

`52 passed`. Then read `examples/similarity.py` and compare — your version and
the reference should agree on behaviour, not on wording. Then run the seven
demonstration scripts in `examples/` in order; they take the same numbers much
further than the tests do.

## Rules

- No `numpy` in `similarity.py`. The whole point is that nothing is done for
  you; NumPy appears only in the tests, as the independent check.
- Never modify an argument. Return new lists.
- Raise `ValueError`, not a bare `assert`, on nonsense input — NumPy raises
  `ValueError` for the same situations, so one `except ValueError` catches your
  code and the library alike.
