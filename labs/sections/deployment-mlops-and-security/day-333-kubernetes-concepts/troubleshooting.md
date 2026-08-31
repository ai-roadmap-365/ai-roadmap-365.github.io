# Troubleshooting — Day 333

## `NotImplementedError` on nearly every test

Expected. The starter stubs eleven functions — see `expected-output/starter-run.txt`, which names the one test that passes without them.

Start with `Cluster.alive` and `Pod.serving`; `reconcile` is meaningless until they are right.

## `converge` raises "did not converge"

The loop is oscillating. Two causes, and the first is far more common:

**Replacements scheduled onto a dead node.** The loop creates a pod on the node that just died, reaps it next step, creates another, forever. `Cluster.schedule` must filter `dead_nodes`. This is a real failure mode when a scheduler's node filter is wrong, not an artefact of the model.

**A ceiling below the replica count.** If `wanted` can never be positive, the loop can never reach the desired state.

## `test_a_rollout_never_exceeds_replicas_plus_surge` fails

Your create step is not accounting for the stale pods it is keeping. Two limits apply at once: you need `replicas` pods on the new image *eventually*, and you may hold at most `replicas + max_surge` pods *at any moment*. Take the minimum of both.

## `test_a_rollout_never_drops_below_the_unavailability_budget` fails

The delete budget is `serving_now - (replicas - max_unavailable)`, and it must be clamped at zero. If you delete stale pods without checking how many are currently serving, the rollout takes the service down — which is exactly what `maxUnavailable` exists to prevent.

## `test_no_actions_does_not_mean_the_rollout_is_finished` fails

This is the subtle one and it is worth understanding rather than working around. A reconcile step can legitimately return **no actions** while old pods are still running: the controller has already replaced as many as the budget allows and is now waiting for the new pods to pass their readiness probe before it may retire any more.

"Nothing to do right now" and "the rollout is complete" are different questions. That is what `rollout_done` is for.

## `test_rollout_done_requires_readiness_not_just_running` fails

`rollout_done` must check `serving`, not `phase`. A cluster with the right number of Running pods has satisfied the spec and may still be routing traffic to none of them.

## Pods are created but never serve

`tick` advances one state per call: Pending becomes Running, then Running becomes ready. A pod therefore needs two ticks before it serves, which is why a first deploy converges in two steps rather than one.

## `test_scaling_to_zero_is_a_valid_desired_state` fails

Zero replicas is a legitimate thing to declare — it is how you take something down without deleting it. Nothing should be created, and `rollout_done` should be False while a pod still exists.
