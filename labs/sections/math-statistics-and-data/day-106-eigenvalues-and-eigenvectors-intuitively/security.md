# Security notes — Day 106 lab

What this lab touches, and what it deliberately does not.

## Network

**Once, to install two packages.** That is the entire network footprint.

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

That reaches the Python Package Index for `numpy==2.5.2` and `pytest==9.1.1`,
both pinned to an exact version so you get the same artifacts that were tested
here. After that command finishes, **nothing in this lab opens a socket**.

Section 7 of `tests/run_tests.sh` checks that claim rather than making it:

```bash
grep -rqE 'urlopen|requests\.|socket\.|http://|https://' examples/ starter/
```

If any lab source ever grows a network call, that check goes red.

The 400-point dataset is **generated in code** from
`numpy.random.default_rng(2106)`, not downloaded. That was a deliberate choice.
A lab that fetches a dataset is a lab that breaks on a train, ships a file whose
licence someone has to check, and hides its own test data behind a URL that will
eventually rot. Section 7 also asserts that no `.csv`, `.npy`, `.npz`, `.json`,
`.parquet` or `.pkl` file exists anywhere in the lab's own tree.

## Credentials

None. No API key, no token, no account, no signup, no login, no environment
variable holding a secret. There is nothing in this lab that could leak a
credential, because there is no credential.

If a future extension of this work does need one, the rule from Day 43 still
applies: it goes in the environment, never in a file, and never in a commit.

## Privileges

**No `sudo`, ever.** Every command in this lab runs as your ordinary user.

`python3 -m venv .venv` creates a directory inside the lab. `pip install` writes
only inside that directory. If any instruction here appears to need
administrator rights, something is wrong — check `troubleshooting.md` rather
than escalating privileges.

## Filesystem

Everything this lab writes stays inside its own directory:

| Path | Written by | Removed by |
| --- | --- | --- |
| `.venv/` | `python3 -m venv` | `rm -rf .venv` |
| `__pycache__/` | Python, if bytecode writing is enabled | the cleanup command |
| `.pytest_cache/` | pytest, if `-p no:cacheprovider` is omitted | `rm -rf .pytest_cache` |
| `starter/eigen.py`, `starter/answers.py` | **you** | `git checkout -- starter/` |

Nothing is written to your home directory, to `/tmp`, or anywhere else on the
system. No lab script opens a file for writing at all — the reference scripts
print to standard output and nothing more. The harness exports
`PYTHONDONTWRITEBYTECODE=1` so that in practice even `__pycache__` does not
appear.

Nothing binds a port. Nothing starts a background process. Nothing reads a file
outside the lab directory.

## Personal data

None is processed, because none exists here.

The only dataset is 400 points drawn from a seeded pseudo-random normal
distribution and shifted to a made-up centre. It describes nothing and nobody.
There is no scraping, no logging, no telemetry, and nothing that leaves your
machine.

That is worth noticing precisely *because* of what the lab teaches. PCA on a
covariance matrix is a real technique applied to real data, and the moment you
point exercise 5's fifteen lines at a table of actual observations — the
extension exercise invites you to — the ordinary obligations arrive with it.
Two are worth stating now rather than later:

- **A principal component is a linear combination of your columns.** If one of
  those columns is a protected or sensitive attribute, the top component can
  carry it even after you drop the column itself, because a correlated column
  reconstructs it. Reducing dimensions does not anonymise anything.
- **Eigenvalues are computed on the whole matrix at once.** Every row
  contributes to the answer, so a covariance matrix derived from personal
  records is itself derived personal data and inherits whatever handling rules
  the records had.

Neither of those is a concern in *this* lab. Both become one the first time you
use what it teaches.

## Supply chain

Two dependencies, both pinned exactly, both long-established and widely audited:

| Package | Version | Licence | Maintenance |
| --- | --- | --- | --- |
| numpy | 2.5.2 | BSD 3-Clause | NumPy developers, in the open |
| pytest | 9.1.1 | MIT | pytest-dev, in the open |

Pinning is a security property as well as a reproducibility one: the version you
install is the version that was tested, and an unexpected upgrade is visible
rather than silent. Section 1 of the harness compares the installed versions
against `requirements/requirements.txt` and reports a mismatch at the top of the
run.

Both licences are permissive, cost nothing, and require no account for personal
or commercial use.

## Untrusted input

There is none. Every matrix in this lab is a literal written into
`dataset.py`, and the cloud is generated from a fixed seed. No lab code parses a
file, deserialises anything, evaluates a string, or accepts input from outside
the process.

`eval`, `exec`, `pickle.load` and `numpy.load` with `allow_pickle=True` appear
nowhere in this lab. That last one is worth knowing about even though it is
absent here: loading a `.npy` file with pickling enabled executes arbitrary code
from that file, so it is never the right default for a file you did not write
yourself.

## What could still go wrong, honestly

The realistic risks in this lab are correctness risks, not security ones, and
the lab is built around surfacing them:

- `numpy.linalg.eigh` on a non-symmetric matrix returns a confident wrong answer
  with **no error and no warning**. It reads one triangle and assumes the other
  matches.
- `numpy.linalg.inv` on the shear's singular eigenvector matrix does **not**
  raise. It returns entries around `4.5e15` and a reconstruction that is clean,
  plausible and completely wrong.
- Forgetting to centre before computing a covariance gives an answer
  `136.583965` degrees wrong, again with no error.

Each of those is a silent failure, each is demonstrated with real numbers in
`examples/`, and each is asserted in `tests/run_tests.sh`. Silent wrong answers
are the failure mode this lab spends most of its effort on, because they are the
ones that survive into production.
