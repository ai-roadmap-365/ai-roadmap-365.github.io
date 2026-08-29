# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, pyarrow and NumPy
  from PyPI into this lab's own `.venv`. Every script and test after that
  runs completely offline. `tests/run_tests.sh` section 6 greps every file
  in `examples/` and `starter/` for a URL and fails the suite if it finds
  one, so this is checked rather than merely claimed.
- Writes only inside its own `.venv` directory (created by you, via `python3
  -m venv .venv`) and transient `__pycache__` / `.pytest_cache` directories
  that the test harness removes both before and after every run.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every value in every exercise is a small literal frame invented for the
demonstration — eight rows of names and test scores, five rows of a
customer/amount/region orders table, six rows of a customer/item orders
table with deliberate duplicates. Nothing here is real personal, financial
or otherwise sensitive data, and nothing is downloaded from any external
dataset.

## The design point this day is actually about

A filter is a claim about which rows a report speaks for, and rows that
silently fail every comparison in a filter — because they are missing —
do not raise an error. They are simply absent from the answer. Exercise 1
demonstrates that directly: "high performers" and "everyone else," each
computed with an ordinary, defensible-looking comparison, together leave
out anyone whose score was never recorded. In a real report this is not a
cosmetic bug — it silently discards exactly the rows a reviewer is least
likely to notice missing, because there is no error message pointing at
them.

Exercise 4's mask-alignment behaviour has a related, quieter risk: a
boolean mask computed against one version of a table and then applied to a
different (reordered, refiltered, or re-fetched) version of the same table
does not fail loudly if the labels still line up — it silently returns the
labels the mask names, in whatever row order the target table happens to
be in. That is usually exactly right. It is also exactly how a mask
computed on last week's snapshot of a table, applied to this week's, can
select the wrong rows with no exception anywhere, if row identities have
shifted underneath it. This lab does not exploit that; it is the exact
failure mode exercise 4 exists to make visible before it reaches a report
or a training set.
