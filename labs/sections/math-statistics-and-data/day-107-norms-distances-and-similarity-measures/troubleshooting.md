# Troubleshooting — Day 107 lab

Every failure below is one that was actually hit while building this lab, or
one the tests were written specifically to catch. Each says what you will see,
what causes it, and how to confirm the fix.

---

## `OverflowError` or `inf` from `p_norm` at `p = math.inf`

**You will see:** `test_1_04_p_norm_reproduces_the_three_named_norms` fails
with `inf`, or an `OverflowError: (34, 'Result too large')`.

**Cause:** you computed the infinity case as arithmetic. `4.0 ** math.inf` is
`inf` for any base above 1, and `inf ** 0.0` is `1.0`, so the formula does not
degrade gracefully — it returns nonsense.

`p = infinity` is a **limit**, not a value to substitute. As `p` grows, the
largest component dominates the sum so completely that the `p`-th root gives it
back on its own.

**Fix:**

```python
if math.isinf(p):
    return max((abs(x) for x in v), default=0.0)
```

**Confirm:** `p_norm((3.0, 4.0), math.inf)` is `4.0`, and
`p_norm((3.0, 4.0), 64)` is `4.000000001` — the limit arriving early, which is
the sanity check that the two agree.

---

## `ValueError: max() arg is an empty sequence`

**You will see:** `test_1_03_linf_norm` fails on the second assertion, the one
for the empty vector.

**Cause:** `max(())` raises. Every other norm of the empty vector is naturally
0 — `sum` of nothing is 0 — and L-infinity has to be told.

**Fix:** `max((abs(x) for x in v), default=0.0)`.

This matters more than it looks. An empty vector is not an exotic case; it is
what a feature extractor returns when a document had none of the terms in your
vocabulary, and a crash there is a crash in production on the emptiest input
you have.

---

## `pytest starter` reports a *failure* on `p_norm`, not a skip

**You will see:** `pytest.fail("p_norm(v, 0.5) should raise ValueError...")`.

**Cause:** you implemented `p_norm` and it happily computed an answer for
`p = 0.5`.

**This is not a rounding detail.** Below `p = 1` the formula still produces a
number, and that number is not a norm: the unit "ball" becomes a four-pointed
star, and the triangle inequality fails. Returning a plausible float there is
worse than refusing, because it will be used.

**Fix:**

```python
if p < 1:
    raise ValueError(f"p must be at least 1 to be a norm; got {p}")
```

**Confirm:** `02_the_p_norm_family.py` prints the refusal at the end of section
4 and exits 0.

---

## The two Mahalanobis numbers differ in the last digit

**You will see:** the value `5.999999999999999` where you expected `6.0`, or
the reverse.

**This is correct behaviour and not a bug.** The lab computes the same quantity
two ways and prints both:

```
via measures.inverse   (Gauss-Jordan)  6.0
via numpy.linalg.inv   (LAPACK)        5.999999999999999
difference                             8.882e-16
```

Both routes are correct. They add the same numbers in a different order, and
IEEE 754 addition is not associative, so the last bit lands differently. The
harness asserts that *both* are within 1e-12 of 6.

**What to do about it:** nothing, except never write `== 6.0` in a test over a
float you did not personally construct. This example exists in the lab
precisely so that the tolerance rule stops being an abstract instruction.

If your two values are swapped, or both come out exactly 6.0, nothing is
broken; `expected-output/FIELDS.md` explains what is and is not guaranteed.

---

## `math domain error` from `mahalanobis_distance`

**You will see:** `ValueError: math domain error` raised inside `math.sqrt`,
usually for two points that are the same or nearly the same.

**Cause:** the value under the square root should be exactly 0 and came out as
about `-1e-17`. A covariance matrix is positive semi-definite, so this cannot
happen in real arithmetic and always can in floating point.

**Fix:** clamp a tiny negative, and refuse a genuinely negative one:

```python
if squared < 0.0:
    if squared < -TOL:
        raise ValueError("the matrix supplied is not a valid inverse covariance")
    squared = 0.0
```

Do not use `abs(squared)`. That would silently turn a real error — being handed
a matrix that is not an inverse covariance at all — into a plausible distance,
which is the failure mode the guard exists to prevent.

**Confirm:** `test_6_06_mahalanobis_clamps_a_tiny_negative_rather_than_raising`
passes, and `test_9_10` still raises for the deliberately invalid matrix
`[[-1, 0], [0, -1]]`.

---

## `column_stds` is close but not equal to NumPy's

**You will see:** `test_5_02_column_stds_use_the_population_divisor` fails with
two numbers that agree to about one part in ten.

**Cause:** you divided by `n - 1` instead of `n`.

Both are correct answers to different questions. `n` (the *population*
divisor) describes the table in front of you. `n - 1` (the *sample* divisor)
estimates the spread of a wider population you are sampling from.

This lab uses `n`, because that is what `numpy.std` does by default and what
scikit-learn's `StandardScaler` does, and because the tests check against
those. On six rows the difference is about 9.5 per cent, which is easily large
enough to move a ranking.

**Confirm:** `test_5_03_column_stds_are_not_the_sample_divisor` passes too. It
exists so that "close enough" does not slip through.

---

## Standardising made every value zero

**You will see:** every candidate at distance 0, or all distances equal.

**Cause:** you standardised the query against itself. A single row has mean
equal to itself and standard deviation 0, so the z-score of every column is 0.

**Fix:** compute the means and standard deviations from the **catalogue**, then
pass them in when standardising the query:

```python
means = column_means(rows)
stds = column_stds(rows)
q = standardise([query], means, stds)[0]
scaled = {n: standardise([v], means, stds)[0] for n, v in candidates.items()}
```

This is exactly the mistake `sklearn`'s `fit` / `transform` split exists to
prevent, and it is why `standardise` takes optional `means` and `stds` at all.

**Confirm:** `test_8_08_standardising_a_query_against_itself_would_give_zeros`
in the reference suite documents the failure mode, and
`test_5_07_standardising_changes_the_bearing_winner` in the starter suite is
the one that proves you did it correctly: raw picks `R`, standardised picks
`P`.

---

## `ZeroDivisionError` in `standardise`

**Cause:** a column with no spread at all — every row the same value.

**Fix:** compare against `TOL`, not against `0.0`, and return `0.0` for that
column. A constant column carries no information, so scaling it is meaningless
rather than merely awkward.

```python
0.0 if sd[j] <= TOL else (row[j] - mu[j]) / sd[j]
```

---

## `ZeroDivisionError` in `jaccard_similarity`

**Cause:** both sets empty, so the union is empty and the denominator is 0.

There is no derivable answer here — `0/0` is not 1 and is not 0. It is a
**convention**, and this lab picks similarity `1.0`: two empty things are
alike. State it in the docstring, as the reference does, so that the next
reader knows a decision was made rather than an accident.

**Confirm:** `test_4_04_jaccard_basic_cases` includes the empty case.

---

## Ranking results move between runs

**You will see:** two candidates swapping places on identical data.

**Cause:** two candidates scored exactly equal and your sort broke the tie by
dictionary order, which is insertion order, which changed.

**Fix:** sort on a **tuple**, so equal scores fall back to the name:

```python
scored.sort(key=lambda pair: (-pair[1] if higher_is_better else pair[1], pair[0]))
```

**Confirm:** `test_7_04_ties_break_by_name` puts three identical candidates in
and expects `["alpha", "mike", "zulu"]`.

---

## The ranking is upside down

**You will see:** the least similar item at the top, and no error anywhere.

**Cause:** `higher_is_better` was left at its default for a *similarity*.
`cosine_similarity` and `jaccard_similarity` grow as things get more alike;
every other measure here shrinks.

This is the most consequential bug in the whole lab, because the output still
looks like a ranked list. Nothing crashes and nothing warns. It is worth
looking at your own retrieval code today.

**Confirm:** `test_7_03_rank_descends_for_a_similarity` and
`test_3_05_cosine_picks_cartogram` in the reference suite.

---

## `pytest starter` reports failures instead of skips

**You will see:** `NotImplementedError` in the failure output rather than a
skip, or an import error.

**Two causes.**

1. **You deleted a `raise NotImplementedError` without writing a body.** The
   skip mechanism works by catching that exception; remove it and the test sees
   `None` returned and fails on the assertion instead. Either write the
   function or leave the `raise` in place.

2. **You ran pytest from inside `starter/`.** Run it from the **lab
   directory**:

   ```bash
   cd labs/sections/math-statistics-and-data/day-107-norms-distances-and-similarity-measures
   .venv/bin/pytest starter -q
   ```

**Confirm:** an untouched checkout prints `1 passed, 71 skipped`.

---

## The starter tests pass work you have not written

**You will see:** `pytest` (with no argument) reports far fewer skips than
`pytest starter` does — possibly `0 skipped`.

**Cause:** a missing or edited `conftest.py`. `examples/` and `starter/` both
contain modules named `measures` and `catalogue`. pytest imports test files by
putting their directory on `sys.path`, so collecting both suites at once lets
whichever `measures` was imported first serve both — and your unwritten
exercises then "pass" against the reference solution. A wrong answer with a
green tick on it is the worst kind of test result.

**Fix:** restore both `conftest.py` files.

```bash
git checkout -- starter/conftest.py examples/conftest.py
```

**Confirm:** section 4 of `tests/run_tests.sh` checks exactly this — the skip
count must be identical whether you run `pytest starter` or bare `pytest`.

---

## `pytest not found` from the harness

**You will see:**

```
FAIL: pytest not found.
```

**Cause:** the virtual environment was never created, or you are running the
harness from somewhere else.

**Fix:** either install into `.venv` inside the lab:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

or point the harness at an existing pytest:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The harness uses the `python3` sitting beside that `pytest`, because that is
the interpreter NumPy is installed into. If NumPy is not importable from it,
the harness stops and says so rather than quietly skipping checks.

---

## The versions do not match `requirements.txt`

**You will see, in section 1 of the harness:**

```
FAIL: installed numpy matches requirements.txt (expected [2.5.2], got [2.4.1])
```

**This is the harness doing its job**, not a failure of your work. It reads the
installed version rather than assuming it, so a mismatch is reported at the top
of the run instead of surfacing later as a confusing diff.

**Fix:** `.venv/bin/pip install -r requirements/requirements.txt` again, or
accept the difference knowingly. Read `expected-output/FIELDS.md` first — one
measured result, the count of 1090 in the seeded sweep, is tied to this NumPy
build's random stream.

---

## My seeded sweep gives a different number from 1090

**You will see:** section 5 of the harness fails on
`in 2000 seeded random catalogues the winner changed 1090 times`.

**This may not be your fault, and the lab says so.**
`numpy.random.default_rng(107)` is reproducible on a given NumPy build, and
NumPy's documentation declines to guarantee the exact stream across versions.

The claim that actually matters is the check beside it: the proportion must
land between 35 and 75 per cent, and that is what
`06_scaling_changes_the_answer.py` asserts. If that passes and only the exact
count differs, your NumPy draws different numbers and the lab's argument is
untouched. Record what you observed.

Every number asserted to the last decimal place elsewhere in this lab comes
from the literal tables in `catalogue.py` and does not depend on the generator
at all.

---

## Something is left behind after a run

Section 7 of the harness checks for `__pycache__`, `.pytest_cache` and any data
file anywhere under the lab, **excluding `.venv`**. If it reports one:

```bash
find . -name '.venv' -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Note the `-name '.venv' -prune` in that command, and in the harness. NumPy
ships 113 `__pycache__` directories of its own inside `.venv`, and the README
tells you to create `.venv` — so a check that did not prune it would fail the
lab for following its own installation instructions. The harness was verified
to exit 0 both with a `.venv` present and without one.

The harness exports `PYTHONDONTWRITEBYTECODE=1` and passes `-p no:cacheprovider`
to pytest, so a normal run leaves nothing. A data file appearing under the lab
means either something was committed by mistake or a script wrote one — and
nothing in this lab writes any file at all.
