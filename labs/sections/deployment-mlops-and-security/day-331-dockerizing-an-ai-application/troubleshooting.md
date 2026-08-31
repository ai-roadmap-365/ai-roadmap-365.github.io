# Troubleshooting — Day 331

## `NotImplementedError` on every test

Expected. The starter stubs ten functions — see `expected-output/starter-run.txt`.

Start with `Stage.size_mb`; nothing else can be checked until a stage has a size.

## `test_only_the_final_stage_ships` fails

The heart of a multi-stage build: earlier stages are discarded entirely. `ImagePlan.size_mb` must consult **only** the final stage plus whatever was carried into it — if you are summing every stage, the builder's four gigabytes are still in your total and multi-stage appears to buy nothing.

## `test_naming_a_stage_that_does_not_exist_is_an_error` fails

Returning `None` or falling back to the first stage hides a typo in `final_stage` and produces a confidently wrong number. Raise `KeyError`.

## An unknown component crashes instead of contributing zero

`COMPONENT_MB.get(name, 0)`, not `COMPONENT_MB[name]`. A plan naming a package the table does not know about is a normal thing to write, and it should not stop the arithmetic.

## `test_a_nonsensical_link_speed_does_not_divide_by_zero` fails

`pull_seconds(size, mbps=0)` must return `0.0` rather than raising. Zero bandwidth is nonsense input, and a tool that crashes on it is harder to use than one that returns a harmless value.

## `test_a_rollout_to_no_nodes_costs_nothing` fails

Guard the node count with `max(0, nodes)`. A negative count should not produce negative seconds.

## `build-tooling-shipped` misses a carried component

`review` must look at the final stage's components **and** the carried list. Copying a build artefact forward is the point of a multi-stage build; copying the toolchain forward defeats it, and that is exactly the case worth catching.

## `test_a_clean_plan_has_no_findings` fails

Something fires on a good plan. The usual cause is treating `cuda-runtime` as build tooling — it is `RUNTIME`, and the runtime is what a GPU service needs. Only `cuda-devel` is build-only.

## The multi-stage saving looks bigger than the weights saving

That can be legitimate, and it is worth understanding rather than "fixing". If the single-stage image carried `cuda-devel` (about 4 GB) then removing it is a large win. The lab's demo does not, which is why mounting the weights dominates there. The test asserts the ordering that holds for the demo's shapes, not a fixed ratio.
