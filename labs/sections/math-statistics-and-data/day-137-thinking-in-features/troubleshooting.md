# Troubleshooting

## `pytest: command not found`, or the harness exits before any check

You have not created the lab's virtual environment, or you are calling
bare `pytest` rather than the one in `.venv`.

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

The harness looks for `.venv/bin/pytest` first, then anything on your
PATH. To point it at an interpreter of your own:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'experiments'`

You ran pytest from somewhere other than the lab directory, or with an
import mode that does not put the test file's own directory on
`sys.path`. Run from the lab directory and name the folder:

```bash
cd labs/sections/math-statistics-and-data/day-137-thinking-in-features
.venv/bin/pytest starter -v
```

`starter/` and `examples/` are each self-contained: every module a test
imports lives beside it.

## `import file mismatch` when you run both suites at once

You ran `pytest examples starter` in one invocation. Both directories
hold a module named `test_features.py`, and pytest collects by dotted
module name, so the second one collides with the first. Run them as two
commands:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Section 5 of the harness runs the bad combination on purpose and asserts
that it fails, so this is a documented behaviour rather than a surprise.

## The suite takes about sixteen seconds and feels slow

That is expected and it is where the honesty comes from. Four of the
nine experiments average over many random train/test splits — 200 for
the scaler, 150 for the imputer, 40 each for the target encoding and the
vocabulary — because a single split with a small test set says nothing.
Each split trains a fresh model with 3,000 gradient-descent steps.

Session-scoped fixtures in `conftest.py` mean each experiment runs once
per pytest invocation, not once per assertion. Do not "optimise" by
dropping the trial counts: the bands in the tests were chosen for those
counts, and a mean over five splits will fail them intermittently.

## One of my gaps came out with the opposite sign

Read `expected-output/FIELDS.md` before you change anything. One of them
is *meant* to: `scaler_optimism_points` is **−0.06** on the authoring
machine, and that negative number is the finding, not a bug. A scaler
fitted on all the data buys essentially nothing, and the file explains
why in full.

If a gap that should be large — target leakage, the imputer, the
temporal split — comes out small or reversed, check in this order:

1. `.venv/bin/pip freeze | grep -E 'numpy|pandas'` against
   `requirements/requirements.txt`. Every result here is seeded, so a
   different NumPy generator stream is the only plausible cause of a
   changed number.
2. Whether you edited a generator in `data.py`. The plants are described
   in each docstring; moving one moves the result.
3. Whether you reduced a `trials` argument.

## An assertion fails on a different NumPy version

Every band in `examples/test_features.py` is wide enough to survive
ordinary variation, and exercise 5 is exact only because it is
arithmetic rather than sampling. If a band still fails, print the
dictionary the fixture handed you before you touch the band:

```python
def test_something(leakage):
    print(leakage)
    assert False
```

Then run `pytest examples -q -s`. Look at the number. Moving a band to
make a test pass throws away the measurement you came for.

## `pip install` fails behind a proxy or with no network

The install is the only step that needs the network. If pandas, NumPy
and pytest are already available in some other environment, point the
harness at it:

```bash
PYTEST=/path/to/other/venv/bin/pytest bash tests/run_tests.sh
```

Section 1 will report a version mismatch against the pins and fail that
one check. The nine exercises should still pass; `expected-output/FIELDS.md`
records exactly which values are version-sensitive.

## `bash: tests/run_tests.sh: No such file or directory` on Windows

Run the lab under WSL2. The harness is bash and is not translated to
PowerShell. Native Windows will run `pytest examples` and
`pytest starter` perfectly well; only `run_tests.sh` needs the shell.
