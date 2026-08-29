# Troubleshooting

## `ModuleNotFoundError: No module named 'numpy'` (or `pandas`)

You are running the system `python3`, not the lab's virtual environment.
Every command in this lab is prefixed `.venv/bin/python3` or
`.venv/bin/pytest` on purpose. If you have not created the environment yet:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

## Running a script directly with `python3 01_forking_paths.py` fails to import `dataset` or `exploration`

Run it from inside `examples/` (or `starter/`), not from the lab root:

```bash
cd examples
../.venv/bin/python3 01_forking_paths.py
```

Each script imports `dataset` and `exploration` from beside itself.

## `pytest starter -q` keeps reporting a test as skipped

A skip means the function it calls still raises `NotImplementedError` (or
returns `None`). Open `starter/exploration.py`, find the function named in
the skip message, and write it. `00_brief.md` describes exactly what each
one should do and return.

## `pytest starter -q` reports a FAILURE, not a skip

Good news first: a failure means you wrote something, and it ran. The
message shows your value next to the expected one -- read both before
changing anything. A common cause: `two_sample_z_test` returning
`(p, z)` instead of `(z, p)` (the order matters, and several later
exercises depend on it being right).

## `simulate_forking_paths` runs but the assertion fails intermittently

If you changed `n_per_group` down from the default of 200, this is
expected, not a bug in your code. The two-sample z-test uses a *z*
critical value, which assumes the population variance is known; with an
estimated variance at small `n`, the true rejection rate under the null
drifts slightly above nominal (the same effect Day 118 measured for
confidence-interval coverage). This lab picked `n_per_group=200`
specifically to keep that drift small enough that three standard errors
of simulation noise comfortably covers it -- confirmed across seeds
1, 7, 42, 118 and 2026 during development (see `metadata.yml`). If you
want to see the drift directly, try `n_per_group=10` and watch the
simulated rate creep above the exact value by more than three standard
errors.

## The "winning" comparison in exercise 2 doesn't clear the effect-size threshold

This is seed-dependent. `dataset.py` pins `NARRATIVE_SEED=6` and
`NARRATIVE_N_ROWS=80` specifically because that combination reliably
produces a winning comparison with `|d| >= 0.5` (see `metadata.yml`'s
third honesty note for the numbers behind that choice). If you experiment
with other seeds or a larger `NARRATIVE_N_ROWS`, expect this assertion to
need a lower threshold, or a seed sweep of your own, exactly as this lab
required.

## The choice-grid or stopping-rule scripts feel slow

`04_choices_are_comparisons.py` runs 3,000 freshly generated datasets
through a 10-cell grid; `08_stopping_rule.py` runs two 20,000-replicate
simulations. Both finish in a few seconds on ordinary hardware (measured:
under 4 seconds total for both, on the authoring machine). If either
takes noticeably longer, check you are not accidentally running under the
system `python3` without NumPy's compiled backend, or on a machine under
heavy load from something else.

## `pytest examples starter` (both directories as separate arguments)

Not documented and not tested by this lab, following the same convention
Day 118 established: `examples/` and `starter/` both define modules named
`dataset` and `exploration`, and combining both directories in one
invocation was found unreliable there (a false green in one case, a
collection abort in another) depending on pytest's rootdir and import-mode
resolution. This lab documents and tests only `pytest examples`,
`pytest starter`, and bare `pytest` with no path (which auto-discovers
both directories and was confirmed here to isolate correctly via each
directory's `conftest.py`).

## `find` reports leftover `__pycache__` or `.pytest_cache` after a run

Running `.venv/bin/pytest starter -q` by itself (outside `run_tests.sh`)
legitimately writes bytecode caches. This is expected and harmless; clean
up with the commands in "Cleanup" in `README.md`. `run_tests.sh` clears
them before it starts, so its own final check measures only what that run
left behind.
