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

The `GatedTestSet` in exercise 7 is worth reading as an access-control
pattern rather than only as a teaching device.

It holds data, permits exactly one read, counts the reads, and refuses the
second with a message explaining what the refused answer would actually
have been. That is a budget enforced by the resource itself rather than by
the good intentions of whoever holds it — the same shape as a one-time
token, a single-use signed URL, or a rate limiter.

The design detail worth copying is that **the counter does not advance on
a refused attempt**. A gate whose refusals consume budget can be drained
by an attacker who never succeeds at anything, and the lab asserts the
correct behaviour explicitly.

The wider point connects to the whole lesson. A test set is a
non-renewable resource: its value comes entirely from never having
influenced anything. Every look spends some of it, and the spending is
invisible in the result — which is exactly the property that makes it a
control worth enforcing mechanically.

## What the code does that is worth understanding

- Every dataset generator takes a seed and returns fresh arrays. Nothing
  is cached to disk, nothing is memoised across runs, and no global state
  carries between tests.
- `GatedTestSet` holds no class-level state, so two gates are two
  independent budgets. The machinery test asserts this, because a gate
  that leaked state between instances would be a subtle and serious bug.
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
