# The brief — Vectors You Can Hold

You run a small recipe-and-lifestyle site with six articles on it. Somebody
has asked for a "related articles" box: given one article, show the one most
like it.

You have no machine learning, no search engine and no budget. What you do have
is a text file per article, and the ability to count words.

So you count. For each article you count how many times it mentions cooking,
running, money and weather. Four numbers per article, always in that order.

| article | cooking | running | money | weather |
| --- | --- | --- | --- | --- |
| `roast-chicken` | 9 | 0 | 1 | 0 |
| `slow-cooker-stew` | 8 | 0 | 2 | 0 |
| `marathon-plan` | 0 | 9 | 1 | 2 |
| `race-day-nutrition` | 4 | 6 | 3 | 0 |
| `household-budget` | 1 | 0 | 9 | 0 |
| `storm-bulletin` | 0 | 1 | 0 | 9 |

That table is the entire lab. Each row is a **vector** — a list of numbers in a
fixed order where position carries meaning. The first number is always cooking.
Swap two columns and every row becomes a lie.

You already believe, looking at that table, that `roast-chicken` and
`slow-cooker-stew` belong together and that `storm-bulletin` belongs with
nothing. Your job today is to make that belief into arithmetic, so a program
can have it too.

## What you are building

Nine functions in `vectors.py`, in order, each one a few lines:

| # | function | what it does |
| --- | --- | --- |
| 1 | `add(u, v)` | componentwise sum |
| 2 | `subtract(u, v)` | componentwise difference |
| 3 | `scale(k, v)` | multiply every component by `k` |
| 4 | `dot(u, v)` | multiply matching components, add them up — returns one number |
| 5 | `l2_norm(v)` | magnitude: square, add, square-root |
| 6 | `l1_norm(v)` | taxicab length: add the absolute values |
| 7 | `distance(u, v)` | the magnitude of the difference |
| 8 | `normalise(v)` | scale to magnitude 1, keeping direction |
| 9 | `nearest(query, labelled)` | the closest entry in a labelled collection |

Exercise 7 is the one to notice. There is no distance formula to learn:
subtract, then measure. Once you see that, most of the rest of linear algebra
stops looking like a list of formulae to memorise.

## Four numbers to check yourself against

Do these on paper before you run anything. If your code disagrees with the
paper, the code is wrong.

- `l2_norm([3, 4])` — 9 + 16 = 25, so the answer is **5**.
- `l2_norm([2, 3, 6])` — 4 + 9 + 36 = 49, so **7**.
- `distance([1, 2], [4, 6])` — the difference is (−3, −4), 9 + 16 = 25, so **5**.
- `distance(roast-chicken, slow-cooker-stew)` — the difference is (1, 0, −1, 0),
  1 + 0 + 1 + 0 = 2, so **sqrt(2) ≈ 1.4142**.

## The trap, stated in advance

When you finish exercise 8, you will want to write this:

```python
assert l2_norm(normalise(v)) == 1.0
```

Do not. It passes for `[3, 4]` and fails for `[1, 1]`, and your code is correct
in both cases. A float is a binary approximation, and dividing by a square root
and squaring the results back up does not have to land on exactly 1.0. Day 46
covered this; today is where it bites.

Every assertion in this lab uses `math.isclose` or `numpy.allclose` with a
stated tolerance — `rel_tol=1e-9, abs_tol=1e-12`. There is a test whose only
job is to prove, on your machine, that `==` would have failed.

## How to work

```bash
python3 starter/vectors.py       # a progress report: which exercises return something
.venv/bin/pytest starter -q      # the exercise suite
```

Before you start: 1 test passes, 11 are skipped. Finish an exercise, delete the
`@pytest.mark.skip(...)` line above its test, run again. When all 12 pass, run
the reference programs in `examples/` and compare your reasoning with theirs.

## Do not import NumPy in `vectors.py`

Write the loops. NumPy does exactly what you are about to write, only faster,
and `examples/agreement.py` proves it operation by operation on the same
inputs. A reader who wrote the loop understands what the library is doing
before being asked to trust it — and that is the difference between using
NumPy and being at its mercy.
