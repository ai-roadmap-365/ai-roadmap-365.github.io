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
  fail-then-restore check (section 5) uses for a scratch copy of the
  solved test file and then deletes. Nothing this lab does leaves a file
  anywhere outside its own directory.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every sample is generated in `data.py` from a fixed
`numpy.random.default_rng(seed)` call — nothing is loaded from a file,
downloaded from an external dataset, or drawn from any real person's
data. The two hand-engineered samples in exercise 5 (a bimodal sample
and a unimodal sample sharing a five-number summary) are built by a
piecewise-linear quantile function defined directly in `data.py`, not by
random sampling, so that the demonstration is exact and reproducible.

## The design point this day is actually about

Every picture in this lab hides something the others show. A histogram's
shape depends on a bin width you chose; a KDE's shape depends on a
bandwidth you chose, and a KDE of strictly positive data quietly places
real probability mass below zero; a boxplot's five-number summary is
compatible with more than one underlying shape, which exercise 5
demonstrates directly by constructing two samples that share one exactly.
The practical consequence for anyone summarizing data for a report,
including a model doing it automatically: a single summary statistic or
a single default chart can be arithmetically correct and still discard
the fact that mattered. A monitoring pipeline that checks a feature's
mean and standard deviation for drift, and nothing else, will not notice
that feature quietly splitting into two populations with the same mean
— which is exactly what exercise 5's two samples do to each other.
