# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, which downloads NumPy, pandas and pytest
  from PyPI into this lab's own `.venv`. Everything after that runs
  completely offline. The harness checks this directly: section 7 greps
  `examples/` and `starter/` for any use of `urllib`, `requests`, `socket`
  or an `http` URL and fails if it finds one.
- Binds **no** sockets and starts **no** servers or subprocesses beyond
  pytest itself.
- Writes only inside `.venv` (created by you), transient `__pycache__` and
  `.pytest_cache` directories the harness removes before and after every
  run, and one `mktemp -d` scratch directory used by the prove-it-can-fail
  section, which is removed by an `EXIT` trap even if the run is
  interrupted.
- Never needs `sudo`, a credential, an API key, or an account of any kind.

## Why every dataset in this lab is synthetic

This is the security note that actually matters here, and it is a design
decision rather than a convenience.

A lab about **who is missing from a dataset**, about **re-identifying
people from quasi-identifiers**, and about **what a sensitive attribute
discloses** should not be taught on records describing real people. There
is no consent for it, no purpose limitation covering it, and no way to
undo it once a copy is on a learner's laptop. Teaching disclosure risk by
demonstrating disclosure on real records would fail the lesson's own
standard on the first page.

So `ethics.py` constructs every table it measures:

- `synthetic_register()` draws birth years, postcodes, sexes and diagnosis
  codes from a seeded generator. The postcodes are four-digit integers in a
  made-up range; they are not a real postal scheme anywhere.
- `fairness_population()` is an integer-exact table written out by hand in
  `FAIRNESS_CELLS`.
- `homogeneous_table()` is twelve hand-written rows.
- `build_versions()` generates one value column and two label columns.

This has a second benefit worth stating: because the population is
constructed, **its true composition is known exactly**. "The west appears
at 0.104 of its population share" is a checkable fact rather than an
estimate, which is what allows the whole lab to be assertions instead of
impressions.

## What the re-identification exercises are, and are not

Exercises 6 and 7 count how many rows of a table are unique on a small set
of quasi-identifiers, and demonstrate that a k-anonymous table can still
disclose a sensitive attribute through a homogeneous class. That is a
**risk measurement technique**, and it is the same arithmetic a data
protection review would run before releasing a table.

It is not an attack tool, and nothing in this lab links a synthetic record
to any external source. If you apply these functions to real data — which
is exactly what they are for — treat the resulting counts as sensitive in
their own right: "these 2,723 rows are singletons" is a map of who is
easiest to identify.

## Handling this material outside the lab

- Run a uniqueness count **before** publishing a table, not after.
- Record the k level you achieved and the number of rows you suppressed to
  get there. Suppression is not free, and the rows it removes are the
  unusual ones — frequently the people the analysis was about.
- Treat "anonymised" as a claim about a threat model, and write down which
  threat model. A file is never anonymous on its own; it is anonymous
  against a stated set of things an adversary is assumed to know.
- A licence that permits a use is not the same as that use being
  appropriate. Permitted is a floor, not a ceiling.
