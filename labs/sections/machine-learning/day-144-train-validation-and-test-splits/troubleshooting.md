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

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names, so pytest cannot decide which
`splits_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so this is documented behaviour rather than a surprise.

## The harness takes a while

It does. The selection-bias curve averages 400 replications at nine values
of K, and the holdout comparison fits 200 logistic regressions plus 200
five-fold cross-validations. On the capture machine the whole harness runs
in well under a minute; on a slower one it will take several.

No timing is asserted anywhere, so a slow machine changes nothing about
whether it passes. If you want a faster loop while developing, call the
library functions directly with a smaller `replications` or `repeats`
argument — both are parameters — and put them back before running the
harness.

## My group-aware score is below 0.5 and that looks broken

It is not, and exercise 3 asserts it. Each person's label in
`grouped_dataset` is a coin flip, so there is genuinely nothing to learn
about a person you have not met. About twelve people land in the
group-aware test half, each contributing twenty identical labels, so the
estimate is effectively a dozen coin flips and it wanders.

The structural claim the lab makes is the one worth defending: the
group-aware score sits below 0.5 while the row-wise score sits far above
it. If those have swapped, something is genuinely wrong.

## My temporal numbers differ from the lesson's

Almost certainly fine, and the lesson says so at length. The effect varies
by a factor of sixteen across constructions — +0.016 to +0.2557 — which is
why exercise 4 asserts only the direction and exercise 4b asserts the
whole distribution rather than a single figure.

What must hold on any version is that shuffling beats chronology in every
construction. If it has stopped doing that, investigate properly rather
than adjusting the assertion.

## `sqrt(2 ln K)` does not match the measured optimism

Correct, and asserted. It is an asymptotic approximation to the expected
maximum of K normals, and it is loose at every K you will actually use. At
K=100 it says 3.03 standard errors where the simulated expectation is 2.50
and the measurement is 2.57.

The lab asserts that the approximation *exceeds* the simulated
expectation, not that it equals the measurement. Treating the closed form
as the truth here would be quoting a formula over a measurement, which is
the one thing this course does not do.

## The selection-bias numbers move on my machine

Read `expected-output/FIELDS.md`. Every figure in that curve is an average
over seeded draws from `numpy.random.default_rng`, and NumPy's
documentation is explicit that `Generator` gives no stream-compatibility
guarantee between versions.

What must hold anywhere: the validation column increases in K, the test
column does not move, and the test column sits at chance. Harness check 8
confirms the selection optimism survives a different replication count, so
it is not an artefact of the 400.

## `LogisticRegression` warns about convergence

`max_iter=1000` is set everywhere in this lab specifically to avoid this.
If you construct your own with the default of 100 you may see a
`ConvergenceWarning` and slightly different scores. Match the library's
settings, or use its helpers directly.
