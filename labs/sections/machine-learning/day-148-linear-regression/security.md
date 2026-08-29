# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory (and
  the diabetes dataset bundled inside your installed scikit-learn
  package). The one write outside it is check 6 of the harness, which
  creates a scratch directory with `mktemp -d` under `$TMPDIR`, copies
  `examples/*.py` into it, deliberately breaks one assertion to prove the
  harness can fail, and removes the directory again in the same run.
  Nothing is written to your home directory, nothing above the lab root is
  modified, and no system path is touched.
- **Network.** After the one `pip install`, this lab is completely
  offline. Check 8 asserts that no URL appears anywhere in `examples/` or
  `starter/` source. `sklearn.datasets.load_diabetes` reads a file shipped
  inside the installed `scikit-learn` package; it does not download
  anything. Every other dataset here is generated on the spot from a
  seeded `numpy.random.default_rng`.
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

## The idea worth carrying past this lab

Exercise 5's leverage point is the security-relevant idea here, even
though this is a statistics lab and not a security one: **a fitted model
can be moved a long way by a single unusual input, and the amount of
movement is computable from that input's position alone, before you even
look at its label.** That is the same shape as an outlier-injection or
data-poisoning concern in a larger pipeline — one crafted row, far from
the bulk of the training data, can dominate a fit that a thousand ordinary
rows barely influence. The defence in this lab is diagnostic (compute the
leverage, plot the residuals); a production pipeline typically adds a
second line of defence, such as capping influence with a robust
estimator, which this course covers when it revisits loss functions.

## What the code does that is worth understanding

- Every synthetic dataset generator takes a seed and returns fresh arrays.
  Nothing is cached to disk, nothing is memoised across runs, and no
  global state carries between tests.
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
