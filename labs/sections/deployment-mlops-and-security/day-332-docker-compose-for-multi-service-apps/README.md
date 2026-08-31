# Day 332 Lab: Docker Compose for Multi-Service Apps

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Docker Compose for Multi-Service Apps
- **Day number:** 332 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-332-docker-compose-for-multi-service-apps
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-332-docker-compose-for-multi-service-apps` when the site is running.
<!-- generated-links:end -->

## Purpose

Work out what a Compose file will actually do before you run it.

A multi-service application is a dependency graph, and three things go wrong in it that are all visible before anything starts: cycles, host-port clashes, and false ordering. The third is the one that bites — `depends_on` waits for the **container**, not for the service, so an API can be "up" four seconds before its database can answer a query.

## Learning objectives

- Detect dependency cycles, reporting each once rather than once per member.
- Produce a stable startup order, and explain why a cycle has none.
- Distinguish a host-port conflict from two containers sharing an internal port.
- Model what `service_started` and `service_healthy` actually wait for.
- Explain why the correctly wired stack is slower to report ready, and why that is the honest number.

## Prerequisites

- Day 331, "Dockerizing an AI Application".
- Comfortable with Python dataclasses, enums and basic graph traversal.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No container runtime. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

**Docker Compose is not required.** The questions worth asking about a Compose file are graph questions, and a graph question is answerable before anything runs — which is the whole argument for asking them.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. For the real thing, Docker Compose is Apache-2.0, and `podman-compose` and `podman kube play` read the same files without a daemon.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/compose_graph.py     your work: nine stubbed tasks
examples/compose_graph.py    reference implementation
examples/compose_demo.py     one AI stack wired two ways, plus a broken file
tests/test_compose_graph.py  grouped by what the check decides
tests/run_tests.sh           suite entry point
expected-output/             real captured output and measured values
requirements/                pinned dependency
```

## How to run

```bash
python3 examples/compose_demo.py   # compare two wirings and inspect a broken file
bash tests/run_tests.sh            # run the suite
```

To work on the exercise, edit `starter/compose_graph.py`, then copy it over the reference:

```bash
cp starter/compose_graph.py examples/compose_graph.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/compose_demo.py` takes a four-service AI stack — postgres, qdrant, api, worker — wires it first with bare `depends_on` and then with `service_healthy`, prints the start order and when each service is genuinely usable, and reports every finding. It then runs a deliberately broken file containing a cycle, an undefined dependency and a port clash.

`bash tests/run_tests.sh` runs `pytest` over twenty-six tests grouped by what the check decides: cycles, undefined dependencies, ports, ordering, readiness, premature starts and the combined review.

## Expected output

```text
--- what the condition changed ---
  api usable at    1.2s  ->  5.2s
  worker usable at 1.2s  ->  5.8s
  premature starts 4  ->  0
```

The correct stack is **slower**, and that is the point: at 1.2s the api was not usable, it was merely running, and its first query would have failed.

## Validation steps

1. `bash tests/run_tests.sh` reports `26 passed`.
2. Under `service_started` the api must be usable *before* postgres is. If the two stacks behave identically, `ready_times` is treating `service_started` as though it waited for readiness.
3. A three-service cycle must be reported **once**, not three times.
4. `8000:8080` and `8001:8080` must not conflict. Only the host side can.
5. A cycle must suppress the timing findings — there is no start order to reason about.

## Tests

Twenty-six tests in seven groups:

- **cycles** — simple, longer and self-dependencies; reported once; a diamond is not a cycle.
- **undefined dependencies** — reported, and defined ones are not.
- **ports** — host clashes conflict; the same container port on different host ports does not.
- **order** — dependencies precede dependants; the order is stable; a cycle raises; an undefined dependency does not block.
- **readiness** — a leaf is start plus ready; `service_started` does not wait; `service_healthy` does; waiting is slower.
- **premature starts** — reported with the gap in seconds; absent under a healthy condition; absent when the dependency is instant.
- **review** — every class found; a cycle suppresses timing; `service_healthy` on a service with no healthcheck is reported; a correct stack is clean.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: publishing a port binds it on the **host**, which on a cloud VM can mean the internet — and services on a Compose network already reach each other without it.

## Extension exercises

1. **Add restart policies and retry.** Model `restart: on-failure` and a client that retries with backoff. Then answer the question the lesson raises: does retry make `service_healthy` unnecessary? Measure the failed requests during startup under each combination before deciding.
2. **Parse a real `docker-compose.yml`.** Read one with `yaml.safe_load`, build the `Service` graph from it, and run the review over a stack you actually operate.
3. **Add resource limits.** Give each service a memory reservation and report when the declared total exceeds what the host has — the failure mode being that Compose starts everything and the kernel then kills whichever container asks for memory last.

## Navigation

- [Lesson](../../../../content/sections/deployment-mlops-and-security/day-332-docker-compose-for-multi-service-apps/README.md)
- Previous: Day 331 — Dockerizing an AI Application
- Next: Day 333 — Kubernetes Concepts
