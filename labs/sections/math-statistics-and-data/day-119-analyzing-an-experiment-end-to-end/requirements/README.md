# What is installed, why, and what it costs

Two packages, both free and open source, both installed into a lab-local
virtual environment that `rm -rf .venv` completely undoes.

| Package | Version pinned | Licence | What this lab uses it for |
| --- | --- | --- | --- |
| `numpy` | 2.5.2 | BSD 3-Clause | `numpy.random.default_rng` inside `examples/generate_data.py`, to draw the two shipped datasets once, deterministically. Nothing in `experiment.py` itself imports NumPy -- the analysis pipeline is pure standard library. |
| `pytest` | 9.1.1 | MIT | The reference suite (12 tests) and your running score in `starter/`. |

There is no paid tier of anything in this lab, no account, no key and no
signup, personally or commercially.

## The one time the network is needed

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That is the only command in the lab that opens a connection. Section 7 of
`tests/run_tests.sh` greps every source file in `examples/` and `starter/`
to prove that nothing else does.

## What is deliberately *not* installed

**`scipy.stats`** would give you `scipy.stats.ttest_ind` for the primary
test, `scipy.stats.chi2_contingency` for the sample-ratio mismatch check,
and `scipy.stats.norm.interval` for the confidence interval, in a fraction
of the code this lab writes by hand. None of it is installed here, and
**no output from scipy is reproduced anywhere** in this lab or its lesson.
The lesson's Tools section describes it from its public documentation.

That is not a limitation to apologise for. Every test statistic in this
lab is built from `math.erf`/`math.erfc` -- the same normal-CDF machinery
Day 118 built -- so a reader who has worked through this lab can read
`scipy.stats.ttest_ind`'s documentation and know exactly what computation
is hiding behind the function call, because they wrote it themselves once,
here.

**`statsmodels`** offers `statsmodels.stats.proportion.proportions_ztest`
and a purpose-built sample-ratio-mismatch helper in some analytics
libraries built on top of it. It is not installed here either, and is
described from its public documentation in the lesson's Tools section, not
run.

**`pandas`** is also not installed, on purpose, even though it would make
`segment_analysis`'s per-segment grouping a one-line `groupby("segment")`
instead of a manual loop over sorted segment names. The lesson names what
`groupby` would do at the point where this lab writes that loop by hand,
and says plainly that Week 18 teaches pandas properly -- this lab does not
assume it.

**`matplotlib`** is not installed. The two hand-authored SVG diagrams in
the lesson carry the visual argument this lab's numbers would otherwise
need a plot for.

## If you cannot install anything at all

The two shipped CSVs (`data/exp_a.csv`, `data/exp_b.csv`) are already
generated and checked in -- you do not need NumPy to run this lab's
exercises, only to regenerate the data from scratch via
`examples/generate_data.py`, which is optional. Every exercise in
`starter/experiment.py` is pure standard library (`csv`, `math`,
`statistics`), so a bare Python 3.11+ interpreter with no third-party
packages at all can complete exercises 1 and 3-9 by loading the shipped
CSVs directly. `pytest` is convenient for checking your work but not
required -- every numbered script in `examples/` runs standalone with
`python3 <script>.py` and prints "every assertion held" on success.
