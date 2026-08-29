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

**A p-value answers a narrower question than the one most people act on.**
It is P(data at least this extreme | the null hypothesis is true) -- not
P(the null hypothesis is true | this data), and not P(the effect is real).
Treating a p-value as the second or third of those is Day 115's base-rate
error wearing different clothes: it discards the prior (how plausible was
the effect before you looked?) exactly the way ignoring a low base rate
does with a diagnostic test. Anywhere a p-value drives a real decision --
shipping a feature, flagging fraud, approving a model change -- that
inversion is worth naming out loud before the number gets used.

**Peeking is not a hypothetical failure mode; it is the default behavior
of a dashboard that updates live.** Exercise 8 measures a roughly 3-4x
inflation in the false-positive rate from checking a fixed test after
every 10 observations and stopping at the first significant result, under
a null hypothesis that never changed. Any monitoring system, A/B-test
dashboard, or alerting rule that a human watches and reacts to as new data
streams in is running exactly this procedure unless it was explicitly
built as a sequential test (which controls the error rate under repeated
looking) or the sample size and decision rule were fixed in advance and
followed regardless of what the running p-value said along the way.

**Multiple comparisons are not a sign of cheating -- they are what "found
something" looks like by default when many things are checked.** Exercise
5's 64% chance of at least one false positive among twenty independent
alpha=0.05 tests requires no bad intent from anyone: it is the same
correctly-computed 5% risk taken twenty separate times. A pipeline that
automatically checks dozens of metrics and flags "significant" changes
needs a family-wise correction (Bonferroni, or a less conservative
alternative) built in from the start, not as a post-hoc fix once someone
notices the flag rate looks suspiciously high.

## What this lab deliberately does not claim

`scipy.stats` and `statsmodels` are not installed here and **no output
from either is reproduced anywhere** in this lab or its lesson. Both are
described from their public documentation in the lesson's Tools section
and marked as not run here. `inference.py`'s `two_sample_z_test` and
`confidence_interval_mean` implement the same underlying ideas
`scipy.stats.ttest_ind` and `scipy.stats.norm.interval` do -- the
difference is engineering (a t-reference distribution for small samples,
several named alternative hypotheses, vectorised batch operation, a stable
public API), not the core idea.
