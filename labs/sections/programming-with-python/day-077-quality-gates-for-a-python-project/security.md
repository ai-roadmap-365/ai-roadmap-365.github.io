# Security notes — Day 077 lab

## What this lab runs

Five free, open-source Python packages, pinned to exact versions in
`requirements/requirements.txt`, installed into a virtual environment you
create and can delete. After the install, everything runs offline: the gate
reads your files, runs your tests, and writes a coverage data file. Nothing
opens a socket, nothing needs a credential, and nothing requires `sudo`.

## Pinned versions are a security control, not just a stability one

`ruff==0.15.22` rather than `ruff` is what stops your build from silently
executing a different piece of software tomorrow than it executed today.
Unpinned dependencies mean the code that judges your code can change without
anyone reviewing the change — and a compromised or simply careless release of
a build tool runs with your permissions, on your files, on every machine that
runs the gate. Pinning turns "upgrade" into a commit somebody reads.

The same argument applies with more force in continuous integration, where the
gate runs automatically on a machine you cannot see. Pin the tools, pin the
actions the workflow uses, and treat a version bump as a change like any other.

## A gate is not a security scanner

Be precise about what today's five stages prove:

| Stage | What it can prove | What it cannot |
| --- | --- | --- |
| format | the layout matches the agreed style | nothing about behaviour |
| lint | a rule from a fixed list was violated | that the code is safe or correct |
| types | the annotations are internally consistent | that the values arriving at runtime match them |
| tests | the cases you wrote behave as you asserted | anything about the cases you did not write |
| coverage | which lines and branches executed | that anything was verified |

None of them is a security review, a dependency-vulnerability scan, or a
secrets scan. Those are separate stages you can add to the same `check.sh` —
and the lesson's Alternatives section names the hosted dashboards that
specialise in them. What a gate gives you is the place to put such a check so
that it actually runs.

## Continuous integration runs your code on someone else's machine

The workflow in `examples/ci-reference/quality-gate.yml` is shipped as a
documented reference and is not executed by this lab. If you adopt it, three
things are worth knowing before you do:

- **The runner executes whatever the repository says.** A workflow triggered by
  a pull request from a fork is running a stranger's configuration. Hosting
  services default to restricting what such runs can access; do not loosen
  that without understanding why it was tight.
- **Secrets belong in the hosting service's secret store, never in the
  workflow file, never in `pyproject.toml`, and never in a test fixture.** The
  gate in this lab needs no secrets at all, which is the safest position to be
  in.
- **Artifacts are downloadable.** The reference workflow uploads coverage data.
  Coverage data contains file paths and line numbers from your project; that is
  usually harmless, but treat anything a workflow uploads as published to
  everyone who can read the repository.

## The lab's own test suite

`tests/run_tests.sh` copies the reference project into directories made with
`mktemp -d`, introduces a defect there, and deletes the directory afterwards.
It never modifies `examples/` or `starter/`, never writes outside the
temporary directories and the lab directory, and never uses a wildcard in a
delete. Read it before you run it — that is a reasonable habit for any script
that removes directories, and this one is short enough to read in full.

## Personal data

None. `pricekit` computes prices from numbers you type into a test file. The
coverage data file (`.coverage`) records paths and line numbers from your own
project and nothing else; the cleanup command removes it.

## Cleanup

```bash
rm -f .coverage
rm -rf .mypy_cache .ruff_cache .pytest_cache
rm -rf .venv          # only if you want the tools gone as well
```
