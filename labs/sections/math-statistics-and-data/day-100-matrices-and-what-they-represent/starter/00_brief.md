# The brief — The Same Numbers, Three Ways

Work through the five exercises below in order. Everything you write goes into
two files in this directory: `matrix.py` (exercise 1) and `answers.py`
(exercises 2 to 5). Nothing else needs editing.

Run this after every change, from the **lab directory**, one level up:

```bash
.venv/bin/pytest starter -q
```

Anything you have not attempted is **skipped**, not failed, so the summary line
is a running score. On an untouched checkout it reads `1 passed, 32 skipped`.
When it reads `33 passed`, you are finished.

## The data

Three invented potting mixes from an invented garden centre, described by four
ingredients, in litres per bag:

|  | base | bark | grit | compost |
| --- | --- | --- | --- | --- |
| **Seedling** | 2 | 4 | 1 | 3 |
| **Container** | 0 | 5 | 2 | 7 |
| **Alpine** | 6 | 1 | 4 | 2 |

and the ingredient prices, in pence per litre: base 10, bark 2, grit 5,
compost 1.

Twelve numbers, chosen so that every answer in this lab can be worked out on
paper in under a minute. That is the only property that matters here. The
garden centre, the recipes and the prices are all invented.

Three rows and four columns, deliberately: because 3 and 4 are different
numbers, the **shape of an answer tells you which operation produced it**. On a
square matrix it would not, and exercise 4 shows you what that costs.

---

## Exercise 1 — build the matrix yourself (`matrix.py`)

Fill in the six methods marked `EXERCISE` in `matrix.py`:

| Method | What it must do |
| --- | --- |
| `shape` | Return `(rows, columns)` — rows first |
| `__getitem__` | Support `m[i, j]` from 0; `TypeError` for a non-pair, `IndexError` naming the shape for an out-of-range or negative index |
| `transpose` | Swap rows and columns: `(r, c)` becomes `(c, r)` |
| `add` | Elementwise, identical shapes only; `ShapeMismatch` for a size clash, `TypeError` for a plain list |
| `scale` | Multiply every entry by one number |
| `identity` | The `n` by `n` matrix with 1 on the diagonal and 0 elsewhere |

Do not import numpy in that file. The whole value of the exercise is that
nothing is done for you; the tests then check your class against NumPy, which
is the point at which you find out whether you agreed with it.

Ten of the thirty-three tests belong to this exercise.

## Exercise 2 — the three meanings (`answers.py`, section 2)

Six predictions. Read the same twelve numbers as a **table** (which row is
Alpine, which column is grit), then as a **transformation** (apply the matrix
to the price vector and you get the cost of one bag of each mix).

Work the three costs out on paper. Each is four multiplications and three
additions. Then note which length the answer came out as, and which length was
consumed.

## Exercise 3 — views and copies (`answers.py`, section 3)

Five predictions about whether writing through a second name changes the
first. Answer them from what you believe *before* running anything — this is
the section where most people discover their mental model was wrong, and that
discovery only happens if you commit to an answer.

## Exercise 4 — broadcasting (`answers.py`, section 4)

Five predictions. Apply the rule by hand, right to left, before you let NumPy
apply it for you:

1. Line the two shapes up from the **right-hand** end.
2. A missing entry on the left of the shorter shape counts as 1.
3. Two dimensions are compatible when they are equal, or one of them is 1.
4. If any pair is neither, the operation is an error.
5. The result takes the larger of each pair.

## Exercise 5 — axis=0 against axis=1 (`answers.py`, section 5)

Seven predictions, and the one rule that settles it permanently:

> **The axis you name is the axis that disappears.**

A `(3, 4)` array summed with `axis=0` loses the 3 and returns shape `(4,)`. The
same array summed with `axis=1` loses the 4 and returns shape `(3,)`.

---

## When you are finished

Compare your `matrix.py` with `../examples/matrix.py`. They should agree on
behaviour; they need not agree on wording. Then read
`../examples/03_views_and_copies.py` and `../examples/04_broadcasting.py`,
which go several steps past what the predictions asked for.
