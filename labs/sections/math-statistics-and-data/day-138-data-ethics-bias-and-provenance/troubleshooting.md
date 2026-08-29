# Troubleshooting

## `pytest: command not found`, or the harness exits before any check

You have not created the lab's virtual environment, or you are calling
bare `pytest` rather than the one in `.venv`.

```bash
cd labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

The harness looks for `.venv/bin/pytest` first, then anything on your
PATH. To point it at an interpreter of your own:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'ethics'` or `'fixtures'`

You ran pytest from the wrong directory, or named a file instead of a
directory. Run from the lab directory and name the directory:

```bash
cd labs/sections/math-statistics-and-data/day-138-data-ethics-bias-and-provenance
.venv/bin/pytest starter
```

pytest inserts the test file's own directory on `sys.path` (rootdir-based
`prepend` import mode), which is what lets `starter/test_ethics.py` import
`starter/ethics.py` without any package plumbing. Naming the file
directly still works; naming a path from somewhere else does not.

## `import file mismatch` when you run both suites at once

```
import file mismatch:
imported module 'test_ethics' has this __file__ attribute: .../examples/test_ethics.py
which is not the same as the test file we want to collect: .../starter/test_ethics.py
```

Expected, and deliberate. `examples/` and `starter/` both define a module
named `test_ethics.py`, and pytest collects by dotted module name. **Never
run `pytest examples starter` in one invocation.** Run two commands:

```bash
.venv/bin/pytest examples
.venv/bin/pytest starter
```

Section 5 of the harness asserts this collision happens, so that the
failure mode is proven rather than merely warned about.

## `version mismatch: numpy pinned 2.5.2, installed <something else>`

The first check in the harness compares what is installed against
`requirements/requirements.txt` and fails loudly rather than proceeding.
Every numeric assertion in this lab is pinned to a specific NumPy random
stream, so a different NumPy is a real reason to stop.

```bash
.venv/bin/pip install -r requirements/requirements.txt
```

If you deliberately want to run on other versions, expect exercises 1, 3,
4, 6 and 7 to report different numbers. Exercises 2, 5, 8 and 9 have no
randomness in them at all and will be identical anywhere.

## Exercise 1 fails on the variance ratio but passes on the bias

The ratio check asserts the standard deviation falls by more than 2.2×
per tenfold increase in n. With only 40 replicates that ratio is itself a
noisy estimate — the true value is about 3.16 — and a very unlucky draw
can land low. If you changed `replicates` or `seed`, put them back to 40
and 138; those are the values every captured number in `expected-output/`
was produced with. If you are experimenting, raise `replicates` rather
than widening the tolerance: more replicates estimate the ratio better and
cost only time.

The bias assertions, by contrast, should never be borderline. If
`abs(bias_b)` came out near zero rather than near 5.94, you fitted a
per-group model somewhere rather than a pooled one.

## Exercise 5: "surely one of these policies is the right one"

That is the exercise working. Each policy closes its own gap exactly and
opens at least one other, and `any_policy_satisfies_all` is `False`. This
is not a defect in the policies and not a limitation of this lab's
arithmetic — when two groups have different base rates, demographic
parity, equal true-positive rates and equal precision cannot generally all
hold at once.

Which one your system should satisfy depends on what the system is for and
who bears the cost of a wrong decision, and informed people disagree about
it in good faith. The exercise deliberately asserts the incompatibility
rather than a winner. If you find yourself wanting to add an assertion
that one policy is best, write down your reasoning in a comment instead —
that comment is the artifact the day is asking you to produce.

## Exercise 7: "k-anonymity passed, so why is there still a leak?"

Because k-anonymity is a guarantee about **how many people share your
quasi-identifiers**, and says nothing about **what those people have in
common**. `homogeneous_table()` has a class of four people who all carry
the same diagnosis. Nobody was re-identified; membership in the class was
enough. In the literature this is the motivation for l-diversity, and
l-diversity has its own limits in turn.

The lesson to take is not "k-anonymity is useless" — it is that a check
trusted past its stated guarantee is worse than no check, because it buys
confidence it did not earn.

## The suppression count is not 794 on my machine

`suppress_small_classes` is applied to the seeded synthetic register, so
794 is exact for `seed=138`, `n=5000` and NumPy 2.5.2. A different seed,
a different row count, or a NumPy 1.x environment will give a different
number. `expected-output/FIELDS.md` lists which values are pinned to the
seed and which are pure arithmetic.

## `numpy.polyfit` emits a `RankWarning`

Only happens if you reduced the sample sizes far enough that a fit has
too few distinct x values to be well-conditioned — for instance calling
`bias_variance_ladder(sizes=(2,))`. Restore a realistic n; the smallest
size the lab ships with is 500.

## The run left a `.pytest_cache` behind

The harness deletes `__pycache__` and `.pytest_cache` at the start and the
end of every run and asserts that none survive. A bare `pytest starter`
run of your own does not do that cleanup. Remove it yourself, or just run
the harness:

```bash
rm -rf .pytest_cache
find . -path ./.venv -prune -o -type d -name '__pycache__' -exec rm -rf -- {} +
```

## Windows

Everything in this lab is plain Python and one bash script. The Python
half runs unchanged on Windows; `tests/run_tests.sh` needs a bash — Git
Bash or WSL — and the venv paths differ (`.venv\Scripts\python.exe`
rather than `.venv/bin/python3`). Under WSL, follow the Linux
instructions exactly. This lab was run and captured on macOS 26.5.2 on
Apple Silicon; no Windows run is reproduced here, and no claim is made
about one.
