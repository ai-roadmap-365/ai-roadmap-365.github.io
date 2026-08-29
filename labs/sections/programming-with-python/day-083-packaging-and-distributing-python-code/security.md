# Security notes — Day 083 lab

## What this lab does and does not do

- **It uploads nothing, anywhere.** No package index is contacted at any point.
  Publishing is described in the lesson, its commands are printed, and the lab
  stops before running them.
- **It fetches nothing.** Every `pip install` here passes `--no-index`, which
  forbids pip from contacting an index even if one is reachable. Builds use
  `--no-isolation`, which reuses the already-installed backend rather than
  downloading one. After the one-time requirements install, this lab is
  entirely offline.
- **It needs no credentials.** There is no token, no password, no account, and
  no configuration file to put one in.
- **It writes only inside `workspace/`** and inside the two project
  directories, and the cleanup commands remove everything it wrote. Nothing is
  installed system-wide and nothing needs `sudo`.

`tests/run_tests.sh` checks the first of those claims mechanically: it reads
`metadata.yml` — the complete list of commands this lab asks anyone to run —
and fails if any publishing command appears there.

## Installing a package runs the publisher's code

This is the single most important security fact in packaging, and it is easy
to forget because installing feels passive.

A wheel is mostly inert: installing one unpacks files and writes a launcher.
An **sdist** is not. Building it can execute the project's own build backend
and, in older projects, a `setup.py` that is arbitrary Python. `pip install
some-package` on a source distribution therefore runs code written by someone
you have never met, with your user's permissions, before you have imported
anything.

Practical consequences:

- Prefer wheels. `pip install --only-binary :all: <name>` refuses to build from
  source at all, which is a reasonable default on a machine that matters.
- Install into a virtual environment, always. This lab's throwaway environment
  is throwaway on purpose: deleting the directory undoes the entire install.
- Read the name you typed. **Typosquatting** — registering a name one keystroke
  away from a popular package — is a real and recurring attack. So is
  **dependency confusion**, where a public package is published under the name
  of somebody's internal one so that a misconfigured installer prefers it.
  If your organisation has private packages, pin the index explicitly rather
  than letting the resolver choose.
- Pin versions and use a lock file for applications. An unpinned dependency
  means that what you install today is not what you tested yesterday.

## Credentials, if you ever do publish

This lab never does, but the rules matter the first time you do:

- Authenticate with an **API token**, not a password, and scope it to one
  project rather than to your whole account.
- Put the token in an environment variable or an operating-system keyring.
  **Never** in a file inside the repository, never in `pyproject.toml`, never
  in a shell script committed alongside the code. A token in git history is a
  leaked token even after you delete the line.
- Prefer a trusted-publishing arrangement where your build system proves its
  identity to the index directly and no long-lived token exists to leak.
- Rehearse against the test index first. It is a separate service with separate
  accounts, and it exists precisely so that a first release can be a mistake.

## What you cannot undo

A version number, once published to the public index, is permanent. You may be
able to hide (yank) a release, but you can never re-upload different bytes
under the same version. Anyone who already installed it keeps what they got,
and any lock file that pinned it keeps pointing at it.

The consequence is a rule, not a preference: **a bad release is fixed by
publishing a new version.** Never by quietly replacing the old one — which the
index will refuse anyway.

The second consequence is why this lab builds locally. An accidental upload is
a class of mistake with no undo, so the safe way to teach packaging is to stop
one command short of it.

## Data handling

Nothing here reads personal data, the network, the clock, or a random number.
The only input is `examples/sample.txt`, which contains one sentence about a
cat. Every number in `expected-output/` is reproducible from the pinned tool
versions.
