# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory, plus
  the diabetes dataset that ships bundled inside scikit-learn's own
  installed package files -- nothing is read from your home directory or
  from anywhere above the lab root. The one write outside the lab
  directory is check 7 of the harness, which creates a scratch directory
  with `mktemp -d` under `$TMPDIR`, copies `examples/*.py` into it,
  deliberately breaks one assertion to prove the harness can fail, and
  removes the directory again in the same run.
- **Network.** After the one `pip install`, this lab is completely
  offline. Check 9 asserts that no URL appears anywhere in `examples/` or
  `starter/` source. `load_diabetes` returns an array bundled inside the
  scikit-learn wheel; nothing is downloaded and no external dataset file
  is fetched.
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

## The security idea in this lab

`r2_score`'s argument-order bug in exercise 8b is worth reading as a
general lesson about function contracts rather than only as a metrics
quirk.

`r2_score(y_true, y_pred)` and `r2_score(y_pred, y_true)` are two different,
silently-accepted calls that return two different numbers, and nothing in
the type system or the function signature stops you from writing the
wrong one. This is the same shape as a security bug caused by swapped
arguments to a comparison function, a signature-verification call, or an
access-control check that takes `(subject, resource)` and is called as
`(resource, subject)`: the call succeeds, returns a plausible-looking
value, and the mistake surfaces only when someone checks the number against
an independent source of truth. The defence in both cases is the same --
prefer keyword arguments for anything where the order is not obvious from
context, and cross-check a computed value against a second method
(`r2_score(y_test, pred)` against `model.score(X_test, y_test)`, in this
lab) rather than trusting a single call site.

## What the code does that is worth understanding

- Every dataset and every synthetic example takes a seed (or uses the
  bundled, unchanging diabetes data) and returns fresh arrays. Nothing is
  cached to disk, nothing is memoised across runs, and no global state
  carries between calls.
- Nothing in this lab evaluates a string, imports dynamically, reads a
  path from data, or inspects the environment.
- The harness captures the exit status of `run_tests.sh` itself and never
  reads the status of a pipeline. `cmd | tail` reports `tail`'s status,
  which is almost always zero -- an always-passing test suite is a security
  control that has quietly stopped working.

## Reporting a problem

If you find something in this lab that writes outside its own directory,
reaches a network it did not start, or asks for a credential, that is a
bug. Nothing here is supposed to do any of those things.
