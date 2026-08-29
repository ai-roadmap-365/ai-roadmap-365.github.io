# Troubleshooting — Day 106 lab

Symptoms first, because that is what you have when something goes wrong.

---

## The three that catch nearly everyone

### "My eigenvector is wrong but the numbers look right"

**Symptom.** You computed `[0.447, -0.894]`. The expected answer is
`[-0.447, 0.894]`. `numpy.allclose` says `False`. Everything else passes.

**Cause.** Nothing is wrong. Both answers are correct.

An eigenvector is defined **only up to sign and scale**. If `A v = lambda v`,
multiply both sides by any non-zero number `c`:

```
A (c v) = c (A v) = c (lambda v) = lambda (c v)
```

So `c v` is an eigenvector too, for every `c` — including `-1`. There is no such
thing as *the* eigenvector for an eigenvalue; there is an eigen-**line**, and
every library that hands you one vector has made an arbitrary choice on your
behalf. Which sign LAPACK picks is a detail of its internal normalisation, not
a fact about your matrix.

**Fix.** Compare directions, not components:

```python
def abs_cosine(u, v):
    return abs(float(np.dot(u, v))) / (np.linalg.norm(u) * np.linalg.norm(v))
```

`1.0` means "same line". That is the only question with a determinate answer.

**Do not** "fix" this by flipping a sign somewhere. You will make one case pass
and another fail, and you will be back here in an hour. The reference test
`test_the_sign_ambiguity_is_real_and_component_comparison_fails` exists to pin
this down, and its docstring says in as many words: do not fix it.

---

### "`numpy.sqrt` gave me `nan` on the rotation"

**Symptom.**

```
RuntimeWarning: invalid value encountered in sqrt
eigenvalues: (nan, nan)
```

**Cause.** A plane rotation has a **negative** discriminant. For the 90-degree
rotation, trace is 0 and determinant is 1, so `b^2 - 4c = -4`. `numpy.sqrt` of a
negative float returns `nan` and warns, because it is a real-valued function
being asked for something that is not real.

That is not an error condition. It is the correct answer arriving in the wrong
container. A rotation turns **every** vector off its line, so there is no real
eigenvector, and the negative discriminant is the algebra reporting exactly that
geometry.

**Fix.** Use `numpy.emath.sqrt`, which returns a complex root when the input is
negative:

```python
>>> np.sqrt(-4.0)
nan
>>> np.emath.sqrt(-4.0)
2j
```

Then `eigenvalues_2x2` returns `(0+1j, 0-1j)` for the rotation, which is what
`numpy.linalg.eig` returns too, and the caller needs no special case.

---

### "My power method never converges"

**Symptom.** `converged` comes back `False` and `iterations` equals `max_iter`,
on a matrix that ought to be easy. Printing the vector each round shows it
landing on the right direction almost immediately and then apparently jittering
forever.

**Cause.** Almost always the missing sign alignment, and it only shows up when
the dominant eigenvalue is **negative**.

Take `numpy.diag([-5.0, 2.0])`. Its dominant eigenvalue is `-5`, so every
multiplication flips the vector end to end:

```
v      = [1, 0]
A @ v  = [-5, 0]  ->  normalised  [-1, 0]
A @ v  = [5, 0]   ->  normalised  [1, 0]
```

The **direction** converged on round one. The distance between successive unit
vectors is `2.0` forever, so a convergence test on that distance never fires.

**Fix.** Align the signs before measuring the change:

```python
w = matrix @ v
w = w / np.linalg.norm(w)
if np.dot(w, v) < 0:
    w = -w            # a flip is not a failure to converge
change = np.linalg.norm(w - v)
```

`test_1e_power_method_handles_a_negative_dominant_eigenvalue` uses exactly that
matrix to catch this.

---

## Setup

### `python3: command not found`

Install Python 3.11 or later. On macOS, `brew install python@3.14`; on Debian or
Ubuntu, `sudo apt install python3 python3-venv`. Then re-run the install steps
in `README.md`.

### `pip: command not found` after creating the venv

The venv did not finish building. On Debian and Ubuntu this usually means the
`python3-venv` package is missing:

```bash
sudo apt install python3-venv
rm -rf .venv
python3 -m venv .venv
```

### `ModuleNotFoundError: No module named 'numpy'`

You are running the system Python rather than the lab's. Use the full path:

```bash
.venv/bin/python3 examples/01_the_fan_of_vectors.py   # not: python3 ...
```

Or activate the environment first with `source .venv/bin/activate`.

### `FAIL: pytest not found` from the harness

The harness looks for pytest in three places, in order: the `PYTEST` environment
variable, `.venv/bin/pytest`, then your `PATH`. If none has it, install the
lab's dependencies or point it at an existing pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

It then uses the `python3` sitting beside that pytest, because that is the
interpreter the packages are installed into.

### `installed numpy matches requirements.txt (expected [2.5.2], got [...])`

You have a different NumPy. The lab will still run and almost everything will
pass. Two things may differ, and `expected-output/FIELDS.md` explains both: on
NumPy 1.x the seeded cloud draws different points, so the PCA digits change
while the claims hold; and if a future version starts casting real-eigenvalued
results to `float64`, the `complex128` test goes red — which is the **correct**
outcome and means the lesson text needs updating, not the test.

To match exactly:

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

---

## Running the exercises

### `pytest starter` says `52 skipped` and I have written code

Check three things, in order.

1. **Are you running from the lab directory?** Not from inside `starter/`.

   ```bash
   .venv/bin/pytest starter -q      # from the directory holding README.md
   ```

2. **Did you remove the `return NotImplemented` line?** A function that still
   returns it is treated as unattempted, by design, so an unwritten exercise
   skips instead of failing with a confusing type error.

3. **Did you set the value in `answers.py`, not just compute it?** Exercises 2
   to 5 read module-level names. A value still equal to `None` skips.

### A starter test fails and I think my answer is right

Read the failure message. Every assertion in `test_starter.py` that can fail in
an interesting way prints your value beside the expected one and says what the
likely cause is. The common genuine-looking failures:

| Failure | Nearly always |
| --- | --- |
| `1a abs_cosine ignores a sign flip` | You forgot `abs()`. |
| `1c a rotation gives complex eigenvalues` | `numpy.sqrt` instead of `numpy.emath.sqrt`. |
| `1e power method converges` — got the wrong iteration count | You measured the change *before* normalising, or omitted the sign alignment. |
| `1f covariance matches numpy` — close but not equal | You divided by `n` instead of `n - 1`. |
| `1f covariance matches numpy` — far out | You forgot to subtract the mean. |
| `3d eig dtype on A` | You predicted `float64` from the documentation. The machine says `complex128`. The machine is right. |
| `5f allclose on the correct component` | You predicted `True`. Read the sign section at the top of this file. |

### `test_3d_eig_dtype_on_a` fails and I predicted what the docs say

That is the point of the exercise, and the failure message says so. The
docstring shipped with numpy 2.5.2 claims the result "will be of complex type,
unless the imaginary part is zero in which case it will be cast to a real type".
Measured on this machine, the imaginary part **is** zero and the cast does
**not** happen — for `A`, for `numpy.eye(2)`, for `numpy.diag([1., 2., 3.])` and
for an integer matrix.

When documentation and measurement disagree, the measurement wins. Answer
`'complex128'`.

---

## The harness

### `bash: tests/run_tests.sh: No such file or directory`

Run it from the lab directory, not from `tests/`:

```bash
cd labs/sections/math-statistics-and-data/day-106-eigenvalues-and-eigenvectors-intuitively
bash tests/run_tests.sh
```

### The harness reports success but my shell says the command failed

You are reading the exit status of a **pipeline**, not of the script:

```bash
bash tests/run_tests.sh | tail -3 ; echo $?   # this is tail's status
```

Check the script's own status:

```bash
bash tests/run_tests.sh; echo "exit=$?"
```

### `no __pycache__ directory left under the lab` fails

Something wrote bytecode during a manual run. Clean it up:

```bash
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note that the harness prunes `.venv` before looking, deliberately — NumPy ships
113 `__pycache__` directories inside it, and `.venv` is documented setup rather
than litter. If this check fails, the directory really is somewhere else in the
lab.

### `collecting both suites at once does not turn skips into passes` fails

This is an important failure, not a cosmetic one.

Both `examples/` and `starter/` contain modules called `eigen` and `dataset`.
pytest imports test files by putting their directory on `sys.path`, so a bare
`pytest` over the whole lab could import whichever `eigen` it saw first and reuse
it for both suites — meaning your unwritten starter exercises would silently
pass **against the reference solution**. A wrong answer with a green tick on it
is the worst kind.

Each directory's `conftest.py` prevents that by putting its own directory first
on the path and dropping any already-imported `eigen` or `dataset` that came
from elsewhere. If this check fails, one of those `conftest.py` files has been
edited or deleted. Restore it:

```bash
git checkout -- examples/conftest.py starter/conftest.py
```

### Section 6 fails: "a deliberately wrong expectation makes the harness exit non-zero"

Section 6 re-runs the whole script with `D106_SELF_TEST=1`, which swaps one
expectation for a deliberately wrong one, and checks that the re-run reports the
failure and exits non-zero. If *this* check fails, the harness has lost the
ability to detect failures at all, and every other green tick in the run is
worthless.

Check that `tests/run_tests.sh` has not been edited, particularly the
`check`/`check_eq` functions and the final `[ "${failures}" -eq 0 ]` line.

---

## Results that look wrong but are not

| What you see | Why it is correct |
| --- | --- |
| `eigenvalues = [5.+0.j 2.+0.j]` on a real matrix | `numpy.linalg.eig` returns `complex128` regardless. Measured, contradicts its own docstring. Take `.real` **after** checking the imaginary parts are zero. |
| `eig` returns two columns for the shear | It must return a square array. The shear has only one eigen-line and both columns lie on it — absolute cosine `1.0`. Count lines, not columns. |
| The sweep reports the shear's line at `0.005` rather than `0.000` | A sampled sweep cannot beat its own grid spacing, and the shear's deviation curve is not symmetric about its eigendirection. The **count** is the reliable output; use the algebra for the exact angle. |
| The sweep says "every direction" for the identity, but `eig` returned `[0, 90]` degrees | Both are right. When every direction is an eigenvector, `eig` still has to return exactly two columns, so it returns a basis and the arbitrariness becomes invisible. |
| A projection's collapsed direction has `nan` deviation | The zero vector has no direction, so "did it keep its direction?" has nothing to compare against. Eigenvalue 0 is real and the algebra finds it; measuring angles cannot. |
| `numpy.linalg.inv` on the shear's eigenvector matrix does not raise | Its determinant is `2.2e-16`, not exactly zero, so LAPACK inverts it and returns entries around `4.5e15`. The reconstruction comes back as a clean, plausible, wrong identity matrix. Check the **condition number**, not for an exception. |
| The Rayleigh quotient is not converging quadratically | The textbook claim needs orthogonal eigenvectors, which symmetry guarantees. This lab's `A` is not symmetric — its eigen-lines meet at `71.5651` degrees — so the quotient converges merely linearly. Measured both ways in `04_power_method.py`. |
| PCA's top component is `[-0.865, -0.502]` when the truth is `[0.866, 0.500]` | Opposite ends of the identical line. Absolute cosine `0.9999984422`. A principal component names an **axis**, not an arrow. |
| The `eig`/`eigh` timing ratio on your machine is not `10.46x` | It is one machine on one day and depends on your BLAS build, core count and thermal state. Nothing asserts it. Expect `eigh` to still win. |

---

## Still stuck

1. Read `expected-output/FIELDS.md`. It names every value that may legitimately
   differ on your machine, and a flipped eigenvector sign is top of that list.
2. Compare your output against the matching file in `expected-output/`. Those
   were captured from real runs and never edited.
3. Read the reference implementation in `examples/eigen.py`. Every function's
   docstring explains not just what it does but why the obvious version is
   wrong.
4. Re-run from clean:

   ```bash
   rm -rf .venv .pytest_cache
   find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
   git checkout -- starter/
   python3 -m venv .venv
   .venv/bin/pip install -r requirements/requirements.txt
   bash tests/run_tests.sh
   ```
