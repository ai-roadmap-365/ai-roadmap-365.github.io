# Day 104 lab — Stop Writing the Loop

One idea holds this whole lab together:

> **A vectorised expression is the SAME computation as the loop, not a
> different one — you have moved the loop, not removed it.**

Everything below is a consequence of that sentence, including the parts where
the trade turns out to be a bad one.

Work in order; each exercise uses the one before it.

Check yourself at any point, from the **lab directory** (the one above this
file):

```bash
.venv/bin/pytest starter -q
```

Unattempted work is **skipped**, not failed. On an untouched checkout you will
see `1 passed, 70 skipped`. When it says `71 passed`, you are finished.

---

## Exercise 1 — `vectorize.py` (ten functions)

Write the ten functions marked `raise NotImplementedError`. Each docstring
gives the derivation and a worked example you can check on paper.

| Step | Function | What it must do |
| --- | --- | --- |
| 1.1 | `scale_and_offset_loop` | `m * x + c`, as an explicit Python loop. No NumPy in this one. |
| 1.2 | `scale_and_offset_vec` | The same, as one expression on the whole array. |
| 1.3 | `roots_loop` | Square roots, as a loop. Use `math.sqrt`, and read why. |
| 1.4 | `roots_vec` | The same, as one call to a universal function. |
| 1.5 | `clip_loop` | Hold every value inside `[lo, hi]`, as a loop. |
| 1.6 | `clip_vec` | The same, in one call. |
| 1.7 | `count_above` | How many elements beat a threshold — no counter variable. |
| 1.8 | `mask_between` | A boolean array, True where `lo < x < hi`. |
| 1.9 | `top_k_indices` | The positions of the `k` largest, best first. |
| 1.10 | `cosine_similarities` | Day 103's search, done to every row at once. |

Nine helpers are written for you at the bottom of the file — `list_bytes`,
`array_bytes`, `wrap_int8`, `nan_aware_mean`, `select`, `time_call`,
`median_seconds`, `speedup` and `describe`. Read them; the tests use them, and
`list_bytes` in particular carries a fact you will need in exercise 2.

**The gotcha in 1.3.** Use `math.sqrt(x)`, not `x ** 0.5`. They give different
answers on about one value in seven hundred, and one of the tests compares a
million elements with `==`. Exercise 6.4 is about why, and it is one of the
more interesting things in the day.

**The gotcha in 1.8.** Two of them, actually. It must be `&` and not `and`,
and each comparison needs its own brackets. The docstring explains both, and
exercise 4.6 and 4.7 make you say why.

**The gotcha in 1.10.** `np.linalg.norm(matrix, axis=1)` — think about which
number comes out six times and which comes out four times before you write it.

---

## Exercise 2 — what an array actually is (`answers.py`)

Six predictions about memory and layout.

2.4 is the one worth slowing down for. `sys.getsizeof(list(range(1_000_000)))`
is 8,000,056 bytes and the equivalent int64 array is 8,000,000 — so the naive
measurement says a list is *exactly as compact as an array*, which is the
opposite of everything you have been told. One of those two numbers is not
measuring what you think it is measuring. Work out which before you answer.

2.5 asks for strides. A stride is how many **bytes** you skip to move one step
along an axis. For a 3 by 4 array of int64, moving one column across is one
element, and moving one row down is four.

---

## Exercise 3 — dtypes

Seven predictions, and 3.1 is the famous one. An int8 holds -128 to 127. What
is 127 + 1?

3.2 and 3.3 are the questions that make it matter: does it raise, and does it
warn? Answer both before you run anything. Whatever you expect, the answer is
worth having been wrong about once.

3.5 is subtler. Adding a plain Python `1` — not an int8 — to an int8 array:
which dtype wins? NumPy 2 changed this rule from NumPy 1, so anything you
remember from an older tutorial may be out of date.

---

## Exercise 4 — masking

The twenty readings are printed in `dataset.py` as `SMALL_READINGS_EXPECTED`.
Count by eye; every answer in this exercise can be got without running
anything.

4.6 and 4.7 are the pair the whole day turns on. `(a > 30) and (a < 70)` does
not work. Name the exception class, then say *why* — and note that the reason
is about Python, not about NumPy. NumPy could not fix this if it wanted to.

4.8 is a small one with a large idea inside it: the mean of a boolean array is
the fraction that are True, because `True` is 1 and `False` is 0. Once you see
that, a whole family of "what proportion of..." questions becomes one line.

---

## Exercise 5 — axes, views and copies

5.1 to 5.4 are the axis rule. **The axis you name is the one that
disappears.** If you find yourself reading it as "the axis I want to keep", you
will be off by exactly one every time.

5.5 and 5.6 are the bug. `row = grid[1]` does not give you a copy of row one.
It gives you a window onto row one, and writing through the window writes
through to the array. This is the hardest NumPy bug to find, because the code
that breaks is nowhere near the code that caused it.

5.7 asks which operations give a view. Predict first, then look for the
pattern: it has to do with whether the elements you asked for are **evenly
spaced**.

5.8 is the trap inside the trap: `ravel` and `flatten` do the same job and have
opposite behaviour.

---

## Exercise 6 — sorting, ranking and speed

6.1 to 6.3 are about `argsort`, and about the fact that `np.sort(a)` and
`a.sort()` behave differently — one returns a new array, the other mutates.

6.4 is the honest finding of the lab. Three ways to take a square root, two of
them identical to the last bit and one of them not. Predict which is the odd
one out, then read the reason in `expected-output/FIELDS.md`.

6.5 asks for the order of magnitude of the speedup on a million elements, and
6.6 asks the same question on **four** elements — where the answer reverses.
Both are measurements this lab actually takes.

---

## Exercise 7 — nan

7.1 is the rule everybody meets once: `np.nan == np.nan` is False.

7.4 and 7.6 are the pair that matters. `a.mean()` on an array containing a nan
returns nan. Is that a bug? Think about what the alternative would be: a mean
that silently averaged three readings while you believed it had averaged four,
and never told you.

---

## When you are done

Read the reference. Each script prints its working and asserts every claim it
makes, so nothing in it is decoration:

```bash
cd examples
../.venv/bin/python3 01_list_versus_array.py
../.venv/bin/python3 02_dtypes_and_overflow.py
../.venv/bin/python3 03_same_answer_faster.py
../.venv/bin/python3 04_creating_and_ufuncs.py
../.venv/bin/python3 05_masks_and_selection.py
../.venv/bin/python3 06_axes_views_and_ranking.py
../.venv/bin/python3 07_nan_and_when_not_to_vectorise.py
cd ..
```

Script 07 is the one worth reading even if you stop everything else. The first
half is `nan`. The second half is the honest case against the habit the rest of
the lab has spent an hour teaching you: three situations where the loop is the
better code, all three measured rather than asserted, including one where the
elegant one-line version allocates 80 GB and the ugly loop finishes.

A tool you can only argue for is a tool you do not understand yet.
