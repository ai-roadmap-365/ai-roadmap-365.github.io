# Troubleshooting — Day 334

## `NotImplementedError` on every test

Expected. The starter stubs fourteen functions — see `expected-output/starter-run.txt`.

Start with `Workload.compute_seconds` and `Workload.egress_gb`; every price depends on them.

## `test_an_always_on_option_bills_by_the_hour_regardless_of_traffic` fails

You are scaling an always-on option by usage. That is the property that distinguishes it: a VM costs `hourly × 730` whether it served ten requests or ten million, including at 3am when it served none. If your always-on cost changes with traffic, the entire comparison in this lab collapses.

## `test_a_per_request_option_costs_nothing_at_zero_traffic` fails

The mirror image. A per-request option must bill nothing when there are no requests — that is what scale-to-zero means and it is the only reason serverless wins at launch.

## `test_free_requests_are_deducted_before_billing` fails

There are two independent allowances on a per-request option: free compute-seconds and free requests. Deduct each from its own quantity. The test isolates the request charge by giving both options the same free seconds, so a failure here means the request allowance is being ignored or applied to the wrong quantity.

## Free allowances go negative

Clamp with `max(0.0, used - allowance)`. Without it, an option under its free tier earns you money, which is a pleasing bug and not a correct one.

## `test_the_binding_constraint_is_the_smallest_headroom` fails

`headroom` returns a multiple per dimension — allowance divided by current usage. `binding_constraint` takes the **smallest** of those, because the free tier ends when the first allowance runs out, not when the advertised one does.

Watch the zero-usage case: a dimension with no usage has infinite headroom, not a division error.

## `crossover` returns None when you expect a number

Three legitimate reasons, and only the third is a bug:

- The two options cost the same at the base workload.
- One option is cheaper at *every* scale in the range — the ranking never changes, which is a genuinely useful answer.
- Your bisection is not bracketing correctly. Check that you compare the ordering at the far end before searching.

## The free ceiling is slightly above the binding constraint

Not a bug. The demo reports a free tier binding on egress at 1.25x and staying free until about 1.30x, because a small fraction of a gigabyte of egress rounds to $0.00 at cent precision. The binding constraint is the honest number; the ceiling includes the rounding.

## The numbers do not match my provider

They will not. The rate cards in the demo are representative, not current, and providers change them. The lab is about the *shape* — always-on against per-request, and which allowance binds first — not about any particular price. Substitute your provider's numbers and re-run.
