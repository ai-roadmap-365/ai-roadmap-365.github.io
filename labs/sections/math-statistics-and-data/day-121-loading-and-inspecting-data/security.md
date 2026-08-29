# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, pyarrow and NumPy
  from PyPI into this lab's own `.venv`. Every script and test after that
  runs completely offline. `tests/run_tests.sh` section 6 greps every file
  in `examples/` and `starter/` for a URL and fails the suite if it finds
  one, so this is checked rather than merely claimed.
- Writes only inside its own `.venv` directory (created by you, via `python3
  -m venv .venv`), and inside a fresh `tempfile.mkdtemp()` directory that
  each individual exercise script creates for its own small CSV, JSON,
  SQLite database or Parquet file — and deletes, in a `finally:` block,
  before the script exits, whether the exercise's assertions passed or
  failed.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside `.venv/`, its own temporary directories, and
  transient `__pycache__` / `.pytest_cache` directories the test harness
  removes both before and after every run.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every value in every exercise is a small literal invented for the
demonstration — three or four rows of country codes, customer IDs, order
totals, or a single accented name — or a synthetic column of a few
thousand to fifty thousand seeded random numbers
(`np.random.default_rng(42)`) generated purely to make the chunking and
category-memory exercises meaningful at a realistic scale. Nothing here is
real personal, financial, or otherwise sensitive data, and nothing is
downloaded from any external dataset. The one "personal-looking" value —
the name "José" and the city "São Paulo" in exercise 5 — is a stock
example chosen only because it contains a byte sequence that fails
predictably under a UTF-8/latin-1 mismatch; it is not associated with a
real person.

## The design point this day is actually about

`read_csv()` is a type-inference engine, and every exercise in this lab is
really about the moment that inference goes unnoticed. An identifier
column silently read as an integer, or a country code silently read as a
missing value, is not a security vulnerability in the traditional sense —
but the same silent-substitution mechanism is exactly how a data pipeline
can quietly merge or export the wrong record with no error anywhere in the
logs. Exercise 3's precision loss is the sharpest version of this: an
identifier that changes value with no warning is a correctness failure
that, in a system where identifiers gate access or authorization, would be
a security failure too. This lab does not exploit anything; it makes the
mechanism visible before it reaches a system where the stakes are real.

The encoding failure in exercise 5 has a related, quieter implication:
`UnicodeDecodeError` is the GOOD outcome here, because it fails loudly. A
byte sequence that happens to decode as different-but-valid text under the
wrong encoding — mojibake — fails silently, and a system that logs or
displays that mojibake without noticing has a data-integrity problem that
looks, to an inattentive reviewer, like everything worked.
