# Day 107 lab — Choose Your Distance on Purpose

One idea holds this whole lab together:

> **"Distance" is not one thing. It is a family, and choosing a member is a
> modelling decision with consequences you can see.**

Everything below is a consequence of that sentence. You will implement five
measures from arithmetic you can check on paper, watch three of them name three
different winners on the same four numbers, prove that one of the most popular
of them is not a metric, and then find that the answer changes again when you
divide two columns by their own standard deviations.

Work in order; each exercise uses the one before it.

Check yourself at any point, from the **lab directory** (the one above this
file):

```bash
.venv/bin/pytest starter -q
```

Unattempted work is **skipped**, not failed. On an untouched checkout you will
see `1 passed, 71 skipped`. When it says `72 passed`, you are finished.

---

## The data

Nothing is downloaded. `catalogue.py` holds five small hand-written datasets,
every number small enough to check without a calculator. Read it first — every
exercise refers to it.

| Dataset | What it is for |
| --- | --- |
| `QUERY` and `ARTICLES` | The opening disagreement: four term counts, three articles, three different winners. |
| `FLOOR_FROM` / `FLOOR_TO`, `MEASURED_PARTS` | Where Manhattan, Euclidean and Chebyshev are each the only correct answer. |
| `REFERENCE_RECORD`, `CANDIDATE_RECORDS`, `FLAGS_A/B` | Categorical and binary data, which is what Hamming is for. |
| `RECIPE_QUERY`, `RECIPES` | Sets, where Jaccard and cosine give opposite answers. |
| `SENSOR_READINGS`, `PROBE_ALONG`, `PROBE_ACROSS` | Two points Euclidean distance cannot tell apart and Mahalanobis can. |
| `BEARINGS`, `BEARING_QUERY` | Two features in mismatched units, where scaling decides the winner. |

There is one seeded random generator in the lab,
`numpy.random.default_rng(107)` in `examples/06_scaling_changes_the_answer.py`,
and it is used only to show that the scaling effect is not a property of the
six hand-picked bearings. Every number asserted to the last decimal place comes
from the literal tables.

---

## The two conventions, and the one that will trip you

**1. A distance shrinks as things get more alike. A similarity grows.**

`l1_distance`, `l2_distance`, `linf_distance`, `hamming_distance` and
`mahalanobis_distance` are distances: **smaller is better**.
`cosine_similarity` and `jaccard_similarity` are similarities: **larger is
better**.

Nothing in this module guesses which you meant. `rank` takes an explicit
`higher_is_better` flag, and getting it backwards returns the *worst* match at
the top of your results with no error message anywhere. This is not a
hypothetical: it is one of the most common bugs in a first retrieval system,
and it is invisible because the output still looks like a ranked list.

**2. Use only the standard library inside `measures.py`.**

`math`, `abs`, `sum`, `max`, `sorted` and set operations are everything you
need. NumPy appears in the *tests*, where it is the independent answer —
`numpy.linalg.norm(v, ord=p)` is exactly the p-norm family you are about to
write, and agreeing with it to 1e-12 means something only if your answer was
not NumPy's answer to begin with.

---

## Exercise 1 — the measures (`measures.py`)

Seventeen functions. Each has a docstring with a worked example.

| # | Function | The one thing to get right |
| --- | --- | --- |
| 1.1 | `l1_norm` | Absolute values, then sum. |
| 1.2 | `l2_norm` | `math.sqrt` of the sum of squares. |
| 1.3 | `linf_norm` | `max(..., default=0.0)` — the empty case raises without it. |
| 1.4 | `p_norm` | `p = math.inf` is the LIMIT, not arithmetic. `p < 1` must raise. |
| 1.5 | `l1_distance` | Use `_paired`, not bare `zip`. |
| 1.6 | `l2_distance` | |
| 1.7 | `linf_distance` | |
| 1.8 | `cosine_similarity` | The zero vector has no direction: raise, do not return 0. |
| 1.9 | `hamming_distance` | Count, do not subtract. Return an `int`. |
| 1.10 | `jaccard_similarity` | Two empty sets are 1.0 by convention. State it, do not divide by zero. |
| 1.11 | `to_binary_vector` | Floats, not booleans. |
| 1.12 | `column_means` | |
| 1.13 | `column_stds` | Population divisor `n`, not `n - 1`. |
| 1.14 | `standardise` | Use the supplied `means`/`stds` when given. A zero-spread column stays 0.0. |
| 1.15 | `covariance_matrix` | Divide by `n`. The answer on the sensor readings is exactly `[[7.5, 7.0], [7.0, 7.5]]`. |
| 1.16 | `mahalanobis_distance` | `sqrt(z . (cov_inverse . z))`. Clamp a tiny negative to 0. |
| 1.17 | `rank` | Sort on a TUPLE so ties break by name. |

Written for you: `_paired`, `dot`, `minkowski_distance`, `cosine_distance`,
`normalised_hamming`, `jaccard_distance`, `vocabulary`, `transpose`, `matmul`,
`mat_vec`, `inverse` and `winner`. Gauss-Jordan elimination is a day of its
own; you built matrix multiplication on Day 101.

### The order that will hurt least

1. `l1_norm`, `l2_norm`, `linf_norm` — three one-liners, and the tests for the
   distances depend on nothing else.
2. `p_norm` — then check that it reproduces all three.
3. The three distances, then `cosine_similarity`.
4. `hamming_distance`, `jaccard_similarity`, `to_binary_vector`.
5. `rank`. Everything above becomes visible the moment this works.
6. `column_means`, `column_stds`, `standardise`.
7. `covariance_matrix`, then `mahalanobis_distance`.

---

## Exercise 2 — the predictions (`answers.py`)

Twenty-five values. **Write your answer before you run anything.** A prediction
you got wrong teaches more than a result you read, and every one of these can
be worked out on paper or reasoned about from the docstrings.

Four of them are worth thinking about rather than computing:

- **2.12** — does the p-norm rise or fall as `p` grows? Try `p = 1` and
  `p = 100` on `(3, 4)` in your head before you decide.
- **2.13** — which axiom does *squared* Euclidean distance break? There are
  four candidates and only one survives contact with doubling a vector.
- **2.15** — does the triangle inequality hold for cosine distance? The triple
  is `(1, 0)`, `(1, 1)`, `(0, 1)`, and the answer is the reason Day 103's
  result matters.
- **2.22** — are the two probe points the same Euclidean distance from the
  mean? Look at the two coordinates rather than reaching for a calculator.

---

## When you are finished

```bash
.venv/bin/pytest starter -q          # should say 72 passed
bash tests/run_tests.sh              # the whole lab, 60 checks
```

Then read `examples/`, in order 01 to 06. The reference implementation is
`examples/measures.py`, and the six scripts are the argument the day makes:
three winners, the unit balls, the metric axioms, the four data shapes,
Mahalanobis, and the scaling that changes the answer.

Reading them before you have attempted the exercises is allowed and is a waste
of the exercise.
