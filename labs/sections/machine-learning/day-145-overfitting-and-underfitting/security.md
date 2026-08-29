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
  is bundled.
- **Credentials.** There are none. `requires_api_key` is `false`, no
  account is needed, and nothing in this lab reads an environment variable
  that could hold a secret.
- **Privileges.** Nothing here needs `sudo`. If a step appears to ask for
  administrator rights, stop and re-read it — it is not this lab.
- **Reversibility.** Everything this lab creates is inside its own
  directory. `rm -rf .venv` returns the machine to exactly its prior
  state.
- **Compute.** CPU only. No GPU is used or required, and nothing here will
  saturate a machine — the heaviest step is a few thousand small
  least-squares solves.

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

Overfitting is a privacy problem, and this lab is where that becomes
concrete rather than abstract.

A high-variance model has, in a literal sense, stored particulars of its
training rows — that is what variance *is*. The predictions move because
the model is reproducing detail specific to the rows it happened to see.
That is precisely the property membership-inference attacks exploit: given
a candidate record, ask whether the model behaves as though it has seen
it before.

The measurement in exercise 2 is therefore also a privacy measurement. A
ridge penalty of 1.0 cut this model's variance enough to improve test
error by a factor of 39,588, and the same penalty reduces how much of any
individual training row the model has retained.

**This is one of the few places where the accuracy fix and the privacy fix
are the same fix**, which is worth knowing because it makes the argument
for regularisation much easier to win. It also means the reverse holds: a
team that tunes for training error is switching off a privacy control
without noticing, since every intervention here makes training error
worse on purpose.

## What the code does that is worth understanding

- Every dataset generator takes a seed and returns fresh arrays. Nothing
  is cached to disk, nothing is memoised across runs, and no global state
  carries between tests.
- `polynomial_model` places a `StandardScaler` between the polynomial
  features and the estimator. That is not decoration: without it, raw
  features up to degree 24 span many orders of magnitude and the normal
  equations become numerically hopeless. A machinery test asserts the
  scaled pipeline fits better than the unscaled one.
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
