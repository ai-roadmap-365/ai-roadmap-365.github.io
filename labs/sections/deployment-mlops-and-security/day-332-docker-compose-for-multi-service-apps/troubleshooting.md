# Troubleshooting — Day 332

## `NotImplementedError` on every test

Expected. The starter stubs nine functions — see `expected-output/starter-run.txt`.

Start with `find_cycles`; `startup_order` depends on it and everything else depends on that.

## A cycle is reported three times for a three-service loop

Walking from each service finds the same cycle rotated. Normalise before recording: rotate the cycle so it begins at its smallest member, and keep a set of what you have already emitted.

## `test_a_self_dependency_is_a_cycle` fails

`a` depending on `a` is a cycle of length one. If your check only looks for a repeat *after* at least one step, it misses this — and Compose will refuse to start such a file, so it is worth catching.

## `test_the_same_container_port_on_different_host_ports_is_fine` fails

You are comparing container ports. Two containers may both listen on 8080; they are in different network namespaces. Only the **host** side can conflict, which is the side `ports:` binds.

## `startup_order` loops forever

A cycle. Check for one first and raise, rather than spinning waiting for a service that can never become placeable.

## `test_a_dependency_on_an_undefined_service_does_not_block_startup` fails

A dependency naming a service the file does not define is a real problem, and it is reported separately. It must not stop the ordering — the service is not waiting on anything that exists.

## `test_service_started_does_not_wait_for_the_dependency_to_be_usable` fails

This is the finding the lab exists for, so get it right. Under `service_started`, a dependant may begin as soon as its dependency's **container** exists — which is `ready_times[dep] - dep.ready_seconds`, not `ready_times[dep]`. If you use the latter, the naive and correct stacks behave identically and the whole comparison collapses.

## The correct stack is slower and that looks like a failure

It is slower, and it is correct. Under `service_healthy` the api is usable at 5.2s instead of 1.2s — because at 1.2s it was not usable at all, it was merely running. `test_waiting_properly_is_slower_and_that_is_the_point` pins this deliberately.

## `test_a_cycle_suppresses_the_timing_findings` fails

`review` must not run the timing checks when a cycle exists. There is no start order, so "starts too early" is not a meaningful statement — and `ready_times` will raise.

## `healthy-without-healthcheck` never fires

The check is about the **target**: some other service waits for `service_healthy` on it, and it defines no healthcheck. Scan every service's dependencies looking for that condition, then check the named target rather than the waiter.
