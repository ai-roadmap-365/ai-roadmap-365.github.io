# Multiply It Yourself — the six exercises, in order

Work top to bottom. Check yourself at any point from the **lab directory**:

```bash
.venv/bin/pytest starter -q
```

On an untouched checkout that prints `1 passed, 56 skipped`. A skip means
"not attempted". A failure means "attempted and wrong", and it prints both your
answer and the real one. When it prints `57 passed`, you are finished.

Two rules that make this worth doing:

1. **Write the answer down before you run anything.** Every prediction in
   `answers.py` can be done with a pen in under a minute. If you run the code
   first and then fill them in, all of them will be right and you will have
   learned nothing.
2. **Do not import NumPy in `matmul.py`.** Exercise 1 is a from-scratch build.
   Its whole value is that you can read every line and see where each number
   came from.

The matrices used throughout, so you never have to hunt for them:

```
X    = [[1, 2, 0],        (2, 3)   a batch: two examples, three features
        [0, 1, 3]]

W    = [[ 2, 0],          (3, 2)   a layer's weights: three in, two out
        [-1, 1],
        [ 0, 4]]

bias = [5, -2]            (2,)     one per output unit

u    = [10, 2, 5]         (3,)

P    = [[1, 2],           (2, 2)
        [3, 4]]

Q    = [[5, 6],           (2, 2)
        [7, 8]]

A = ROT90  = [[0, -1],    (2, 2)   a quarter turn anticlockwise
              [1,  0]]

B = FLIP_X = [[1,  0],    (2, 2)   a reflection in the horizontal axis
              [0, -1]]

v    = [3, 1]
```

---

## Exercise 1 — build it (`matmul.py`)

Nine functions, each marked `EXERCISE` in the file. Written for you already:
`shape`, `transpose`, and the `ShapeMismatch` exception.

| # | Function | The idea |
| --- | --- | --- |
| 1.1 | `dot` | Multiply pairwise, then add. Six lines. |
| 1.2 | `check_multipliable` | The shape rule, with an error message that names both shapes. |
| 1.3 | `matmul_loops` | Three nested loops. The definition, transcribed. |
| 1.4 | `matvec` | A vector, as a weighted sum of the matrix's **columns**. |
| 1.5 | `matmul_dots` | The same product, as a list of dot products. |
| 1.6 | `identity` | The matrix that does nothing. |
| 1.7 | `add_bias` | Broadcasting, written out as a loop. |
| 1.8 | `multiplication_count` | Count the work: one expression. |
| 1.9 | `chain_costs` | Both associations of a three-matrix chain. |

Two traps worth naming before you meet them.

**In 1.3, build the result grid with `[[0] * p for _ in range(m)]`.** The
shorter-looking `[[0] * p] * m` makes `m` references to **one** row, so writing
to `C[0][0]` changes every row at once. That is the view-versus-copy lesson from
Day 100 turning up in plain Python, and there is a test that catches it by name.

**In 1.4, resist writing "dot v with each row".** It gives the right numbers and
the wrong picture. Write it as columns: take `v[0]` copies of column 0, plus
`v[1]` copies of column 1, and add them up. Then try `matvec(A, [1, 0])` and see
which column comes back. That is the fact everything in Week 15 rests on.

---

## Exercise 2 — the shape rule (`answers.py`)

Eight predictions. For each expression, give the shape of the result, or the
string `"error"`. Derive them from the rule rather than recalling them:

> An `(m, n) @ (n, p)` is legal only when the inner dimensions agree, and the
> result is `(m, p)`.

And one question with a different flavour: which exception **class** does NumPy
raise when they do not agree? Give the class, not its name as a string.

---

## Exercise 3 — composition and order (`answers.py`)

Seven predictions, all doable with a pen — each is four multiplications and two
additions.

Apply `B` to `v`. Then apply `A` to that. Then work out the single matrix
`A @ B` and check it takes `v` to the same place in one step. Then do `B @ A`
and see that it does not.

The question that decides whether you have understood it: **in `A @ B @ v`,
which matrix meets the vector first?** Think about `A @ (B @ v)` before you
answer.

---

## Exercise 4 — `*` against `@` (`answers.py`)

Seven predictions. `P * Q` and `P @ Q` are both legal, both return a `(2, 2)`
array, and are not the same numbers — so no shape check will save you.

Then `X * u` and `X @ u`, where the shapes finally do differ, and one question
that states the whole distinction as code: **`@` is `*` followed by a sum along
which axis?**

---

## Exercise 5 — one layer of a neural network (`answers.py`)

Compute `X @ W + bias` entirely by hand and record both the product and the
final output. Four dot products of length three, then two additions per row.

This is the operation that consumes essentially all the compute in training any
model you will ever use. Doing it once with a pen is the point of the day.

Then three questions about what the shapes mean: is the bias one per example or
one per output; which shapes change when the batch grows; and whether two
layers with no activation function between them collapse into one.

---

## Exercise 6 — cost (`answers.py`)

Seven predictions. Count the multiplications for a small layer and for a pair of
200 by 200 matrices. Then count both associations of the chain
`(10, 100) @ (100, 5) @ (5, 50)` and say which is cheaper — and confirm that
they nonetheless give the same answer.

The last question is the one the timing script is really about. NumPy's `@` on a
`float64` array is dramatically faster than on an `int64` array of the same
shape and the same values. Four explanations are offered; one is true. Run
`05_cost_and_speed.py` if you want the evidence before committing.

---

## When you are done

Read the reference, which is written to be read rather than merely to be
correct. Each script prints its working and asserts every claim it makes:

```bash
cd examples
../.venv/bin/python3 01_matmul_from_scratch.py
../.venv/bin/python3 02_composition.py
../.venv/bin/python3 03_star_versus_at.py
../.venv/bin/python3 04_network_layer.py
../.venv/bin/python3 05_cost_and_speed.py
cd ..
```

Then the full harness:

```bash
bash tests/run_tests.sh
echo "exit=$?"
```
