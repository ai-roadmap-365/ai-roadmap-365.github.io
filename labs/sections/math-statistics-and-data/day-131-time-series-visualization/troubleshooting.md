# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'pandas'`

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

Something imported `matplotlib.pyplot` before `matplotlib.use("Agg")`
ran. Both `conftest.py` files set the backend first, before anything
else is imported — if you add a new test file, import `matplotlib` and
call `matplotlib.use("Agg")` at its very top, before `import
matplotlib.pyplot`. The test harness also exports `MPLBACKEND=Agg` as a
second line of defense.

## `pytest examples starter` aborts with `import file mismatch`

Both directories define a module named `test_timeseries.py`, and pytest
imports test modules by their dotted name — running them together is
tested directly in this lab's harness (section 4) and reliably aborts
collection before running a single test. Run them as two separate
commands, always:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

## Exercise 9 raises `ZoneInfoNotFoundError` or similar

Your platform has no installed IANA timezone database. Install the
pure-Python fallback:

```bash
.venv/bin/pip install tzdata
```

macOS and Linux normally do not need this — see
`requirements/README.md` for when it applies.

## Exercise 9's hour counts are not exactly `23` / `25` / `24`

Recompute directly rather than hardcoding: `2024-03-10` is the date the
US moved clocks forward that year, and `2024-11-03` is when they moved
back. If your installed tz database is unusually old, US DST rules have
in fact been stable (the second Sunday in March / first Sunday in
November) since 2007, so this is unlikely to be the cause — check first
whether your date range actually spans the boundary you think it does.

## Exercise 3's spurious period is not `20`

Recompute `ALIASING_TRUE_PERIOD_DAYS` (4) and
`ALIASING_SAMPLE_INTERVAL_DAYS` (5) from `data.py` directly rather than
hardcoding the number — if either constant has been edited, the
spurious period changes with it, predictably: it is always the smallest
`k` (in samples) at which the downsampled cosine repeats, times the
sampling interval.

## Exercise 4's trailing offset is outside `10`-`20` days

The reference solution asserts a tolerance range, not the single
captured value (`14` days), because the exact offset depends on the
triangular bump's shape and the window size, not just "half the
window" as a rule of thumb. If you changed `PEAK_HALF_WIDTH_DAYS` or the
rolling window size in your own experiment, recompute the expected
range rather than assuming `10`-`20` still applies.

## The savefig check in `tests/run_tests.sh` fails

Confirm the same `.venv` used for the rest of the harness has
matplotlib's own PNG writer available (matplotlib ships its own PNG
backend and needs no separate image library for this). If
`fig.savefig(...)` raises, run the same lines from section 6 of
`tests/run_tests.sh` directly in your shell to see the real traceback.

## Image files left behind after a manual experiment

If you called `plt.savefig(...)` yourself while exploring outside the
test suite, `tests/run_tests.sh`'s cleanliness check (section 7) will
report it. Remove the file and re-run; nothing in `examples/` or
`starter/` writes an image file on its own.
