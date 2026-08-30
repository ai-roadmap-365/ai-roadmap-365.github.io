# Troubleshooting — Day 364

## `NotImplementedError` on every test

Expected. The starter stubs eight functions and `Task.ratio` is one of them, so nothing computes until task 1 is done. See `expected-output/starter-run.txt`.

Fix them in order. Task 2, the median, is the one everything else depends on.

## One bad task dominates the calibration

You are computing a mean. A single task that ran eight times over will pull an average far above the typical task and make the whole project look worse than it was, which is exactly the distortion the median exists to avoid.

## `test_median_of_an_even_count_averages_the_middle_two` fails

Your median returns `ordered[len(ordered) // 2]` unconditionally. For an even count there is no single middle element, so average the two either side.

## `is_uniform` returns `True` for the concentrated fixture

You are comparing each area against the overall median. Compare the **highest area against the lowest**. The overall median is itself pulled by whichever area contributed more tasks, so measuring against it answers a weaker question.

Measured on the demo record, the highest-to-lowest ratio is 2.909, so a 1.5x threshold reports `False`. If yours reports `True`, check the threshold as well as the comparison — anything at 3.0 or above calls this record uniform.

## Every incident counts as escaped

`STAGING` is not an escape. The code was deployed and reached nobody, which is the whole reason a staging environment exists. Only `MONITORING` and `USER` are escapes, and using `STAGE_RANK` to compare against `MONITORING` keeps that decision in one place.

## A task with a zero estimate raises `ZeroDivisionError`

A task nobody estimated is a real entry in a real record, so `ratio` must return `0.0` rather than raising. This is task 1 for a reason.

## `test_calibration_counts_direction_not_just_size` fails

A task at exactly 1.0 is neither under-estimated nor over-estimated. If your counts add up to the number of tasks on a record containing an exact estimate, you are using `>=` or `<=` somewhere.

## `worst_area` and `best_area` come back the same

With a single area that is correct — the highest and lowest of one value are the same value. On multi-area input, check that you are taking `max` and `min` over the **area medians** rather than over the raw task ratios.

## `apply_multiplier` returns a long float

Round to one decimal. `4 * 1.2` is `4.800000000000001` in binary floating point, and an estimate printed to fifteen decimal places suggests a precision the number does not have.

## The findings list is empty on a project that clearly went badly

Check that `findings` calls `calibration` and `detection` rather than reimplementing them, and that the concentrated-error branch is not nested inside the multiplier branch. On a record where estimates were accurate but incidents escaped, the multiplier finding correctly does not fire and the escape findings still must.

## The report invents a finding on a clean record

The opposite failure, and the more damaging one. If nothing fired, say so. A retrospective tool that always produces a finding trains people to ignore its findings.
