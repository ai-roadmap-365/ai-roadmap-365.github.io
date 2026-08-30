# Troubleshooting — Day 360

## Every small window pages

You are evaluating the rules before checking the sample size. The `min_sample` check must come **first** and return immediately — one failure in three requests is a 33 percent error rate, and paging on it is how a channel gets muted.

## The p50 of `[1, 2, 3, 4, 100]` comes out as 2

You used `round` for the nearest-rank calculation. Python rounds halves to even, so `round(2.5)` is 2 and you land on the wrong observation. Use `math.ceil`.

## `test_p95_cannot_see_a_single_outlier_in_twenty_samples` fails

Read the test before changing the code — it asserts that p95 over twenty samples is **200**, not 9000, and that is correct. Nearest rank puts p95 at the nineteenth value, so a single outlier sits above it. If your implementation returns 9000 you are computing a maximum rather than a percentile.

## The cost alert stops firing after the first spike

Your baseline is a mean, and the spike raised it enough to make the next one look normal. Use a median, which is unmoved by a single outlier. This failure is self-concealing, which is why it has its own test.

## A spend spike alerts on the very first window

There is no baseline yet, so there is nothing to compare against. `rolling_baseline` should return `None` for an empty history, and `evaluate` should skip the cost rule when the baseline is `None`. Inventing a fixed threshold instead would either never fire or always fire.

## `ZeroDivisionError` on an empty window

A window with no requests is a normal state, particularly at the edges of a traffic period. Guard every denominator and return zeros.

## Ungrounded answers never warn

Check that your generator is actually producing them, and that the rule compares against `ungrounded_budget` rather than the error budget. The point of this rule is that it fires while `error_rate` is zero — if both move together, you are measuring failures rather than quality.

## The demo numbers do not match

Traffic is generated from a seeded RNG, so a correct implementation reproduces the table exactly. Differences usually come from the percentile rank calculation or from bucketing boundaries — windows are half-open, `start <= at < end`.

## `NotImplementedError` on nearly every test

Expected. The starter stubs four functions — see `expected-output/starter-run.txt`, which also names the one test that passes without them.
