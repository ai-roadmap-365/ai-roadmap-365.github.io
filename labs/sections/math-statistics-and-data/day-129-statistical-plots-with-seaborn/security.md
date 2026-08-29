# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download seaborn, matplotlib,
  pandas, NumPy and pytest from PyPI into this lab's own `.venv`. Every
  script and test after that runs completely offline.
- Renders headless via matplotlib's `Agg` backend (`matplotlib.use("Agg")`,
  set before `pyplot` is imported anywhere, and `MPLBACKEND=Agg` in the
  test harness) — no window ever opens, and no display server is needed,
  which matters on a CI runner or a machine with no screen.
- Writes only inside its own `.venv` directory (created by you, via
  `python3 -m venv .venv`), transient `__pycache__` / `.pytest_cache`
  directories the harness removes both before and after every run, and
  one deliberately temporary directory (`mktemp -d`) that the harness's
  savefig check writes a single PNG into and then deletes. Nothing this
  lab does leaves a file anywhere outside its own directory.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every table is a small literal built by hand in `data.py` —
`team_scores` (sixteen rows across four teams), `wide_revenue` (five
regions, four quarters) and its melted form `long_revenue` — invented for
the exercises. Nothing here is real personal, financial or otherwise
sensitive data, and nothing is downloaded from any external dataset.

## The design point this day is actually about

seaborn draws a *computed statistic*, not your raw data — a `barplot`'s
bar height is a group mean, and its error bar is, by default, a random
bootstrap resampling of your own data. That randomness is exactly why
this lab's exercise 3 asserts that two unseeded runs differ: nothing is
broken, seaborn's default confidence interval is genuinely a different
number each time it is drawn, unless you fix `seed=`. The practical
consequence for anyone reading a `barplot` in a report, including one a
model produced: the chart states a claim about sampling variability
whether or not the person who made it meant to make one, and knowing
which statistic is on the page — mean, standard deviation, a bootstrapped
interval — is part of reading the page honestly.
