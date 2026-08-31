# Reading the reconciliation output

## A step

    the loop compares and acts:
        delete api-001      node node-a is gone
        create api-004      2 of 3 replicas present
        -> 3 alive, 2 serving  api-002(1.4) api-003(1.4) api-004(1.4)

| Part | Meaning |
| --- | --- |
| `delete` / `create` | One action the loop decided to take this step. |
| the reason | Why. Always a statement about the **current gap**, never about history. |
| `N alive` | Pods that exist, are not failed, and are not on a dead node. |
| `N serving` | Pods a Service would actually route to — running **and** ready. |

`alive` and `serving` differ whenever a pod is starting. That gap is the whole
of readiness.

## Alive versus serving

    3 alive, 2 serving

Three pods exist and two can take a request. The third is Running and has not
yet passed its readiness probe. A Service routes to two of them.

This is the same distinction as yesterday's `service_healthy`, made continuous:
Compose asks it once at startup, Kubernetes asks it every few seconds forever.

## The four scenarios

| Scenario | What the loop does |
| --- | --- |
| first deploy | Nothing exists; create every replica. Converges in **2** steps, because a pod needs one tick to run and another to become ready. |
| a node dies | Reap the stranded pod, create a replacement — **on a live node**. |
| a manual delete | Exactly the same as a node death. The loop never asks how the gap appeared. |
| a rolling update | Replace stale pods within the budget, wait for readiness, repeat. |

Scenarios 2 and 3 producing the same behaviour is the point. `kubectl delete
pod` is not destructive because deletion is just another gap.

## The rollout

    step 1: 3 action(s)  -> 4 alive, 2 serving   api-004(1.4) api-005(1.4) api-006(1.5) api-007(1.5)
    step 2: 0 action(s)  -> 4 alive, 4 serving   (no action — waiting for the new pods to become ready)
    step 3: 3 action(s)  -> 3 alive, 2 serving   api-006(1.5) api-007(1.5) api-008(1.5)
    step 4: 0 action(s)  -> 3 alive, 3 serving   (no action — waiting for the new pods to become ready)
    step 5: rollout complete — every pod on app:1.5

**Step 2 is the one to read.** Zero actions, and the rollout is not finished.
The controller has already replaced as many pods as `maxUnavailable` permits
and may not retire another until the new ones are ready. That pause is the
budget working.

It is also why `rollout_done` exists separately from "reconcile returned no
actions" — they answer different questions, and conflating them makes a
half-finished rollout report success.

## The guarantee

    serving during rollout: [2, 4, 2, 3]  minimum 2
    2 required, 2 observed

With `replicas=3` and `maxUnavailable=1`, at least two pods must be serving at
every moment. The observed minimum is exactly two — the budget is fully used
and never exceeded.

Note the 4 in the middle: `maxSurge=1` permits one extra pod temporarily, which
is how the rollout makes progress without dipping below the floor.
