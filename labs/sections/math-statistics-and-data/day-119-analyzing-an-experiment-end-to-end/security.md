# Security notes

## What this lab does

It reads two CSV files, computes, and prints. It writes no files outside
its own directory (except the reference suite's use of pytest's `tmp_path`
fixture for one deliberately-broken CSV, which pytest cleans up itself),
opens no network connection after the one-time `pip install`, needs no
credentials, no `sudo` and no elevated permissions.

Section 7 of `tests/run_tests.sh` greps every source file in `examples/`
and `starter/` for `urlopen`, `requests.`, `socket.`, `http://` and
`https://` and fails if any of them appears.

## The data is simulated

`data/exp_a.csv` and `data/exp_b.csv` contain **no real user data of any
kind**. Every row -- the `user_id`, the `group`, the `segment`, whether the
simulated visitor converted, their simulated page latency and time on
page -- is drawn from `numpy.random.default_rng` with a fixed seed in
`examples/generate_data.py`. There is no relationship between these
numbers and any real product, company, or person. Regenerating the CSVs
from that script reproduces them exactly.

## The virtual environment

`python3 -m venv .venv` creates the environment inside the lab directory,
so nothing installed here can affect the rest of your machine, and
`rm -rf .venv` is a complete undo. The two packages are pinned to exact
versions in `requirements/requirements.txt`, and section 1 of the harness
reads the installed version back and compares it against that file rather
than trusting that the install did what it said.

## Three things worth carrying away from this particular day

**Randomization you cannot verify is a security-shaped problem, not just a
statistics one.** Dataset B's sample-ratio mismatch means someone (or
something -- a caching layer, a bot filter, a load balancer's routing
rule) assigned users to groups in a way that was not actually the coin
flip the plan assumed. In production this is frequently caused by an
implementation bug that correlates assignment with something real: users
on a slower connection retrying and getting reassigned, a caching layer
serving stale bucket assignments to one arm more than the other, or a
targeting rule leaking into what was meant to be a clean random split. The
SRM check does not diagnose the cause -- it only proves something is
wrong before you act on numbers that assume nothing is.

**A verdict function that can be silently overridden defeats the entire
pipeline.** `verdict()` in this lab refuses to compute an estimate at all
once the SRM check has failed, and deliberately does not accept a
`force=True` escape hatch. If you extend this lab, resist adding one --
the entire value of a refusal is that nobody downstream can quietly turn
it into a number by passing a flag under deadline pressure.

**A guardrail metric that can be silently dropped from the analysis
defeats it just as completely.** Nothing in `verdict()` computes "ship"
without also having a guardrail result to check. If a future guardrail
metric is added to this pipeline and a caller forgets to pass it, the
correct failure mode is an exception, not a verdict that quietly ships
with one fewer check than the plan called for.

## What this lab deliberately does not claim

`scipy.stats` and `statsmodels` are not installed here and **no output
from either is reproduced anywhere** in this lab or its lesson. Both are
described from their public documentation. Every test statistic, p-value,
confidence interval and chi-squared calculation in this lab is computed
from `math.erf`/`math.erfc` and the standard library, exactly as Day 118
built its own tests -- there is no `scipy.stats.ttest_ind` or
`statsmodels.stats.proportion` call anywhere in `examples/` or `starter/`.
