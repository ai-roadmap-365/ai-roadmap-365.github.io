# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness will not run against whatever Python is on your `PATH`,
because every number here is pinned to exact package versions. Build the
environment first:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you deliberately want a different interpreter, the harness honours
`PYTHON` and `PYTEST`:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

Expect version-check failures if those do not match the pins. That is the
harness working, not the harness breaking.

## `StageContractError` when I did not expect one

Read the message. It names the stage and the key:

```
stage 'select' requires ['folds'] which no earlier stage produced
```

That means a stage was placed before something it depends on. If you are
running `leaky_stages()` with contracts enforced, this error is the
expected result and exercise 3b asserts it. If you are seeing it on a
pipeline of your own, the ordering genuinely is wrong.

The contract also checks the other direction: a stage that produces a key
it did not declare, or fails to produce one it did, raises the same error.
That catch is deliberate — a stage quietly adding keys is how a pipeline
becomes impossible to reason about.

## `KeyError` deep inside a stage

You ran with `enforce_contracts=False` and a required key was absent. The
pipeline fails either way; the difference is that the contract tells you
*which stage* broke and the `KeyError` tells you only which dictionary key
was missing, from somewhere inside a function you now have to find.

Exercise 8 asserts both behaviours side by side, because the contrast is
the argument for contracts.

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names, so pytest cannot decide which
`workflow_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so that this is documented behaviour rather than a surprise.

## My honest score is below 0.5, which looks like anti-learning

It is not. With 100 rows split into 5 folds, each fold's score is measured
on 20 rows, which gives a standard error of about 0.11 around a true value
of 0.5. Landing at 0.39 or 0.38 is well within that.

This is exactly why the lab asserts `right <= 0.5` in exercise 3c rather
than `right == 0.5`. The claim worth defending is that the honest pipeline
does not beat chance on data with nothing in it — not that it lands on
0.5000 every time.

## The manifest hashes do not match on my machine

Check `expected-output/FIELDS.md` first. The four hashes are SHA-256 over
the raw bytes of the arrays, so they depend on the exact float values,
which depend on NumPy's generator stream. NumPy's documentation is
explicit that `Generator` gives no stream-compatibility guarantee across
versions.

The property that must still hold on any version is that **two runs at the
same seed agree and a run at a different seed does not**. If that has
broken, something genuinely non-deterministic has entered the pipeline and
is worth finding. If only the literal hashes have moved, the pins are
doing their job.

## The stage line counts do not match

`stage_source_lines` reads the actual source with `inspect.getsource`, so
if you have edited `workflow_lib.py` the counts will legitimately have
changed. That is the intended behaviour — exercise 7 measures *this*
pipeline, not a remembered figure. Either restore the file or update the
assertion to what your version actually is, and say so.

## `LogisticRegression` warns about convergence

`max_iter=1000` is set on both logistic models specifically to avoid this.
If you construct your own with the default of 100 you may see a
`ConvergenceWarning`, and the scores will differ slightly from the
captured ones. Use `w.candidate_models()` rather than building your own,
or match its settings.
