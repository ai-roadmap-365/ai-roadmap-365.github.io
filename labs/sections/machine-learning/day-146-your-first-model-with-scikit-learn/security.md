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
  is bundled. `sklearn.utils.estimator_checks.check_estimator` (exercise
  10) also runs entirely offline — it builds its own synthetic data.
- **Subprocesses.** `estimator_census()` (exercise 7) spawns exactly one
  child process, `sys.executable -c "..."`, to get a genuinely fresh
  `all_estimators()` reading unaffected by anything already imported in
  the parent. It is the same Python interpreter running this lab, invoked
  with a fixed, hard-coded, three-line snippet — no data, no argument from
  outside the lab, and nothing from the environment is passed into it. It
  writes nothing, reads nothing but its own `import`, and exits
  immediately.
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

The `get_params`/`set_params`/`clone` machinery this lab builds and tests
(exercises 3, 3b, 4 and 4b) is worth reading as more than a convenience
API.

`clone()` is scikit-learn's answer to a real hazard: an object holding
mutable state (a fitted model's learned attributes) being handed to code
that expects a blank slate. `GridSearchCV`, `cross_val_score` and every
`Pipeline` fold rely on `clone()` producing a fresh instance with the same
*configuration* and none of the previous run's *learned state*. If cloning
ever accidentally carried learned state forward, a search or a
cross-validation loop would silently leak information between folds —
which is the same shape of bug Day 143 spent a whole day on, arriving here
from the object-model side instead of the workflow side.

`get_params()`/`set_params()` round-tripping correctly is what makes that
safe: `clone()` is implemented as `type(estimator)(**estimator.get_params(deep=False))`,
so an estimator whose `get_params()` does not report every constructor
argument, or whose `set_params()` does not accept every reported key, is
silently unclonable in a way that is easy to miss until a search behaves
strangely.

## What the code does that is worth understanding

- `MajorityClassifier` (exercises 1-3) never mutates any argument passed
  into it, never reads an environment variable, and never touches the
  filesystem.
- `check_estimator()` (exercise 10) constructs its own tiny synthetic
  datasets internally and never reaches outside the process.
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
