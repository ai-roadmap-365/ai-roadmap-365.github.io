# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, matplotlib, NumPy
  and pytest from PyPI into this lab's own `.venv`. Every script and test
  after that runs completely offline.
- Renders headless via matplotlib's `Agg` backend (`matplotlib.use("Agg")`,
  set before `pyplot` is imported anywhere, and `MPLBACKEND=Agg` in the
  test harness) — no window ever opens, and no display server is needed,
  which matters on a CI runner or a machine with no screen.
- Writes only inside its own `.venv` directory (created by you, via
  `python3 -m venv .venv`), transient `__pycache__` / `.pytest_cache`
  directories the harness removes both before and after every run, and
  two deliberately temporary directories (`mktemp -d`) that the harness
  uses to prove the suite can fail and to prove a real headless savefig
  works — both removed immediately after use. Nothing this lab does
  leaves a file anywhere outside its own directory.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.
- Exercise 9 reads your system's installed IANA timezone database (via
  Python's `zoneinfo`) to compute DST transition dates for
  `America/New_York`. It does not download, modify, or otherwise touch
  that database — it only reads publicly documented transition rules
  already present on your machine (or, on platforms without one, the
  optional `tzdata` PyPI package documented in `requirements/README.md`).

## What the data in this lab is

Every table and signal is a small, deterministic construction built by
hand in `data.py` — date ranges, a hand-written cosine, a triangular
bump, a fixed compounding-growth formula. Nothing here is real personal,
financial, sensor, or otherwise sensitive data, and nothing is
downloaded from any external dataset.

## The design point this day is actually about

A plotted time series makes claims about *when* something happened, and
those claims are easy to get quietly wrong: plotting against a row index
instead of a parsed datetime erases real gaps; resampling silently picks
an aggregation that answers one specific question and not others;
downsampling below a signal's true frequency does not just lose detail,
it manufactures a false pattern that looks completely convincing;
connecting across a genuinely missing observation instead of reindexing
first hides the very fact that anything is missing. None of these is a
security vulnerability in the conventional sense, but every one of them
is a way a chart can misrepresent reality to a reader who trusts it —
and a trailing-window monitoring dashboard that reports an accuracy
regression two weeks late, because of exactly the lag exercise 4
measures, is a real operational risk in any team running a model in
production.
