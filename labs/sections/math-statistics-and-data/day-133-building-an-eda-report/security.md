# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, which downloads matplotlib, seaborn,
  pandas, NumPy and pytest from PyPI into this lab's own `.venv`.
  Everything after that runs completely offline. Section 7 of the harness
  asserts directly that no URL of any kind appears in `starter/` or
  `examples/`.
- Renders headless via matplotlib's `Agg` backend — `matplotlib.use("Agg")`
  runs in each `conftest.py` before `pyplot` is imported anywhere, and
  `report.py` sets it again at import for anyone who uses the generator
  outside pytest. `MPLBACKEND=Agg` is exported by the harness as a third
  belt. No window opens and no display server is needed, which matters on
  a CI runner or a machine with no screen.
- Writes only inside its own `.venv` (created by you), transient
  `__pycache__` and `.pytest_cache` directories the harness removes both
  before and after every run, and temporary directories created with
  `tempfile.TemporaryDirectory` and `mktemp -d` that are deleted when the
  test or the harness section that made them finishes.
- Never binds a port, never needs `sudo`, never reads or writes a file
  outside this lab's directory and those temporary directories.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

`data.monthly_sales()` generates every row from a fixed
`numpy.random.default_rng(133)` call. Nothing is loaded from a file,
downloaded, or derived from any real organisation's or person's data. The
"pricing change", the missing partner rows and the single anomalous month
are all put there deliberately by `data.py`, and the module says so at the
top.

That matters for more than privacy. A generated report that argues about
data whose truth you already know is the only way to check that the
argument is honest — you can compare what the report claims against what
you put in.

## The part of this lab that is actually a security habit

A report generator writes files, and two of its behaviours are worth
naming as controls rather than as features:

- **Nothing is interpolated from user-controlled text into a shell or a
  template engine.** The generator builds Markdown by joining strings in
  Python. It does not shell out, it does not `eval`, and it does not
  render through a template language, so there is no injection surface in
  it at all.
- **Provenance is a hash of the input, not a note about the run.** The
  report records `sha256` of the input frame's CSV serialisation, first
  twelve hex characters. That is what makes two runs byte-identical, and
  it is also what lets a reader ask "was this built from the data I think
  it was built from?" and get an answer. A report that records only a
  timestamp cannot answer that question.

## What to be careful about if you point this at real data

The generator embeds computed numbers directly into prose. That is the
point — but it means anything in the input reaches the output. Before you
run it on a real dataset:

- Check what your captions and prose would print. A caption interpolating
  a "top customer by revenue" prints a customer name into a document you
  may be about to share.
- The `sha256` fingerprint is of the data, so it changes when the data
  changes. It is not a secret, but it is a fingerprint: two people can
  tell whether they hold the same input without either showing it.
- Figures are raster images with no metadata scrubbing applied. matplotlib
  does not embed a filename or a user name in a PNG by default, but if you
  add `savefig(..., metadata=...)` you are responsible for what goes in.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv
```

Nothing else is created. Section 7 of the harness checks that claim
rather than asserting it: it looks for image files, for a generated
`report.md`, for `__pycache__`, for `.pytest_cache`, and for any
`d133-*` directory left in the system temporary directory, and fails if
it finds one.
