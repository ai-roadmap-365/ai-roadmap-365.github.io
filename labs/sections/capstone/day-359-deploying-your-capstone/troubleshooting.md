# Troubleshooting — Day 359

## A blocked build still changes the live version

You are mutating state before raising. Collect the blockers first, and if there are any, append the `BLOCKED` event and raise **without** touching `live_version` or `traffic_to_new`. A preflight failure must deploy nothing at all.

## `preflight` reports only one problem

You are returning at the first failure. Accumulate all of them into a list and return it. A build with three problems should tell you three things once, rather than sending you round the loop three times.

## A failed health check still produces a `canary` event

You are checking health after routing traffic. Check before, and return immediately on failure — `test_a_failed_health_check_never_reaches_canary` asserts that no `CANARY` event exists in that path.

## `test_health_names_every_failing_signal` fails

You are reporting the first failing signal instead of all of them. Build the detail from every one of liveness, readiness and dependency that is false, for the same reason preflight accumulates.

## Rolling back twice does nothing the second time

You are setting `previous_version` to `None`, or overwriting it, instead of swapping. Exchange the two values so the operation is symmetric — a rollback you cannot undo is another one-way door pressed under pressure.

## The canary promotes when it should roll back

Check the comparison direction: roll back when `error_rate > error_budget`. A rate exactly equal to the budget is within it.

## `test_canary_takes_only_a_fraction_of_traffic_before_the_decision` fails

Two things must both hold: the canary event names the configured percentage, and a failed canary leaves `traffic_to_new` at zero rather than at the canary value. Reset it when you roll back.

## The demo output ordering differs from the reference

Events are appended in the order the gates run, and the reference order is preflight, deploying, health, canary, promotion. If your `deploying` event comes after the health check, the transcript no longer shows that the version was rolled out before it was found unable to serve.

## `NotImplementedError` on every test

Expected. The starter stubs all three functions, and every test depends on at least one — see `expected-output/starter-run.txt`.
