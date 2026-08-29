# Security notes

## What this lab does

It computes and prints. It writes no files, opens no network connection
after the one-time `pip install`, needs no credentials, no `sudo` and no
elevated permissions, and touches nothing outside its own directory. Every
population, seed, sample size and tolerance is invented and is written out
in `examples/dataset.py`.

Section 6 of `tests/run_tests.sh` greps every source file in `examples/`
and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
`https://` and fails if any of them appears.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory,
so nothing installed here can affect the rest of your machine, and
`rm -rf .venv` is a complete undo. The two packages are pinned to exact
versions in `requirements/requirements.txt`, and section 1 of the harness
reads the installed version back and compares it against that file rather
than trusting that the install did what it said.

## Three things worth carrying away from this particular day

**A spread measure computed on the wrong kind of data can be a plausible
number attached to nothing real.** A standard deviation computed on a
sample from the Cauchy distribution looks like an ordinary float -- it
prints, it has units, it is not `nan` or `inf` -- and it estimates nothing,
because the population variance it would be estimating does not exist. The
lab's fix is exercise 4's choice of the interquartile range instead, which
depends only on the order of the data. If you ever compute a "confidence
interval" or "error bar" on a metric with a genuinely heavy tail --
latency percentiles under contention, financial returns, retry counts under
a cascading failure -- ask whether the underlying quantity has a finite
variance before trusting a standard-deviation-based error bar on it.

**A naive standard error fails silently, and it fails in the dangerous
direction.** Exercise 7 measures a case where `sample_std / sqrt(n)`
understates the true standard error of a dependent series by more than a
factor of two. It does not raise, does not warn, and produces a number of
entirely plausible size -- the failure is invisible until you compare it
against a measurement that does not share its independence assumption.
Time-series metrics, session-level telemetry, and anything sampled from a
system with momentum (a queue, a cache, a slowly drifting user population)
are exactly the settings where this understatement shows up in production
dashboards as false confidence.

**Sampling bias produces a more precise wrong answer as you add more
data, and there is no purely statistical test that can catch it from the
sample alone.** Exercise 5's biased sampler -- one that can only see the
upper half of the population -- becomes more confident in its (wrong)
estimate as `n` grows, exactly as fast as an unbiased sampler becomes more
confident in the (right) one. The standard error, the confidence interval,
and every quantity this lab computes describe the sampling *error*, not
the sampling *frame*. Whether the frame reaches the population you actually
care about is a question about how the data was collected, and no amount
of additional data collected the same way answers it.

## What this lab deliberately does not claim

`scipy.stats` and `pandas` are not installed here and **no output from
either is reproduced anywhere** in this lab or its lesson. `scipy.stats`
is described from its public documentation, including its `bootstrap` and
`sem` functions, and marked as not run here. The bootstrap you build in
`starter/sampling.py` implements the same idea `scipy.stats.bootstrap`
does -- resample, recompute, read off the spread -- and differs from it in
engineering (confidence-interval methods, vectorisation, bias correction
options), not in the core idea.
