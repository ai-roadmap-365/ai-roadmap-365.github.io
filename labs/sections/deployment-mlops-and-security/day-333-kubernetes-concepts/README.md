# Day 333 Lab: Kubernetes Concepts

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Kubernetes Concepts
- **Day number:** 333 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-333-kubernetes-concepts
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-333-kubernetes-concepts` when the site is running.
<!-- generated-links:end -->

## Purpose

Build the control loop that is Kubernetes' one idea, and watch four different situations turn out to be the same situation.

You declare three replicas. The loop sees what exists, compares, and takes one step. It never asks how the gap appeared — which is why a node failure and `kubectl delete pod` produce identical behaviour, and why a rolling update is not a special operation but the same loop with a changed spec.

No cluster required. The loop is about forty lines, and the forty lines are the part worth understanding.

## Learning objectives

- Implement a reconciliation step: compare desired against actual, then act.
- Distinguish a pod that is Running from one that is serving, and explain what a Service routes to.
- Show that node failure, manual deletion and scaling are one mechanism.
- Enforce `maxUnavailable` and `maxSurge` during a rolling update.
- Explain why "no actions this step" does not mean "the rollout is finished".

## Prerequisites

- Day 332, "Docker Compose for Multi-Service Apps" — the readiness distinction, made continuous here.
- Comfortable with Python dataclasses and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No cluster, no container runtime, no cloud account. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

**No Kubernetes cluster is required and none is contacted.** Installing one is a large detour, and the idea you need is not in the YAML — it is in the loop.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. If you later want a real cluster locally, `kind`, `k3s` and `minikube` are all Apache-2.0 and run on a laptop.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/reconcile.py       your work: eleven stubbed tasks
examples/reconcile.py      reference implementation
examples/reconcile_demo.py four situations, one loop
tests/test_reconcile.py    grouped by what the loop decides
tests/run_tests.sh         suite entry point
expected-output/           real captured output and measured values
requirements/              pinned dependency
```

## How to run

```bash
python3 examples/reconcile_demo.py   # deploy, lose a node, delete a pod, roll out
bash tests/run_tests.sh              # run the suite
```

To work on the exercise, edit `starter/reconcile.py`, then copy it over the reference:

```bash
cp starter/reconcile.py examples/reconcile.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/reconcile_demo.py` runs one deployment through four situations: a first deploy from nothing, a node dying and taking a pod with it, somebody deleting a pod by hand, and a rolling update to a new image. It prints each action the loop takes and the reason, then the serving count throughout the rollout.

`bash tests/run_tests.sh` runs `pytest` over nineteen tests grouped by what the loop decides: serving, first deploy, healing, scaling, rollout and completion.

## Expected output

```text
--- 4. a rolling update to app:1.5 ---
  step 1: 3 action(s)  -> 4 alive, 2 serving  api-004(1.4) api-005(1.4) api-006(1.5) api-007(1.5)
  step 2: 0 action(s)  -> 4 alive, 4 serving  (no action — waiting for the new pods to become ready)
  step 3: 3 action(s)  -> 3 alive, 2 serving  api-006(1.5) api-007(1.5) api-008(1.5)
  step 5: rollout complete — every pod on app:1.5
  serving during rollout: [2, 4, 2, 3]  minimum 2
```

Step 2 is the one to read: zero actions, and the rollout is not finished. The controller is waiting for the new pods to become ready before it may retire any more.

## Validation steps

1. `bash tests/run_tests.sh` reports `19 passed`.
2. A first deploy must converge in **2** steps, not 1 — a pod needs one tick to run and another to become ready.
3. Losing a node and deleting a pod by hand must produce the same kind of action. If they differ, the loop is reasoning about history.
4. During the rollout, `serving` must never fall below `replicas - max_unavailable`, and `alive` must never exceed `replicas + max_surge`.
5. Replacements must never be scheduled onto a dead node. If they are, `converge` will raise after churning forever.

## Tests

Nineteen tests in six groups:

- **serving** — a pod must be both Running and ready; a failed pod never serves.
- **first deploy** — an empty cluster creates every replica; a satisfied deployment does nothing; convergence reaches the declared count.
- **healing** — failed pods and pods on dead nodes are reaped; a manual delete is simply refilled; replacements avoid dead nodes; a cluster with no live node raises.
- **scaling** — scaling up creates only the difference; zero replicas is a valid desired state.
- **rollout** — a changed image starts one; the surge ceiling and the unavailability floor both hold; it finishes with every pod on the new image; no actions does not mean finished.
- **completion** — `rollout_done` requires readiness and the full replica count.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: the loop erases manual changes to running pods, which makes the manifest repository the only durable configuration — and therefore production infrastructure.

## Extension exercises

1. **Add a liveness probe.** A pod that fails liveness is restarted rather than deleted. Model the difference and answer the question it raises: what happens when a liveness probe checks a downstream dependency and that dependency is briefly slow?
2. **Add resource requests and node capacity.** Give each node a CPU budget and each pod a request, then make `schedule` refuse to place a pod that does not fit. Watch a Deployment stay Pending forever, which is the most common "why is nothing happening" in a real cluster.
3. **Add a PodDisruptionBudget.** Model voluntary disruption — a node drain — separately from involuntary, and enforce a minimum available across both.

## Navigation

- [Lesson](../../../../content/sections/deployment-mlops-and-security/day-333-kubernetes-concepts/README.md)
- Previous: Day 332 — Docker Compose for Multi-Service Apps
- Next: Day 334 — Cloud Options and Free Tiers
