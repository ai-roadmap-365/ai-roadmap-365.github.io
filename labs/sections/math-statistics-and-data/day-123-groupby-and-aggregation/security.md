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

Every table is a small literal built in `data.py` — `orders`, `sales`,
`cat_sales` and `weighted` are each a dozen or fewer rows invented for the
exercises — except `large`, a synthetic column of 200,000 rows generated
with a fixed seed (`np.random.default_rng(42)`) purely to make the
built-in-versus-`.apply` timing comparison in exercise 8 meaningful at
scale. Nothing here is real personal, financial or otherwise sensitive
data, and nothing is downloaded from any external dataset.

## The design point this day is actually about

`groupby` drops rows whose key is missing by default, silently — no
exception, no warning, a plausible-looking result. Applied to a fairness
or coverage report (accuracy per demographic segment, revenue per region),
that default quietly removes exactly the rows whose segment label was
never recorded, which are rarely the rows a report can afford to drop
without saying so. This lab's exercise 1 is not a hypothetical: it is the
concrete mechanism by which an aggregate report can look complete while a
whole category of it is missing, undetected, unless someone checks that
the parts reconcile with the whole.

`observed=` in exercise 7 has a related, quieter cost: grouping several
categorical keys without `observed=True` can manufacture a combinatorial
number of empty rows for combinations that were never seen. On a wide
categorical dataset this is a genuine memory hazard, not merely a
cosmetic one — the lesson's Implications section measures it.
