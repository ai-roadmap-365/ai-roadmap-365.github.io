# Troubleshooting

Grouped by the message you actually see.

## `ModuleNotFoundError: No module named 'matplotlib'`

The lab's dependencies live in its own `.venv`, not on your system
Python.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the harness at a Python that already has the pinned packages:
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## `ModuleNotFoundError: No module named 'PIL'`

The package is installed as `pillow` and imported as `PIL`. That is
correct and confusing, and it is why `requirements.txt` says `pillow`
while `render.py` says `from PIL import Image`. Install the requirements
file, not the import name.

## `pytest examples starter` fails with `import file mismatch`

This is expected, not a bug — do not work around it by renaming files or
adding `__init__.py`. `starter/` and `examples/` both define modules
called `encoding`, `charts`, `palettes`, `render`, `conftest` and
`test_charts`, and pytest refuses to import two different files under one
module name. Run the two commands separately:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

Section 5 of `tests/run_tests.sh` asserts that the combined invocation
fails this way, so the warning is a measurement rather than a rumour.

## `ModuleNotFoundError: No module named 'charts'` when running one file

Run pytest against the **directory**, from the lab root:

```bash
.venv/bin/pytest starter
```

not `pytest starter/test_charts.py` from inside `starter/`. pytest adds
the test file's directory to `sys.path` for you when it collects a
directory with no `__init__.py`, which is how `import charts` resolves.

## The suite hangs, or you see a warning about a GUI backend

You have a `MPLBACKEND` environment variable set to something
interactive, and it is overriding matplotlib's own default. `render.py`
calls `matplotlib.use("Agg")` explicitly, which wins over the
environment, so this should not happen — but if you have imported
`pyplot` yourself in the same process first, the backend is already
chosen and `use()` may not take effect. Start a fresh interpreter:

```bash
unset MPLBACKEND
.venv/bin/pytest examples
```

Section 2 of the harness checks the resulting backend is `agg` and will
tell you if it is not.

## A pixel count is a few percent off the captured value

Check your matplotlib version first:

```bash
.venv/bin/python3 -c "import matplotlib; print(matplotlib.__version__)"
```

It must be `3.11.1`. Every pixel count in `expected-output/` came from
that version's Agg rasteriser; a different version can change a default
line width or a rasterisation rule and move the totals. The harness
checks the pin before it asserts anything, so a version mismatch is
reported as its own failure rather than as a confusing pixel count.

If the version matches and a count is still off, read
`expected-output/FIELDS.md` — it lists which numbers are exact
arithmetic, which are renderer-dependent, and which are neither.

## `assert 3.9503... == approx(4.0 ± 4.0e-02)` fails in exercise 1

Your tolerance is too tight. A rasteriser decides whether each boundary
pixel of a circle is in or out, and with antialiasing off that decision
lands a couple of percent away from the ideal `pi*r^2`. Use
`pytest.approx(4.0, rel=0.02)` — and note that the *ratio* is what
survives; asserting the raw pixel count against `pi*r^2` exactly would
be asserting something that is not true.

## `ValueError: change_over_time needs a temporal variable in data_types`

`choose_chart` refuses rather than guesses. You asked for a chart of
change over time without telling it there is a time variable. Add
`"temporal"` to `data_types`. If there genuinely is no time variable, the
question is not about change over time and the right fix is upstream of
the chart.

## `ValueError: 'hue' is not a ranked magnitude channel`

Working as intended, and the error is the lesson. Cleveland and McGill
ranked channels by how accurately people read *magnitudes* off them. Hue
carries identity, not magnitude, so "how accurately can you read a
quantity off a hue" is not a question hue can be asked. Use
`charts.IDENTITY_CHANNELS` if you want to check membership.

## The lab left a `.png` behind

You rendered to a path that was not the `png_dir` fixture. Every render
function takes an explicit path on purpose; pass it
`png_dir / "something.png"` and the fixture removes the whole directory
when the test finishes. Delete the stray file and re-run:

```bash
find . -name '.venv' -prune -o -name '*.png' -print
```

## `pytest starter` reports `17 skipped` and you have written code

You wrote assertions but left the `pytest.skip(...)` call above them. A
`skip` raises immediately, so nothing below it runs. Deleting the skip
line is part of each exercise.
