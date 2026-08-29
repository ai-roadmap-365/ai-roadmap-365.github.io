# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory, plus
  scikit-learn's own bundled `load_diabetes` dataset, which ships inside
  the installed `scikit-learn` package and is never fetched or written
  anywhere. The one write outside this directory is check 7 of the
  harness, which creates a scratch directory with `mktemp -d` under
  `$TMPDIR`, copies `examples/*.py` into it, deliberately breaks one
  assertion to prove the harness can fail, and removes the directory again
  in the same run. Nothing is written to your home directory, nothing
  above the lab root is modified, and no system path is touched.
- **Network.** After the one `pip install`, this lab is completely
  offline. Check 9 asserts that no URL appears anywhere in `examples/` or
  `starter/` source. `load_diabetes` is bundled data inside the
  scikit-learn package itself, not a download.
- **Credentials.** There are none. `requires_api_key` is `false`, no
  account is needed, and nothing in this lab reads an environment variable
  that could hold a secret.
- **Privileges.** Nothing here needs `sudo`. If a step appears to ask for
  administrator rights, stop and re-read it -- it is not this lab.
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

## The security-adjacent idea in this lab

`check_estimator`'s two named failures are worth reading as a class of bug
rather than only as a scikit-learn compatibility gap.

`check_dtype_object` fails because `OLSRegressor.fit()` does not reject a
`y` array whose dtype is `object` with a clear message -- it lets whatever
NumPy does with mixed types propagate instead. In a production system, an
estimator that silently accepts malformed input rather than failing loudly
at the boundary is the same category of problem as a web form that accepts
a string where it expected a number: the failure moves downstream, gets
harder to diagnose, and can corrupt something before anyone notices.

`check_n_features_in_after_fitting` fails because `predict()` does not
confirm that a new `X` has the same number of columns the model was fitted
on. Handed a wrong-shaped array, this `OLSRegressor` will either raise a
generic NumPy shape-mismatch error deep inside a matrix multiply, or --
worse, if the shapes happen to broadcast -- silently produce a number
instead of an error. `sklearn.utils.validation.check_array`'s `reset=False`
and `n_features_in_` machinery exists specifically to turn that into a
clear, immediate failure, and the honest reading of this lab's result is
that skipping it is not a cosmetic omission.

Both gaps are recorded rather than fixed here, because the point of this
lab is to measure what a from-scratch implementation does and does not do,
not to reproduce scikit-learn's own validation layer line by line.

## What the code does that is worth understanding

- Every dataset generator takes a seed and returns fresh arrays. Nothing is
  cached to disk, nothing is memoised across runs, and no global state
  carries between calls.
- Nothing in this lab evaluates a string, imports dynamically, reads a path
  from data, or inspects the environment.
- The harness captures the exit status of `run_tests.sh` itself and never
  reads the status of a pipeline. `cmd | tail` reports `tail`'s status,
  which is almost always zero -- an always-passing test suite is a security
  control that has quietly stopped working.

## Reporting a problem

If you find something in this lab that writes outside its own directory,
reaches a network it did not start, or asks for a credential, that is a
bug. Nothing here is supposed to do any of those things.
