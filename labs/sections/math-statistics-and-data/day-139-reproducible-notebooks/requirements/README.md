# Requirements

`requirements.txt` pins the exact versions this lab was written and run
against on 2026-08-20: `nbformat`, `nbclient`, `nbconvert`, `ipykernel`
and `pytest`. Everything else the lab uses — `copy`, `importlib`, `sys`
— is in the Python standard library.

This lab's whole point is executing real notebooks with a real Jupyter
kernel, so its own dependency stack is the largest of any lab in this
section. None of it is installed in the shared authoring virtual
environment for this course (see Day 133, where `pandas.DataFrame.style`
fails for exactly the same reason: nothing that pulls in `jinja2` is
installed centrally, and `nbconvert` depends on `jinja2`). Every command
below runs inside this lab's own `.venv`, which is the normal pattern.

```bash
cd labs/sections/math-statistics-and-data/day-139-reproducible-notebooks
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Only that install step needs the network. Everything after it runs
offline: every notebook in this lab is built in memory, executed by a
kernel on `127.0.0.1` (ZeroMQ over loopback, the same transport Jupyter
always uses for a local kernel), and never written to disk.

## Why the pins are exact

- `nbclient` writes a wall-clock timestamp into `cell.metadata.execution`
  on every run. Exercise 5 depends on that behaviour existing at all — a
  much older `nbclient` before this metadata was added would make the
  exercise's central claim untestable.
- `nbformat` is the schema every assertion in this lab reads: cell
  `outputs`, `execution_count`, `metadata`. A schema version bump could
  change field names.
- `ipykernel` is the kernel every notebook in this lab actually runs on.
  Its version is recorded because exercise 9 (the environment record)
  quotes it directly.

## If a pin will not install

Recent `nbformat` 5.x, `nbclient` 0.10+ and `nbconvert` 7.x will almost
certainly run this lab unmodified. `ipykernel` just needs to be new
enough to register a `python3` kernel spec automatically on import,
which every version in the last several years does. If a test fails
after a version substitution, `expected-output/FIELDS.md` records which
captured values are exact everywhere and which are specific to the pins
above.
