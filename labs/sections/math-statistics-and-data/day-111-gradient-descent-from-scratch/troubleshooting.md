# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'dataset'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `dataset` and `descent` from beside
themselves.

```bash
cd examples
../.venv/bin/python3 01_the_hook.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test
file's own directory on the import path.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. Everything in
this lab goes through `.venv/bin/python3`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you would rather use an interpreter you already have, the harness
accepts one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## The starter tests all skip and I have written code

A skip means the function still returns `None`. Look for a leftover
`return None` below the code you added — every skeleton has it on the last
line of the docstring, and it is easy to write the body above it and leave
the `return None` in place, in which case your work is computed and then
discarded.

## My `classify_regime` says "divergent" for the monotone or oscillating case

Check your shrinking test. `values[i + 1] <= values[i] + 1e-12` needs the
small slack — without it, float64 rounding on the very last step of a
run that is converging towards exactly zero can make a value that should
compare equal look very slightly larger than its predecessor, and a
strict `<=` with no slack then misclassifies a converging run as
divergent.

## My contraction ratio does not match `|1 - eta*a|`

Two likely causes. First: check you are computing `|x_{n+1} / x_n|`, not
`|x_n / x_{n+1}|` — the ratio is direction-sensitive in code even though
the ordering does not matter for the final ratio at fixed `eta` and `a`.
Second: if you are testing the "exact" regime (`eta = 1/a`), `x_1` is
exactly `0.0`, so `x_2 / x_1` divides by zero — `per_step_ratios` must
skip steps where `x_n == 0`, which is exactly what the reference
implementation does.

## My isotropic bowl (kappa=1) does not converge in one step

Check the learning rate you are passing. `dataset.kappa_lr(1)` returns
`2.0 / (1.0 + 1) = 1.0`, which is exactly the reciprocal of the only
eigenvalue an isotropic bowl has — the same "exact" boundary exercise 3
meets on the 1-D quadratic, applied in both directions of a 2-D bowl at
once. If you hard-coded a different learning rate for exercise 5, this
result will not appear.

## Momentum needs *more* steps than plain descent in my run

Check that both calls use the **same** learning rate,
`dataset.kappa_lr(dataset.MOMENTUM_KAPPA)` — `dataset.MOMENTUM_LR` already
equals that value, so if your momentum call uses a different constant the
comparison is not the one the exercise is testing. Also check the update
order inside your momentum loop: `v` must be updated with the gradient
**before** `x` is updated with the new `v`. Reversing the order still
runs and still looks plausible, but it uses last step's velocity to make
this step's move, which is a different (and, on this bowl, slower)
algorithm.

## My gradient check flags every component, not just the buggy one

`gradient_check` must compare component by component and return a list,
not a single boolean over the whole vector. If you are collapsing the
comparison to `np.allclose(...)` first and then reporting one flag,
you have thrown away the information the exercise is built to preserve.

## My two-minima run converges to the same point from both starts

Check `dataset.TWO_MINIMA_LEFT_START` and `..._RIGHT_START` are on
opposite sides of `x = 0` — `-0.1` and `0.1` — and that
`dataset.TWO_MINIMA_ITERS` (400) is large enough for both runs to
actually reach their minima rather than stop partway. A learning rate
that is too large here can also overshoot past `x = 0` on the first step
and land both runs in the same basin; `dataset.TWO_MINIMA_LR = 0.05` was
chosen specifically to avoid that.

## The stopping-criterion trap doesn't trip in my run

Check you are comparing `grad_fn(x)` and `value_fn(x)` at the **same** `x`
before the step, and `value_fn` again at `x - lr * grad_fn(x)` after it —
not, for instance, the gradient before the step against the value after
it. Also confirm you used `dataset.PLATEAU_X0`, `..._LR`, `..._GRAD_TOL`
and `..._DELTA_F_TOL` rather than the constants from the ill-conditioning
section; the two sets of tolerances are sized for different comparisons
and are not interchangeable.

## The opening hook run raises a `RuntimeWarning` about overflow

Your `gradient_descent` loop is not wrapped in
`np.errstate(over="ignore", invalid="ignore")`. The overflow is the
point — a diverging training run really does look like this — not a bug
to be silenced by catching an exception, and the reference implementation
never raises.

## `__pycache__` or `.pytest_cache` appears and section 7 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-path ./.venv -prune` in that command, and note that the harness
uses the same prune. NumPy and pytest ship their own `__pycache__`
directories inside the virtual environment; those are theirs, not litter
you created, and a check that searched them would report a failure you
cannot fix and did not cause. `.venv` itself is the documented setup and
is never treated as a stray file.

You should not actually be able to hit this in normal use. The "How to
run" section tells you to run `.venv/bin/pytest starter -q` while you
work, and that command *does* write `starter/__pycache__` and
`.pytest_cache` — it has no reason not to. The harness clears both at the
**start** of its run, pruning `.venv`, so the check at the end measures
what this run left rather than what an earlier command left. If you edit
`tests/run_tests.sh`, keep that block where it is.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/`
and `starter/` contain modules called `dataset` and `descent`. Without
the `conftest.py` in each directory, collecting both suites at once would
import whichever module was seen first and reuse it for the other — so
your unwritten starter exercises would silently pass against the
reference solution. A wrong answer with a green tick on it is the worst
kind of wrong answer.

If you delete or edit either `conftest.py`, section 4 of the harness will
notice: it compares the skip count from `pytest starter` against the skip
count from `pytest` with no arguments and requires them to be identical.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`.
Everything in the lab is plain arithmetic and NumPy, so nothing in it is
platform-specific — but "should work" and "was run" are different claims
and only the second one is worth making.
