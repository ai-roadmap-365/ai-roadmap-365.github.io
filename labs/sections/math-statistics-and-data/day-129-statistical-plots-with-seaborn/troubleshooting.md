# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'seaborn'`

Your `.venv` was never created or activated. Run:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the harness at an existing install:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## A plot window tries to open, or the run hangs

Something imported `matplotlib.pyplot` before `matplotlib.use("Agg")` ran.
Both `conftest.py` files set the backend first, before anything else is
imported — if you add a new test file, import `matplotlib` and call
`matplotlib.use("Agg")` at its very top, before `import matplotlib.pyplot`
or `import seaborn`. The test harness also exports `MPLBACKEND=Agg` as a
second line of defense.

## `pytest examples starter` aborts with `import file mismatch`

Both directories define a module named `test_seaborn.py`, and pytest
imports test modules by their dotted name — running them together is
tested directly in this lab's harness (section 4) and reliably aborts
collection before running a single test. Run them as two separate
commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## Exercise 2's bar heights are not exactly `79.0, 70.0, 67.5, 57.5`

Recompute them from `team_scores.groupby("team")["score"].mean()` rather
than hardcoding the numbers — if your `team_scores` fixture has been
edited, the means will legitimately differ from the ones in this
README.

## Exercise 3's two "unseeded" runs come out identical

This can genuinely happen by chance on a tiny sample, though it did not
happen in this lab's own capture (`expected-output/examples-run.txt`).
If it does, re-run once more before concluding something is wrong; the
*seeded* half of the same exercise (`seed=42` twice) must always be
identical, with no exceptions — if that half also disagrees, seaborn is
not receiving your `seed=` argument at all, which usually means an older
seaborn is installed. Check with
`.venv/bin/python3 -c "import seaborn; print(seaborn.__version__)"`.

## `MatplotlibDeprecationWarning: vert: bool was deprecated`

Expected on this pin set. seaborn 0.13.2's internal `boxplot` call still
passes the now-deprecated `vert` keyword to matplotlib's `ax.bxp()` on
matplotlib 3.11.1. It is a warning, not a failure, and every test still
passes; it is documented in `expected-output/FIELDS.md` rather than
hidden.

## The savefig check in `tests/run_tests.sh` fails

Confirm the same `.venv` used for the rest of the harness has `Pillow`
available implicitly through matplotlib's own PNG writer (matplotlib
ships its own PNG backend and needs no separate image library for this).
If `fig.savefig(...)` raises, run the same three lines from section 6 of
`tests/run_tests.sh` directly in your shell to see the real traceback.

## Image files left behind after a manual experiment

If you called `plt.savefig(...)` yourself while exploring outside the
test suite, `tests/run_tests.sh`'s cleanliness check (section 7) will
report it. Remove the file and re-run; nothing in `examples/` or
`starter/` writes an image file on its own.
