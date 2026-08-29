# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory, plus
  the diabetes dataset that scikit-learn bundles inside its own installed
  package (`sklearn/datasets/data/diabetes_*.csv.gz`) — that file is read
  from local disk, never fetched over the network. The one write outside
  this directory is check 7 of the harness, which creates a scratch
  directory with `mktemp -d` under `$TMPDIR`, copies `examples/*.py` into
  it, deliberately breaks one assertion to prove the harness can fail, and
  removes the directory again in the same run. Nothing is written to your
  home directory, nothing above the lab root is modified, and no system
  path is touched.
- **Network.** After the one `pip install`, this lab is completely
  offline. Check 9 asserts that no URL appears anywhere in `examples/` or
  `starter/` source. Every synthetic dataset is generated on the spot from
  a seeded `numpy.random.default_rng` or `sklearn.datasets.make_regression`;
  the one real dataset, `load_diabetes`, ships bundled inside the
  scikit-learn wheel.
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

```
.venv/bin/pip install --require-hashes -r requirements/requirements.txt
```

That requires a hash-annotated requirements file, which this lab does not
ship because the correct hashes differ per platform wheel. Generating one
for your own platform with `pip-compile --generate-hashes` is a reasonable
habit for any environment you care about.

## The security idea in this lab

Regularization itself is worth reading as a control on a model's
trustworthiness in production, not only as a statistics topic.

A model with 10 nonzero coefficients over unscaled inputs has an attack
surface: whichever raw feature happens to arrive in large natural units
(a count in the thousands rather than a fraction between 0 and 1) can
dominate the fit regardless of whether it actually carries signal, purely
because the penalty — or the absence of one — treats it as "big" or
"small" in the wrong units. Exercise 4 in this lab measures that failure
directly: the identical alpha, in three different units, selects 10, 7
and 3 features. A pipeline that fits a penalised model on unscaled inputs
without noticing has not actually regularised anything meaningful.

Sparsity is also an auditability property. A model with 3 nonzero
coefficients is far easier to review, explain, and monitor for drift than
one with 10 small nonzero coefficients that are individually
unremarkable and collectively opaque. Exercise 3 measures that lasso can
recover the RIGHT sparse set, which is what makes that auditability claim
trustworthy rather than accidental — and exercise 3b measures that it can
also fail to, which is why "the model is sparse" is not by itself
evidence that the model found the truth.

## What the code does that is worth understanding

- Every dataset generator either bundles data read-only from the
  scikit-learn package or takes a seed and returns fresh arrays. Nothing
  is cached to disk, nothing is memoised across runs, and no global state
  carries between tests.
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
