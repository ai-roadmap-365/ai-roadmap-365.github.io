# Requirements

`requirements.txt` pins the exact versions this lab was written and run
against on 2026-08-20. Everything else it uses — `dataclasses`, `typing` —
is in the Python standard library.

Install into a lab-local virtual environment so the pins cannot collide
with anything else on your machine:

```bash
cd labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

**Only that install step needs the network.** Nothing else in this lab
opens a socket, reads a file from disk, or downloads anything. Every table
it measures is constructed in `ethics.py` at import time.

## Why each pin is here

- **NumPy 2.5.2** — every random draw goes through
  `numpy.random.default_rng(seed)`, whose stream is stable across NumPy 2.x
  by NumPy's own documented policy. That stability is what turns "the bias
  stays flat" into a number you can assert rather than a trend you have to
  eyeball. `numpy.polyfit` supplies the least-squares fits in exercises 1
  and 4.
- **pandas 3.0.5** — the group-composition, equivalence-class and
  version-diff work is all `groupby` and `value_counts`. Doing it in plain
  dictionaries would be possible and would teach the wrong habit: these are
  exactly the operations you would run on a real frame.
- **pytest 9.1.1** — the exercise runner.

## What is deliberately NOT pinned here

**No fairness toolkit is installed.** Fairlearn and AIF360 both implement
the metrics exercise 5 computes by hand, and the lesson describes both from
their published documentation. Neither was installed, neither was run, and
no output from either is reproduced anywhere in this lab. Computing the
three criteria in twenty lines of pandas is also the point of exercise 5:
you can see that the incompatibility is arithmetic rather than a library's
opinion.
