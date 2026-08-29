# Security notes — Day 141 lab

## What this lab touches

- **Files:** only this lab directory, plus one temporary directory the
  harness creates with `mktemp -d` and removes before it exits. Nothing
  is written to your home directory, your shell configuration, or
  anywhere above the lab root.
- **Network:** one step only — `pip install -r requirements/requirements.txt`,
  which fetches the three pinned packages and their dependencies from
  your configured package index. Every other command in this lab runs
  entirely offline. The harness checks directly that no URL appears
  anywhere in `starter/` or `examples/` source.
- **Credentials:** none. No API key, no token, no account, no
  environment variable carrying a secret. `requires_api_key` is `false`
  in `metadata.yml` and there is nothing to configure.
- **Privileges:** none. No `sudo`, no system package manager, no
  installation outside the lab-local `.venv`.
- **Processes and ports:** none. This lab starts no server and binds no
  port.

## Data

Every dataset in this lab is either generated on the spot from a seeded
`numpy.random.default_rng`, or is the iris measurements bundled inside
the installed scikit-learn package. Iris is 150 rows of flower
measurements published in 1936; it contains no personal data and needs
no download. Nothing in this lab reads a file you own, inspects your
environment, or records anything about your machine.

## The one risk worth naming

The genuine hazard in this lab is not technical, it is professional: the
techniques here produce numbers that look authoritative and are not. A
training-set accuracy of 1.000 from a model that has learned nothing is
the clearest example, and it takes six lines to produce. If you copy
these patterns into work that other people rely on, report what the
number was measured on every single time. A score without its evaluation
protocol is not a result; it is a claim someone else will have to
disprove.

## Supply chain

The three pins in `requirements/requirements.txt` are exact versions,
not ranges, so a re-run installs the same code that produced the
captured output. Installing scikit-learn also brings in `scipy`,
`joblib` and `threadpoolctl` as transitive dependencies; those are not
pinned here because nothing in this lab imports them directly, and their
versions are recorded in `expected-output/FIELDS.md` for the run that
produced the captured numbers. If you need byte-for-byte supply-chain
reproducibility, generate a full lock file with `pip freeze` after
installing.
