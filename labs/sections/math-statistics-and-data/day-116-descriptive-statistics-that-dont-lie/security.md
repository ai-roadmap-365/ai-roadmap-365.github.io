# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection
after the one-time `pip install`, needs no credentials, no `sudo` and no
elevated permissions, and touches nothing outside its own directory. Every
number it works with is invented or, for Anscombe's quartet, a published
dataset reproduced exactly and cited: the salary list, the population
parameters for the Bessel simulation, the contamination values, and the
Simpson's-paradox subgroup counts are all written out in
`examples/dataset.py`.

Section 5 of `tests/run_tests.sh` greps every source file in `examples/`
and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
`https://` and fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory,
so nothing installed here can affect the rest of your machine, and `rm -rf
.venv` is a complete undo. The two packages are pinned to exact versions in
`requirements/requirements.txt`, and section 1 of the harness reads the
installed version back and compares it against that file rather than
trusting that the install did what it said.

Pinning is a security property as much as a reproducibility one: an
unpinned `numpy` in a lab that a few thousand people will run is an
invitation you did not mean to send.

## Three things worth carrying away from this particular day

**A summary statistic is a claim about what the data was safe to compress
away, and every one of them is wrong for some dataset.** The mean is wrong
for skewed distributions and for any dataset with even one corrupted value.
The standard deviation is wrong under contamination in exactly the way
exercise 8 measures. Reporting a single number without saying *which*
summary it is and what it discards is a form of overclaiming — the same
overclaiming this lab's whole design argues against.

**Reported percentiles are not directly comparable across tools without
knowing the convention.** A dashboard built on `pandas.DataFrame.describe()`
and a script built on raw `numpy.percentile()` with a non-default `method=`
can report two different, both-correct 75th percentiles for the same data.
In any system where a percentile crosses a decision boundary — an SLA
threshold, a fraud-detection cutoff, a performance budget — that ambiguity
is a real operational risk, not a rounding curiosity.

**Subgroup breakdowns are not optional when a decision rides on an
aggregate.** Simpson's paradox is not a rare edge case invented for
textbooks; it is the generic behaviour of any weighted average when the
weights are unequal and correlated with the outcome. A model-evaluation
pipeline, an A/B test dashboard, or a hiring-funnel report that only
publishes the aggregate number can be hiding a subgroup where the true
picture is the opposite of the headline — and nothing about a
correctly-computed aggregate signals that it might be hiding one.

## What this lab deliberately does not claim

`scipy.stats` and `pandas` are not installed here and **no output from
either is reproduced anywhere** in this lab or its lesson. Both are
described from their public documentation in the lesson's Tools section
and marked as not run here.

Anscombe's quartet (exercise 6) is the published 1973 dataset reproduced
exactly, not data generated for this lab: Anscombe, F. J. (1973). "Graphs
in Statistical Analysis." The American Statistician, 27(1), 17-21. The
Simpson's-paradox table (exercise 7) is an invented illustrative example,
not a claim about any real treatment, dataset or study — its numbers are
chosen to be the smallest integers that demonstrate the mechanism clearly,
and the lesson and this file say so plainly rather than implying it is real
clinical data.
