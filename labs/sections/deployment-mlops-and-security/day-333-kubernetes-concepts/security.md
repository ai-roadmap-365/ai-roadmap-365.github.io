# Security notes — Day 333

## What this lab does and does not touch

- **No Kubernetes cluster required and none is contacted.** The cluster is a Python dataclass. Nothing is scheduled, no kubeconfig is read, no API server is reached.
- **No network**, no credentials, no cloud account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.** Installing a real cluster is neither, and this lab deliberately does not ask you to.

## The control loop is a security property

A loop that continuously drives actual state toward declared state has a consequence people meet by accident: **manual changes do not persist.**

`kubectl edit` a Deployment during an incident and the change survives. `kubectl edit` the Pod it created and the change is erased the moment the controller notices. That is the intended behaviour, and it is why the declared state — the thing in Git — is the only durable configuration. An attacker who modifies a running pod has made a change with a short half-life; an attacker who modifies your manifests has made a permanent one.

This is the argument for treating the manifest repository as production infrastructure with the review requirements that implies.

## Readiness probes gate traffic, and that makes them a control

A Service routes only to pods that are ready. That means a readiness probe is not diagnostics — it decides whether requests reach a process.

Two failure modes, in opposite directions:

- **A probe that always passes** routes traffic to a pod that cannot serve it. This is the Compose failure from yesterday, made continuous.
- **A probe that is too strict** — one that checks a downstream dependency — removes every pod from the Service the moment that dependency wobbles, converting a partial outage into a total one. Probe what *this* pod can do, not what the system can do.

## What this model deliberately omits

It is a teaching model of the loop, not of Kubernetes' security surface. Absent here and important in a real cluster:

- **RBAC.** Who may change the declared state is the whole question, and this model has no notion of an actor at all.
- **Namespaces and NetworkPolicy.** Every pod here can reach every other; a real cluster's default is the same, which is why NetworkPolicy exists.
- **Pod security context.** `runAsNonRoot`, dropped capabilities, a read-only root filesystem. Day 330's `USER` finding is the same idea one layer down.
- **Secrets.** Kubernetes Secrets are base64, not encrypted, unless encryption at rest is configured. Base64 is an encoding.

Day 344 threat-models these properly. The point today is that the loop's behaviour — declared state wins, always, eventually — is the foundation the rest sits on.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
