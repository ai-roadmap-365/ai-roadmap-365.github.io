# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, pyarrow, NumPy and
  pytest from PyPI into this lab's own `.venv`. Every script and test
  after that runs completely offline.
- Writes only inside its own `.venv` directory (created by you, via
  `python3 -m venv .venv`) and transient `__pycache__` / `.pytest_cache`
  directories that the test harness removes both before and after every
  run.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every table is a small literal or seeded-random construction built in
`data.py` — `income_spending`, `temperature_readings`, `dropna_frame`,
`sensor_timeseries`, `coerce_frame`, `country_frame`, `duplicates_frame`,
`clean_customers` and `contract_violating_customers` are all invented,
none exceeding forty rows. Nothing here is real personal, financial or
otherwise sensitive data, and nothing is downloaded from any external
dataset.

## The design point this day is actually about

Every cleaning decision in this lab — impute, drop, coerce, normalise,
deduplicate, discard an outlier — throws information away or invents
information that was never observed, and each one changes the answer a
downstream analysis or model produces. Exercise 1's demonstration is the
sharpest version of the risk: the one statistic a careless reviewer is
most likely to check after imputing (the mean) is *exactly* the one
statistic imputation is mathematically guaranteed to leave alone, which
means "the mean didn't move" is worthless as a safety check on its own.
Applied to a production feature-engineering pipeline, the same mechanism
means a naive imputation step can pass a shallow sanity check while
silently degrading a model's ability to use the very column it touched —
this lab's exercise 9 (the cleaning contract) is the concrete habit that
catches that class of problem before it reaches training data: name every
post-condition you actually depend on, and let the pipeline fail loudly
rather than pass a check that never tested the thing that mattered.
