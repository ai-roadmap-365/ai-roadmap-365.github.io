# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory. The
  one write outside it is check 7 of the harness, which creates a scratch
  directory with `mktemp -d` under `$TMPDIR`, copies `examples/*.py` into
  it, deliberately breaks one assertion to prove the harness can fail, and
  removes the directory again in the same run. Nothing is written to your
  home directory, nothing above the lab root is modified, and no system
  path is touched.
- **Network.** After the one `pip install`, this lab is completely
  offline. Check 9 asserts that no URL appears anywhere in `examples/` or
  `starter/` source. Every dataset here is generated on the spot from a
  seeded `numpy.random.default_rng`; nothing is downloaded and no dataset
  is bundled. (This day does not use `sklearn.datasets.load_diabetes` or
  any bundled dataset — every example here is a synthetic straight line
  with known truth, which is what lets the lab inject an exact outlier and
  measure exactly what each loss does about it.)
- **Credentials.** There are none. `requires_api_key` is `false`, no
  account is needed, and nothing in this lab reads an environment variable
  that could hold a secret.
- **Privileges.** Nothing here needs `sudo`. If a step appears to ask for
  administrator rights, stop and re-read it — it is not this lab.
- **Reversibility.** Everything this lab creates is inside its own
  directory and is removed by the cleanup commands in `metadata.yml`.
  `rm -rf .venv` returns the machine to exactly its prior state.

## The one install step, and how to check it

`pip install -r requirements/requirements.txt` downloads three packages
from the Python Package Index into a **lab-local** virtual environment,
never into your system Python. Pinning exact versions is a security
control as well as a reproducibility one: an unpinned install resolves to
whatever is newest at the moment you run it, which is a moving target you
have not reviewed.

If you want to verify what you are installing before you install it, pip
can check hashes for you:

```bash
.venv/bin/pip install --require-hashes -r requirements/requirements.txt
```

That requires a hash-annotated requirements file, which this lab does not
ship because the correct hashes differ per platform wheel. Generating one
for your own platform with `pip-compile --generate-hashes` is a reasonable
habit for any environment you care about.

## The idea in this lab worth reading as a security idea

A loss function decides, silently, how much weight one extreme data point
gets relative to everything else. Squared error gives an 80-unit residual
6,400 times the weight of a 1-unit residual; absolute error gives it only
80 times the weight. That is not only a statistics fact — it is the same
shape as a system that lets one anomalous input dominate a decision simply
because nobody chose to bound its influence. A model trained with plain
squared-error loss on data an attacker can partially influence (a
recommendation signal, a price feed, a user-submitted rating) inherits
that same unbounded sensitivity: one adversarially large value can move
the fitted line far more than its single vote should buy it. `Huber` and
`QuantileRegressor` are, among other things, ways of putting an explicit
ceiling on how much any one point can buy — worth remembering the next
time "just use least squares" is the whole plan for a pipeline that
ingests data you do not fully control.

## What the code does that is worth understanding

- Every dataset generator (`make_line_data`) takes a seed and returns
  fresh arrays. Nothing is cached to disk, nothing is memoised across
  runs, and no global state carries between tests.
- Nothing in this lab evaluates a string, imports dynamically, reads a
  path from data, or inspects the environment.
- The harness captures the exit status of `run_tests.sh` itself and never
  reads the status of a pipeline. `cmd | tail` reports `tail`'s status,
  which is almost always zero — an always-passing test suite is a security
  control that has quietly stopped working.

## Reporting a problem

If you find something in this lab that writes outside its own directory,
reaches a network it did not start, or asks for a credential, that is a
bug. Nothing here is supposed to do any of those things.
