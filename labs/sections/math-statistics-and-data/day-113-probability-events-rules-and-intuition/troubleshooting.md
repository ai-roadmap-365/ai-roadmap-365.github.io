# Troubleshooting

Every entry below was hit while building this lab, or is named by a test that
exists because of it.

## `ModuleNotFoundError: No module named 'probability'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `probability`, `simulate` and `dataset` from
beside themselves.

```bash
cd examples
../.venv/bin/python3 01_sample_space_and_events.py
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

If you would rather use an interpreter you already have, the harness accepts
one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## The starter tests all skip and I have written code

A skip means the function still raises `NotImplementedError` or still
returns `None`. Look for a leftover `raise NotImplementedError` below the
code you added — it is easy to write the body above it and leave the raise
in place, so your work never runs at all.

## `probability()` fails a test even though the count looks right

Check the return type. `probability()` must return a `fractions.Fraction`,
not a `float`. `Fraction(1, 6) == 0.16666666666666666` compares `False` for
most fractions because a float cannot represent one exactly, and one of the
day's own points is that this comparison should be exact rather than
"close enough".

## My naive addition-rule sum matches the true union

Then your two events do not overlap. The lesson's worked example uses `A =
"sum is 7"` and `B = "first die is 6"` specifically because their
intersection is a single outcome, `(6, 1)`, which is exactly what makes the
naive sum wrong. If you swap in disjoint events, the naive sum and the true
union are the same number, correctly — the addition rule reduces to plain
addition whenever `P(A and B) = 0`, and `test_addition_rule_reduces_to_naive_sum_for_disjoint_events`
in the reference suite checks exactly that case.

## My `at_least_one` gives a probability greater than 1 or less than 0

You applied the complement rule to the wrong quantity. It is `1 -
P(single failure) ** trials`, not `1 - P(single success) ** trials`. Compute
the failure probability first with `complement()`, raise *that* to the power
of the trial count, and complement the result once more.

## de Méré's two bets look equal to me

They are not, and the gap is the entire point of the exercise. `24 = 6 x 4`
matches the six-times-smaller probability of a double six exactly, and it is
still wrong — `0.5177...` against `0.4914...`, a difference well outside
either simulation's tolerance at 200,000 trials. If your two numbers come out
equal, you probably computed `(5/6)**4` for both bets instead of `(5/6)**4`
for the first and `(35/36)**24` for the second — check which fraction and
which exponent belong to which bet.

## My simulated de Méré probability is outside the stated tolerance

First check the exponent: 4 rolls for the single-die bet, 24 for the
double-dice bet, not the other way round. If the exponents are right and the
gap is still outside `DE_MERE_SINGLE_TOL` or `DE_MERE_DOUBLE_TOL`, print the
tolerance itself — those are three standard errors, `3 x
sqrt(p(1-p)/n)`, and at 200,000 trials they run to about `0.0034`. A
simulation landing just past that is not automatically a bug: about 0.3% of
honest runs will, by construction, land outside a three-standard-error band.
Re-run with a different seed before assuming the code is wrong.

## `is_independent` reports the wrong answer for a pair I believe is independent

Independence is about the numbers, not about how the events sound. "Sum is 7"
and "first die is 3" are independent because *every* value of the first die
leaves the conditional probability of summing to 7 at exactly 1/6 — try
`test_sum_seven_is_independent_of_every_value_of_the_first_die` in the
reference suite, which checks all six values. Most other pairs of dice events
are not independent; "sum is 2" and "first die is 1" fail because sum=2 is
only reachable when the first die shows exactly 1.

## I conflated mutual exclusivity with independence

This is the single most common mistake in the subject, and the lab is built
to make it visible rather than to warn about it in prose. Run
`05_mutual_exclusivity_implies_dependence.py` and watch `P(A | B)` collapse
to exactly 0 for the mutually exclusive pair while it stays unchanged for the
independent pair from exercise 4. If the two events can happen together with
non-zero probability, they might be independent. If they cannot ever happen
together, they are necessarily dependent — knowing one occurred tells you the
other definitely did not.

## My two methods of conditioning (formula vs. filtering) disagree

They should be identical, not approximately equal — both are exact
`Fraction` arithmetic over the same finite space. If they disagree, the
usual cause is restricting the wrong set: `probability(restricted_event,
restricted_space)` needs the *restricted* space as the denominator (the
outcomes where B is true), not the full 36-outcome space.

## My urn's weighted total does not match the enumeration

Check that both urns have the same total number of balls (10 each here).
The direct-enumeration method in this lab treats every `(urn, ball)` pair as
equally likely, which is only valid when the urns are the same size *and*
the prior over urns is uniform. With urns of different sizes or an unequal
prior, the enumeration would need to be weighted, and the two methods would
need a more careful combined space to agree.

## My Monte Carlo error does not shrink smoothly

A single seed at each sample size is not enough — Monte Carlo error is
itself a random variable, so a single run can go the "wrong" way by chance.
This lab averages over twenty seeds at every sample size specifically to
smooth that noise out; if you loosen `MONTE_CARLO_SEEDS` down to one or two
seeds, the trend can look flat or even reversed on an unlucky run. The
reference tests never assert on a single seed's error for this reason.

## Two runs with the same seed give different results

You are calling `numpy.random.seed(n)` somewhere instead of building a
`Generator` with `numpy.random.default_rng(n)`. The legacy `seed()` function
mutates one global state shared across your whole process — importing a
library that seeds it, or calling any other function that also draws from
the global generator, changes what your "same seed" produces next. Pass the
`Generator` object itself into every function that needs randomness, as
`simulate.py` does, and reproducibility stops depending on what else ran
first.

## `__pycache__` or `.pytest_cache` appears and section 5 fails

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
*does* write `starter/__pycache__` and `.pytest_cache` — it has no reason not
to. The harness clears both at the **start** of its run, pruning `.venv`, so
the check at the end measures what *this* run left rather than what an
earlier command left. If you edit `tests/run_tests.sh`, keep that block where
it is.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/` and
`starter/` contain modules called `probability`, `simulate`, `dataset` and
`answers`. Without the `conftest.py` in each directory, collecting both
suites at once would import whichever copy was seen first and reuse it for
the other — so your unwritten starter exercises would silently pass against
the reference solution. A wrong answer with a green tick on it is the worst
kind of wrong answer.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash with
`.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Everything in
the lab is plain arithmetic, standard-library Python and NumPy, so nothing in
it is platform-specific — but "should work" and "was run" are different
claims and only the second one is worth making.
