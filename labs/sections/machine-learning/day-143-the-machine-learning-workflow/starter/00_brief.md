# Day 143 lab brief — The Workflow, Wired Up

The machine learning workflow is normally drawn as a row of boxes with
arrows between them. Everybody nods. Then everybody goes and writes a
notebook where the boxes are cells, the arrows are the order you happened
to run them in, and the whole thing produces a number that nobody can
reproduce and nobody can defend.

This lab builds the same workflow with the arrows made load-bearing.
Every stage declares **what it requires** and **what it produces**, the
runner refuses to run a stage whose inputs are absent, and every run
leaves a step log and a manifest of content hashes behind it.

## The claim you are here to measure

> The same stages in a different order give a different answer, and the
> wrong order is silent.

Exercise 3 does it in five lines. A dataset of 100 rows and 5000
features, where the labels are coin flips and no feature carries any
information whatsoever:

| Pipeline | Order | Score |
| --- | --- | --- |
| honest | load, **split, select**, fit, baseline | **0.50** |
| leaky, contracts off | load, **select, split**, fit, baseline | **0.73** |
| leaky, contracts on | same as above | `StageContractError` |

Twenty-three accuracy points, on data that contains nothing to learn,
produced by transposing two stages. Same data, same model, same folds,
same seed. Nothing raises. Nothing warns. A number comes out and it looks
like a result.

And then the third row, which is the actual lesson:

```
StageContractError: stage 'select' requires ['folds'] which no earlier
stage produced
```

The contract is not ceremony. It is what turns a silent twenty-three
point lie into a loud error naming the stage that broke.

## The thing to understand about that contract

Look carefully at how `leaky_stages()` is written. Its `select` stage
still declares `folds` among its requirements — because that requirement
is **true**. Choosing features is a per-fold operation. Declaring it
honestly is the entire mechanism by which the runner can notice.

A team that writes `requires=("X", "y")` on that stage has not been caught
out by a subtle bug. They have written down a claim that is false, and
every checking tool in the world is downstream of that.

## Six more things this lab measures

| # | What it establishes |
| --- | --- |
| 1 | The pipeline as stages with a step log, and stages that never mutate their input |
| 2 | The honest pipeline reports chance on data that is chance |
| 3b | The inflation grows with the number of features chosen: +0.26, +0.22, +0.23, +0.47 |
| 4 | The metric decides which model you ship — accuracy and recall pick different winners |
| 5 | A 94.35 percent accurate model that misses more positives than it catches |
| 6 | Two runs of the pipeline are byte-identical; a different seed is not |
| 7 | The modelling stage is 30 percent of this pipeline, and that is an upper bound |

Exercise 4 is the one to sit with. On an imbalanced problem — 8 percent
positive — a majority-class baseline scores **0.92 accuracy with zero
recall**, and three of the four real models beat it by at most 2.35
points. The one model that actually finds most of the positives, at 0.8438
recall, scores **worse than the constant** on accuracy.

Choosing the metric is therefore not a reporting decision made at the end.
It is the decision that determines which model you ship, and you make it
before any model exists.

## How to work

1. Build the environment (see the lab `README.md`).
2. Run `.venv/bin/pytest starter -q`. You will see four passes (the
   machinery checks in `test_workflow_lib.py`) and thirteen skips.
3. Replace one `pytest.skip(...)` at a time with real code. The skip text
   names the exact helper and the exact value to assert.
4. Print the measured pair in every exercise. A number you did not print
   is a number you did not look at.
5. When you want the whole measured table at once, run
   `.venv/bin/python3 examples/report_measurements.py`.

Do not run `pytest starter examples` in one invocation. Both directories
define `workflow_lib.py`, `test_workflow_lib.py` and
`test_workflow_claims.py`; pytest aborts on the module-name collision.
Run them separately, always.

## A note on the honest score being 0.50

It is 0.50 because the labels are coin flips, and that is the correct
answer. But the five per-fold scores behind it are `[0.5, 0.55, 0.5, 0.4,
0.55]`, which is a wide spread — twenty test rows per fold buys you a
standard error of roughly 0.11.

Two of the honest scores in the `inflation_by_k` table are *below* chance,
at 0.39 and 0.38. That is not anti-learning and it is not a bug. An
estimate of a 0.5 quantity from a small sample wanders, and it wanders
below as readily as above. The lab therefore asserts `right <= 0.5`
rather than `right == 0.5`, because the structural claim is the one worth
asserting.
