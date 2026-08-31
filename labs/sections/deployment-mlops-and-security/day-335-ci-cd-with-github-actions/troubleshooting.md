# Troubleshooting — Day 335

## `NotImplementedError` on every test

Expected. The starter stubs nine functions — see `expected-output/starter-run.txt`.

Start with `finish_times`; the critical path, the review and the savings all read from it.

## `test_independent_jobs_run_in_parallel_not_in_sequence` fails

You are accumulating durations across every job rather than only along dependency edges. A job's finish time is `max(finish of its needs) + its own duration`, and a job with no needs starts at zero regardless of what else exists.

If this is wrong, wall clock equals runner minutes everywhere and the entire lesson disappears.

## `test_the_critical_path_is_the_longest_chain_not_the_sum` fails

The critical path is the chain ending at the **latest-finishing** job, walked backwards through whichever dependency finished last. It is not the sum of all durations, and it is not necessarily the longest chain by number of jobs.

## `finish_times` loops forever

A cycle. Check for one and raise before the scheduling loop, rather than spinning waiting for a job that can never become ready.

## `test_a_cycle_suppresses_the_other_findings` fails

`review` must return the cycle finding and stop. With no valid ordering there are no finish times, so every timing-derived finding would either be wrong or raise. A fatal finding should suppress the derived ones.

## `test_removing_a_job_does_not_orphan_its_dependants` fails

This is the subtle one. When you delete job `a`, anything that needed `a` must inherit `a`'s own dependencies — otherwise `b` becomes a root job and starts immediately, which silently understates the wall clock and makes deletion look better than it is.

## `savings_from_removing` reports wall-clock savings for an off-path job

Then your critical path is wrong, because removing a job nothing waits for cannot make the pipeline finish sooner. Getting `0.0` here is the correct and instructive answer.

## `secrets-exposed-to-forks` fires on `pull_request`

Only `pull_request_target` hands repository secrets to a workflow running against fork-controlled code. Plain `pull_request` runs with a read-only token and no secrets, and reporting it produces noise that trains people to ignore the finding that matters.

## `no-cache` fires on everything

The rule is for jobs that are **slow** — three minutes or more — and have no cache declared. A half-minute job without a cache is not worth a finding, and a rule that fires on every job is a rule nobody reads.

## The numbers do not match my pipeline

They will not. The durations and failure rates in the demo are illustrative. Put your own in: you can read job durations from any recent run, and the failure rates from how often each job has actually gone red this quarter — which is a number most teams have never looked at.
