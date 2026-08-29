# Security notes

## What this lab touches

Nothing outside its own directory, and nothing outside your machine.

- **Filesystem.** The lab reads only files inside its own directory. The
  one write outside it is check 7 of the harness, which creates a scratch
  directory with `mktemp -d` under `$TMPDIR`, copies `examples/*.py` into
  it, deliberately breaks one assertion to prove the harness can fail, and
  removes the directory again in the same run. Nothing is written to your
  home directory, and nothing above the lab root is modified.
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
for your own platform with `pip-compile --generate-hashes` is a reasonable
habit for any environment you care about.

## The security-relevant idea in this lab

The manifest in exercise 6 is worth reading as a supply-chain control and
not only as a reproducibility one.

`fingerprint()` is a SHA-256 over the raw bytes of an array, including its
dtype. Two runs that produce the same hash produced the same bytes. That
is the same primitive behind package lock files, container digests and
signed release artifacts, and it answers the same question: *is what I have
now the thing I checked before?*

A pipeline that cannot answer that question cannot be audited. If a
regulator, a reviewer or a future colleague asks which data produced a
deployed model, "the notebook I ran in March" is not an answer and a
manifest of content hashes is.

Note also what the fingerprint deliberately includes: `str(value.dtype)`.
The same numbers stored as `int64` and as `float64` hash differently, on
purpose. Treating them as the same artifact would hide a real class of
bug, and silently equal hashes are worse than no hashes at all.

## What the code does that is worth understanding

- `Artifact.with_()` returns a new artifact rather than mutating in place.
  A stage that mutates its input makes the step log a work of fiction,
  because the log then describes states that no longer exist — and an
  audit trail that can be rewritten by the thing it audits is not an audit
  trail.
- `run_pipeline` checks contracts in **both** directions: a stage that
  fails to produce what it declared, and a stage that produces something
  extra, both raise. The second is easy to dismiss and worth keeping —
  undeclared outputs are how a pipeline accumulates hidden coupling.
- Nothing in this lab evaluates a string, imports dynamically, or reads a
  path from data. `inspect.getsource` in `stage_source_lines` reads the
  source of functions defined in this package and nothing else.
- The harness captures the exit status of `run_tests.sh` itself and never
  reads the status of a pipeline. `cmd | tail` reports `tail`'s status,
  which is almost always zero — an always-passing test suite is a security
  control that has quietly stopped working.

## Reporting a problem

If you find something in this lab that writes outside its own directory,
reaches a network it did not start, or asks for a credential, that is a
bug. Nothing here is supposed to do any of those things.
