# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'bayes'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `bayes`, `simulate`, `naive_bayes` and
`dataset` from beside themselves.

```bash
cd examples
../.venv/bin/python3 01_opening_posterior.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test
file's own directory on the import path.

## `ModuleNotFoundError: No module named 'numpy'`

You are running the system `python3` rather than the lab's. Everything here
goes through `.venv/bin/python3`:

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

A skip means the function still raises `NotImplementedError` or still
returns `None`. Look for a leftover `raise NotImplementedError` below the
code you added — it is easy to write the body above it and leave the raise
in place, so your work never runs at all.

## My `posterior()` gives 0.99, not about 0.09

You almost certainly returned the sensitivity directly instead of
completing the division. `posterior()` is `(prior x sensitivity) /
evidence`, where `evidence` is the FULL law of total probability sum —
`(prior x sensitivity) + ((1 - prior) x (1 - specificity))` — not just the
numerator. Skipping the denominator, or accidentally returning `sensitivity`
itself, is the single most common way to reproduce the exact misconception
this lesson opens with.

## `posterior()` fails a test even though the decimal "looks right"

Check the return type. `posterior()` must return a `fractions.Fraction`,
not a `float`. `Fraction(99, 1098) == 0.09016393442622951` compares `False`
for most fractions because a float cannot represent the exact rational
value, and the whole point of using `Fraction` throughout this lab is that
comparisons are exact rather than "close enough".

## My prevalence sweep is not strictly increasing

Check that `PREVALENCE_SWEEP` in `dataset.py` is unmodified and that
`posterior()` is being called with the SAME sensitivity and specificity at
every point in the sweep — only the prevalence should vary. If sensitivity
or specificity accidentally changes too (for instance, if you are reusing a
loop variable name that collides with one of them), the sweep can stop
being monotonic.

## My odds-form answer does not match the direct posterior

`likelihood_ratio()` is `sensitivity / (1 - specificity)`, not
`sensitivity / specificity`. The denominator is the FALSE POSITIVE rate —
how likely a positive result is even without the condition — not the true
negative rate. Swapping them gives a plausible-looking but wrong ratio
(here, `99` instead of the correct value, or vice versa if you inadvertently
compute the reciprocal).

## Updating test A then test B gives a different answer from B then A

This should be mathematically impossible if `sequential_posterior()` is
implemented correctly, since it is built entirely from multiplying
`Fraction`s onto a running odds value, and multiplication is commutative. If
your two orders disagree, check that you are re-computing `prior_odds` from
the ORIGINAL prior at the start of each call rather than accidentally
carrying state between the two calls (for instance, reusing a mutable odds
variable across both runs instead of starting fresh each time).

## My naive and correlated posteriors in exercise 7 come out equal

Check `correlation_weight`. If you pass `Fraction(0)` to
`correlated_pair_probability()`, it reduces to exactly
`independent_pair_probability()` by construction — `test_correlated_pair_probability_with_zero_weight_matches_independent`
in the reference suite checks this directly, and it is correct behaviour,
not a bug. `dataset.CORRELATION_WEIGHT` is `Fraction(1, 2)`; if your naive
and correlated numbers are identical, confirm you are actually passing that
constant rather than a literal `0`.

## My naive posterior in exercise 7 is LOWER than the correlated one

You likely swapped which model is "naive" and which is "correct".
`independent_pair_probability()` (naive) assumes full independence and
therefore treats two positive results as twice as much evidence as they
actually are when a shared failure mode is present — it should always be
**higher** than `correlated_pair_probability()`'s more cautious estimate
whenever `correlation_weight > 0`, never lower.

## Everything in my Naive Bayes classifier ties at zero

You are running the unsmoothed classifier (`alpha=0`) on a document that
contains a word absent from one class's training data — this is exactly
exercise 8's veto case, `"please review schedule watches"`, and the ties
are the point, not a bug. If you did not intend to demonstrate the veto,
call `classify()` with `alpha=1` (Laplace smoothing) instead.

## My smoothed and unsmoothed classifiers give the same answer on the veto document

Then smoothing is not actually changing `word_probability()`'s denominator.
Check that `word_probability()` adds `alpha * len(model.vocabulary)` to the
denominator, not just `alpha` — with `alpha=1` and a 17-word vocabulary,
the denominator should grow by 17, not by 1, or the smoothing is too weak
to move the classification away from the unsmoothed (wrong) answer.

## My 500-factor product in exercise 9 does not reach exactly 0.0

Confirm you are multiplying plain Python `float`s in a loop with `*=`, not
using `math.prod` on a generator that short-circuits, and that
`UNDERFLOW_COUNT` and `UNDERFLOW_FACTOR` are unmodified in `dataset.py`
(`500` factors of `0.01`). If you multiply fewer than roughly 150 factors
of `0.01`, the product is still representable and will not underflow — the
underflow specifically needs enough factors that the true product's
magnitude (`10^-1000` at 500 factors) falls below float64's smallest
representable positive value, about `5e-324`.

## `__pycache__` or `.pytest_cache` appears and section 7 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-path ./.venv -prune` in that command, and note that the harness
uses the same prune. NumPy and pytest ship hundreds of their own
`__pycache__` directories inside the virtual environment; those are theirs,
not litter you created. `.venv` itself is the documented setup and is never
treated as a stray file.

You should not actually be able to hit this. The "How to run" section tells
you to run `.venv/bin/pytest starter -q` while you work, and that command
*does* write `starter/__pycache__` and `.pytest_cache` — it has no reason
not to. The harness clears both at the **start** of its run, pruning
`.venv`, so the check at the end measures what *this* run left rather than
what an earlier command left. If you edit `tests/run_tests.sh`, keep that
block where it is.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `bayes`, `simulate`, `naive_bayes`,
`dataset` and `answers`. Without the `conftest.py` in each directory,
collecting both suites at once would import whichever copy was seen first
and reuse it for the other — so your unwritten starter exercises would
silently pass against the reference solution. A wrong answer with a green
tick on it is the worst kind of wrong answer.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash with
`.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Everything in
the lab is plain arithmetic, standard-library Python and NumPy, so nothing
in it is platform-specific — but "should work" and "was run" are different
claims and only the second one is worth making.
