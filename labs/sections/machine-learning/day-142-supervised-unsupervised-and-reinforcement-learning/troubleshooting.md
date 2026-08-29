# Troubleshooting

## `No lab .venv found at .venv/bin/python3`

The harness refuses to run against whatever Python happens to be on your
`PATH`, because the numbers in this lab are pinned to exact package
versions. Build the environment first:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you deliberately want to use a different interpreter, the harness
honours `PYTHON` and `PYTEST`:

```bash
PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh
```

Expect version-check failures if those tools do not match the pins. That
is the harness working, not the harness breaking.

## `numpy installed=… pinned=2.5.2`

Check 1 compares what is installed against `requirements/requirements.txt`
and fails loudly rather than letting you compare numbers that were
produced under different conditions. Either install the pinned versions,
or read `expected-output/FIELDS.md` first: it separates the results that
hold everywhere from the ones that hold only under the pins. If you are
on a different NumPy and only the sampled figures moved, nothing is
broken — the lab is telling you the truth about what seeding does and
does not guarantee.

## `import file mismatch` when running pytest

You ran `pytest examples starter` in one invocation. Both directories
contain modules with the same names, so pytest cannot decide which
`feedback_lib` a test meant. Run them separately:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

Check 5 of the harness deliberately asserts that the combined invocation
fails, so that this is documented behaviour rather than a surprise.

## My exercise 7 agent never reaches the goal

That is the point of exercise 7, and it is worth understanding rather
than working around. `np.argmax` returns the lowest index attaining the
maximum. A Q-table initialised to zeros makes every row one enormous tie,
so the greedy branch of your ε-greedy policy always chooses action 0 —
which in `GridWorld.ACTIONS` is "up". With ε = 0.2 the agent takes a
biased random walk that never leaves the top of the grid, and 200-step
episodes time out forever.

Pass `break_ties_randomly=True` (the default) to get an agent that
learns, and `break_ties_randomly=False` to reproduce the failure. Both
are asserted, because the contrast is the lesson.

## The bandit numbers do not match on my machine

Check `expected-output/FIELDS.md`. Every bandit figure comes from a
seeded `numpy.random.default_rng`, and NumPy's documentation is explicit
that `Generator` gives no stream-compatibility guarantee between
versions. A different NumPy can legitimately produce different draws from
the same seed.

What must still hold on any version is the *ordering*: ε = 0.1 beats
ε = 0.01 beats greedy, on both mean reward and optimal-action rate. If
that ordering has inverted, something is genuinely wrong. If only the
fourth decimal has moved, the pins are doing their job.

## Exercise 9's single-split curve is not monotone

Correct, and asserted as such. On split 142 alone, five random labels
score 0.92 and twenty score 0.86. Fifty rows of test data cannot resolve
a few points of accuracy, which is Day 117's standard error arriving in a
new setting. The averaged curve over 40 splits *is* monotone, and the lab
asserts both so the difference is visible rather than smoothed away.

## `KMeans` warns about memory leaks on my machine

Some builds of scikit-learn emit a warning about `KMeans` and OpenMP
thread counts on Windows with certain MKL versions. It does not affect
any value in this lab. If you want it silenced, set `OMP_NUM_THREADS=1`
in your environment before running.

## The harness leaves nothing behind but my editor shows `__pycache__`

The harness clears caches at the **start** of the run as well as the end,
so the final cleanliness check measures what that run left rather than
what a previous manual `pytest` invocation left. If you run pytest by
hand afterwards you will create them again; that is expected, and the
cleanup commands in `metadata.yml` remove them.
