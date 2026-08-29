# The Vectors That Keep Their Direction — your brief

Five exercises, in order. Exercise 1 is code; exercises 2 to 5 are predictions
you write down before you run anything.

Everything you write goes in exactly two files:

- `starter/eigen.py` — six functions, each currently `return NotImplemented`
- `starter/answers.py` — twenty-six predictions, each currently `None`

Nothing else in `starter/` needs editing, and `starter/dataset.py` is read-only
data you should read rather than change.

## Before you start

From the **lab directory** (the one with `README.md` in it), not from
`starter/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest starter -q
```

That last command should print:

```
1 passed, 52 skipped
```

The one pass is `test_the_environment_is_ready`. The fifty-two skips are the
exercises. **A skip means "not attempted", not "broken".** When it says
`53 passed`, you are finished.

Run that command as often as you like. A failure prints your answer beside the
real one, so a wrong guess still teaches you something.

## The one habit that matters more than any other

An eigenvector is defined **only up to sign and scale**.

If `A v = lambda v`, then the same equation holds for `-v`, for `3.7 v`, and
for every other non-zero multiple. There is no such thing as *the* eigenvector
for an eigenvalue — there is an eigen-**line**, and every library that hands
you one vector has made an arbitrary choice on your behalf.

So `(1, -2)`, `(-1, 2)` and `(0.447, -0.894)` are all the same answer, and
`numpy.allclose` will tell you two of them are wrong.

Every test in this lab compares **directions**, using the absolute cosine.
Write your code the same way and this trap never catches you. Fight it — try to
"fix" a sign somewhere — and you will spend an hour on a bug that was never
there. Exercise 5f is built to spring this trap on purpose.

---

## Exercise 1 — write the six functions (`starter/eigen.py`)

Each function's docstring gives the steps and, where it matters, says why the
obvious implementation is wrong. Read the docstring before writing the body.

| Function | What it does | Watch out for |
| --- | --- | --- |
| `abs_cosine(u, v)` | 1.0 when `u` and `v` lie on the same line | Take the **absolute** value. Raise `ValueError` mentioning "no direction" on a zero vector. |
| `characteristic_coefficients(matrix)` | `(trace, determinant)` of a 2x2 | Raise `ValueError` mentioning "2x2" on anything else. |
| `eigenvalues_2x2(matrix)` | Solve the characteristic equation | Use `numpy.emath.sqrt`, **not** `numpy.sqrt`. Return complex always. |
| `eigenvector_2x2(matrix, eigenvalue)` | A unit eigenvector for a real eigenvalue | Try both rows. Do not try to fix the sign. |
| `power_method(matrix, start, ...)` | The dominant eigenvector by repeated multiplication | Normalise every round. Align the signs. Report non-convergence rather than raising. |
| `covariance_matrix(data)` | Covariance of an `(n_points, n_features)` array | **Centre it first.** Divide by `n - 1`. |

Check your progress at any point:

```bash
.venv/bin/pytest starter -q -k "1a or 1b or 1c or 1d or 1e or 1f"
```

Two of these have a failure mode that produces a plausible wrong answer rather
than an error, which is why they get their own warning here:

- **`eigenvalues_2x2` with `numpy.sqrt`.** On a rotation the discriminant is
  negative. `numpy.sqrt(-4.0)` returns `nan` and emits a `RuntimeWarning`;
  `numpy.emath.sqrt(-4.0)` returns `2j`, which is the actual answer. Test 1c
  checks the rotation case for exactly this reason.
- **`power_method` without the sign alignment.** Give it a matrix whose
  dominant eigenvalue is *negative* and the iterate flips direction every
  single step. The answer converged on round three; your `change` measurement
  never drops below `tol` and the loop runs to `max_iter` reporting failure.
  Test 1e uses `numpy.diag([-5.0, 2.0])` to catch this.

## Exercise 2 — solve the 2x2 by hand (`starter/answers.py`, 2a–2g)

```
A = [[4, 1],
     [2, 3]]
```

Pencil and paper. Seven answers, none of them needing a calculator:

1. The trace, then the determinant.
2. The characteristic equation is `lambda^2 - b*lambda + c = 0`. Those two
   numbers are the trace and the determinant, in that order — derive that once
   from `det(A - lambda*I)` and you never have to again.
3. The discriminant `b^2 - 4c`. Its **sign** is the interesting part.
4. Both eigenvalues, largest first. The quadratic factorises over the integers.
5. An eigenvector for each. For `lambda = 5`, the first row of `A - 5I` is
   `[-1, 1]`, which says `-x + y = 0`. For `lambda = 2`, the first row of
   `A - 2I` is `[2, 1]`.

Any non-zero multiple of the right eigenvector passes. Check yourself before
running: `A @ (1, 1)` should come out as exactly `5 * (1, 1)`.

## Exercise 3 — the standard transformations (`answers.py`, 3a–3g)

The matrices from Day 102, and what each one does to directions. Predict from
the **geometry** first, then run `examples/03_standard_transformations.py` and
see whether you were right.

- **3a** — the shear `[[1, 1], [0, 1]]`. Count eigen-**lines**, not columns
  returned by NumPy. Those are different numbers here, and the difference is
  the question.
- **3b, 3c** — the 90-degree rotation. Picture an arrow being turned before you
  reach for any algebra. Then remember that a rotation changes no lengths.
- **3d** — what dtype does `numpy.linalg.eig` return for `A`, whose eigenvalues
  are 5 and 2, both real? Predict from the documentation, then measure. If your
  prediction and the machine disagree, **the machine is right**, and that
  disagreement is one of the things this lab exists to show you.
- **3e** — the projection `[[1, 0], [0, 0]]`. Its determinant and its smaller
  eigenvalue are the same number, and Day 102 explains why.
- **3f** — the reflection. One eigenvalue is negative. Say out loud what a
  negative eigenvalue means before you write it down.
- **3g** — for a symmetric matrix, at what angle do the eigenvectors meet?

## Exercise 4 — the power method (`answers.py`, 4a–4e)

Multiply, normalise, repeat. Predict what it converges to and how fast.

- **4a, 4b** — which eigenvalue and which direction. The clue is in the name
  "dominant".
- **4c** — each round the error shrinks by a constant factor. It is a ratio of
  the two eigenvalues, and the **smaller one is on top**. Reason about which
  ingredient of the mixture is dying out relative to which.
- **4d** — eigenvalues of 5 and 4.9 instead of 5 and 2: more iterations or
  fewer?
- **4e** — what happens to the raw length of `A^k v0` if you never normalise?

`examples/04_power_method.py` shows every one of these happening, with the
iteration table printed step by step. Predict first, then read it.

## Exercise 5 — PCA (`answers.py`, 5a–5g)

The cloud in `dataset.py` is 400 points deliberately stretched along **30
degrees**, with a standard deviation of 3.0 along that direction and 0.4 across
it, centred at `(5, -2)`. That direction appears nowhere in the array. PCA has
to rediscover it from 400 pairs of coordinates.

- **5a, 5b** — the shape of the covariance matrix of a `(400, 2)` dataset, and
  whether it is symmetric. It is neither `(400, 400)` nor `(400, 2)`.
- **5c, 5d** — where the top eigenvector points, and what the square root of
  the top eigenvalue comes out near.
- **5e** — `eig` or `eigh` for a covariance matrix?
- **5f** — the sign trap, sprung. The top component is **correct** and
  `numpy.allclose` against the true direction returns... what?
- **5g** — forget to subtract the mean. Is the answer still within 5 degrees?

## When you are done

```bash
.venv/bin/pytest starter -q          # expect: 53 passed
bash tests/run_tests.sh              # expect: 0 failure(s), exit 0
```

Then read `examples/` end to end. Every function you wrote has a reference
version there with a docstring explaining the choices, and the six numbered
scripts print the whole story with real numbers. Reading them *after* writing
your own is worth several times reading them before.
