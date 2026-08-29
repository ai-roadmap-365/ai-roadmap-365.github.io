# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection
after the one-time `pip install`, needs no credentials, no `sudo` and no
elevated permissions, and touches nothing outside its own directory.
Every number it works with is invented and is stated to be invented: the
curvature `a = 5`, the four learning rates, the condition numbers, the
momentum coefficient, the gradient-check point and its deliberately
broken gradient, the two-minima starting points and the plateau's
curvature are all written out in `examples/dataset.py`.

Section 7 of `tests/run_tests.sh` greps every source file in `examples/`
and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
`https://` and fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory,
so nothing installed here can affect the rest of your machine, and
`rm -rf .venv` is a complete undo. The two packages are pinned to exact
versions in `requirements/requirements.txt`, and section 1 of the harness
reads the installed version back and compares it against that file rather
than trusting that the install did what it said.

Pinning is a security property as much as a reproducibility one: an
unpinned `numpy` in a lab that a few thousand people will run is an
invitation you did not mean to send.

## Three things worth carrying away from this particular day

**A learning rate that is only slightly too large produces a run that
looks like it is training, right up until it is not.** The opening
demonstration's loss increases smoothly, step after step, for thousands
of iterations, before it overflows to `inf` and then `nan` on the very
next step. Nothing about the early steps announces the coming failure —
the loss simply climbs, the way a loss climbing for a completely
different, more mundane reason (a bad batch, a bug in a preprocessing
step) also climbs. A training loop that does not check its own loss for
finiteness will spend real compute time computing with `nan` before
anyone notices, and the earlier it is caught the cheaper the mistake.

**A silently wrong gradient is worse than a crash.** The gradient check
in exercise 7 exists because a gradient with a sign error in one
component runs, produces numbers of a plausible shape, and moves a model
in a direction that is *partly* right — which is exactly what makes it
survive casual testing. The only defence used throughout this lab is the
one exercise 1 builds: compare the analytic gradient against an
independent numerical one that shares none of its assumptions, and do it
per-component so the failure is localised rather than merely detected.

**A stopping rule that only watches the loss can declare victory on a
problem that has not been solved.** Exercise 9's plateau is a genuine,
bounded convex bowl — not a pathological edge case — and one step from a
point far from its minimum already produces a loss change below a
plausible tolerance while the gradient remains ten times its own
tolerance. In a real training run, watching only "has the loss stopped
moving" can end a run early on a landscape with a long, gently sloped
approach, which is a lost-compute problem rather than a security one, but
the shape of the mistake — trusting one aggregate number instead of
checking the thing you actually care about — is the same shape as several
real security mistakes.

## What this lab deliberately does not claim

`scipy.optimize.minimize`, `torch.optim.SGD` and `jax.grad` with `optax`
are not installed here, and **no output from any of them is reproduced
anywhere** in this lab or its lesson. They are described from their
documentation and marked as not run here. The loop this lab builds by
hand, `x <- x - lr * grad(x)`, is the same update every one of those
tools performs underneath — but "the same update" is a claim about
design, and "here is what it printed" is a claim about a measurement, and
this lab only makes the first one for those three tools.
