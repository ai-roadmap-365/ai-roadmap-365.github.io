# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory. The
  one write outside it is check 7 of the harness, which creates a scratch
  directory with `mktemp -d` under `$TMPDIR`, copies `examples/*.py` into
  it, deliberately breaks one assertion to prove the harness can fail,
  and removes the directory again in the same run. Nothing is written to
  your home directory, and nothing above the lab root is modified.
- **Network.** After the one `pip install`, this lab is completely
  offline. Check 9 asserts that no URL appears anywhere in `examples/` or
  `starter/` source. The iris measurements come from a copy bundled
  inside the installed scikit-learn package; every other dataset is
  generated on the spot from a seeded `numpy.random.default_rng`.
- **Credentials.** There are none. `requires_api_key` is `false`, no
  account is needed, and nothing in this lab reads an environment
  variable that could hold a secret.
- **Privileges.** Nothing here needs `sudo`. If a step appears to ask for
  administrator rights, stop and re-read it — it is not this lab.

## The one install step, and how to check it

`pip install -r requirements/requirements.txt` downloads three packages
from the Python Package Index. Pinning exact versions is a security
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
for your own platform with `pip-compile --generate-hashes` is a
reasonable habit for any environment you care about.

## Running a virtual environment at all

The lab builds a `.venv` inside its own directory rather than installing
into your system Python. That is the security-relevant choice: a
project-local environment cannot break another project, cannot be broken
by one, and can be deleted with a single `rm -rf .venv` if you want the
machine back exactly as it was.

Do not run `pip install` into a system Python as an administrator to make
this lab work. If something fails, the fix is in `troubleshooting.md`,
not in elevated privileges.

## What the code does that is worth understanding

- `q_learning` and `run_bandit` are pure computation over NumPy arrays.
  They evaluate no strings, import nothing dynamically and touch no
  files.
- `classify_problem` deliberately raises `KeyError` on an incomplete
  description rather than filling in a default. A function that quietly
  guesses at a missing input is a small security problem as well as a
  correctness one: the guess is invisible in the output, so nobody
  reviewing the result can see that it happened.
- The harness captures the exit status of `run_tests.sh` itself and never
  reads the status of a pipeline. `cmd | tail` reports `tail`'s status,
  which is almost always zero — an always-passing test suite is a
  security control that has quietly stopped working.

## Reporting a problem

If you find something in this lab that writes outside its own directory,
reaches a network it did not start, or asks for a credential, that is a
bug. Nothing here is supposed to do any of those things.
