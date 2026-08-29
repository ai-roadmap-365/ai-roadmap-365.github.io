# Troubleshooting

Every entry below was hit while building this lab, or is named by a check
that exists because of it.

## `ModuleNotFoundError: No module named 'experiment'`

You ran a numbered script from the lab directory instead of from inside
`examples/`. The scripts import `experiment` and `dataset` from beside
themselves.

```bash
cd examples
../.venv/bin/python3 01_load_and_validate.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test
file's own directory on the import path.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. Everything in
this lab goes through `.venv/bin/python3`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you would rather use an interpreter you already have, the harness
accepts one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## The starter tests all skip and I have written code

A skip means the function still raises `NotImplementedError`. Every
function in `starter/experiment.py` has `raise NotImplementedError` as its
body -- replace that line with your own implementation and `return`.

## My `srm_check` passes on B (it should fail)

Two common causes. First: check you are computing `expected_control` and
`expected_treatment` from `n * planned_split`, not from `n_control` and
`n_treatment` themselves -- computing "expected" from the observed counts
makes chi2 zero by construction, every time, on every dataset. Second:
check the comparison direction in `passed` -- the check PASSES when the
p-value is *large* (the split looks consistent with what was planned) and
FAILS when the p-value is *small* (the split looks implausible under the
planned ratio), which is the opposite direction from a normal significance
test where a small p-value is the "interesting" result.

## My `segment_analysis` never flags a reversal on B

Check `reversal_flagged`: it must require **every** segment's sign to
disagree with the pooled sign, not just one. A single segment near zero
(exactly what dataset A's `tablet` segment looks like) should not trip the
flag; three segments all pointing the opposite way from the pooled number,
as in dataset B, should. If your comparison uses `!=` on floats without a
sign function, a segment whose diff is exactly `0.0` will compare unequal
to both a positive and a negative pooled sign in confusing ways -- write a
small `sign(x)` helper that returns `-1`, `0`, or `1` and compare those.

## My `peek_path` checkpoints don't line up with the lesson's numbers

Check that you are walking `rows` in the order they appear in the list
returned by `load_experiment` -- the CSV's row order IS the simulated
arrival order for this dataset, and `csv.DictReader` preserves file order
by default. If you sort, group, or otherwise reorder the rows before
walking them (for example, by `group` or by `user_id`), the checkpoints
describe an experiment that never happened this way.

## My `primary_test` p-value doesn't match the interval's exclude/include zero

You are likely using the pooled proportion's standard error for the
interval instead of the unpooled one, or vice versa for the z-statistic.
The hypothesis test conventionally pools (it assumes the null -- equal
proportions -- to compute the standard error), while the confidence
interval conventionally does not (it estimates the difference under
whatever the data actually show). Using the same standard error for both
is defensible too, but will occasionally make the two checks disagree very
close to the boundary in a way that confuses a reader; the reference
solution keeps them as textbook-conventional and separate.

## `RuntimeWarning` or a p-value that prints as `0.0`

Expected on dataset B's primary test: the true difference is large enough
relative to its standard error (z is close to 9) that `2 * (1 - Phi(z))`
underflows below double-precision's smallest representable positive float
and prints as exactly `0.0`. This is a real, correctly-computed result --
"astronomically significant" -- not a bug. If you want a readable number in
that regime, report `-log10(p)` or simply state "p < 1e-15" instead of the
literal underflowed value.

## `__pycache__` or `.pytest_cache` appears and section 7 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

`.venv` itself ships its own `__pycache__` directories from NumPy and
pytest; those are pruned deliberately and are never treated as litter left
by this lab's own code.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `experiment` and `dataset`. Without the
`conftest.py` in each directory, collecting both suites at once would
import whichever copy was seen first and reuse it for the other -- so your
unwritten starter exercises would silently pass against the reference
solution. A wrong answer with a green tick on it is the worst kind of
wrong answer.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Nothing in
the lab is platform-specific -- but "should work" and "was run" are
different claims and only the second one is worth making.
