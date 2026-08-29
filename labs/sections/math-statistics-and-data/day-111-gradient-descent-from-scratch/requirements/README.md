# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | Vectors for the two-dimensional ill-conditioning and momentum exercises (5, 6), reading float64's machine epsilon from `numpy.finfo`, and `np.linalg.norm` for the stopping-tolerance checks. |
| `pytest` | 9.1.1 | MIT | The reference suite and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 7 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/` to
prove that nothing else does.

## If you cannot install anything at all

You lose relatively little. Every scalar exercise (1 through 4, 7, 8 and 9)
needs only `math` and the standard library — a plain Python float and a
`for` loop compute all of them. Only the two-dimensional bowl in exercises 5
and 6 genuinely wants a small array type; without NumPy, `x, y = point` on a
two-element Python list or tuple does the same job with a few more lines,
and `math.hypot(x, y)` replaces `np.linalg.norm`.

What you lose without `pytest` is the running score and the skip-versus-fail
distinction — you would read your own printed numbers against the ones in
`expected-output/` instead.

## What is deliberately *not* installed

`scipy.optimize.minimize`, `torch.optim.SGD` and `jax.grad` with `optax` all
do this job at production scale, and none of them is installed here. **No
output from any of them is reproduced anywhere in this lab or its lesson.**
They are described from their documentation, and the lesson's tools section
marks each one as not run here.

That is not a limitation to apologise for. The nine exercises in this lab are
the same update rule every one of those tools runs underneath — `x <- x -
lr * grad(x)`, or a running average of it — with the engineering (batching,
adaptive learning rates, GPU dispatch, automatic differentiation feeding the
gradient in) removed. Having written the loop by hand, you will read a
`for epoch in range(...): optimizer.step()` differently.
