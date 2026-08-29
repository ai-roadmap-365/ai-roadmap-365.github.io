# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, pyarrow, NumPy and
  pytest from PyPI into this lab's own `.venv`. Every script and test
  after that runs completely offline.
- Writes only inside its own `.venv` directory (created by you, via
  `python3 -m venv .venv`), transient `__pycache__` / `.pytest_cache`
  directories the test harness removes both before and after every run,
  and Parquet files written only to `tmp_path` — a pytest-managed
  temporary directory outside the lab, cleaned up automatically by
  pytest itself.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory and pytest's own
  temporary directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

`data.py`'s `build_raw_orders()` is seven literal rows invented for this
lab's exercises. Nothing here is real personal, financial or otherwise
sensitive data, and nothing is downloaded from any external dataset.

## The design point this day is actually about

A cleaning pipeline that is not idempotent will drift without ever
failing: run it twice by accident — a re-triggered scheduled job, a retried
API call, a notebook cell run out of order — and it produces a
DIFFERENT, silently wrong result, with no exception anywhere to flag it.
This lab's exercise 1 is not a hypothetical: it is the concrete mechanism
by which a step that looks correct once (clip outliers to the 99th
percentile) becomes actively harmful the moment it runs again on its own
output, which is exactly the situation a production scheduler creates
routinely and a person testing a notebook by hand almost never does.

The manifest in exercise 9 is this lab's other security-adjacent point,
and it is also this lesson's AI thread: a training set is the output of a
pipeline, and when a model's behaviour changes unexpectedly, the first
question is whether the data changed. Without a manifest recording the
input hash and the configuration that produced a given output, that
question has no answer, and debugging a model regression becomes
guesswork rather than a lookup.
