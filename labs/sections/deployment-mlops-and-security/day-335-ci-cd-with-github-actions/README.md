# Day 335 Lab: CI/CD with GitHub Actions

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** CI/CD with GitHub Actions
- **Day number:** 335 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-335-ci-cd-with-github-actions
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-335-ci-cd-with-github-actions` when the site is running.
<!-- generated-links:end -->

## Purpose

Reason about a CI pipeline before you push and wait eleven minutes to find out.

A workflow is a job graph, and three questions about it are answerable from the graph alone: how long it actually takes, which jobs can reach a secret, and whether a gate is protecting anything.

You will find that deleting the two jobs that have never caught a bug makes the pipeline **zero seconds faster**, and that one cache makes it 3.7 minutes faster — because those are different problems.

## Learning objectives

- Compute finish times across a dependency graph where independent jobs run in parallel.
- Distinguish wall-clock time (the critical path) from runner minutes (the bill).
- Explain why `pull_request_target` with secrets is dangerous and `pull_request` is not.
- Identify gates that have never fired and caches that are missing.
- Show what removing a job saves — and why an off-path job saves no time at all.

## Prerequisites

- Day 334, "Cloud Options and Free Tiers".
- Comfortable with Python dataclasses, enums and basic graph traversal.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

**No GitHub account and no runner are used.** The shape of a pipeline is the part you can get wrong for months without noticing, and it is checkable offline.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. GitHub Actions is free for public repositories; `act` runs workflows locally in containers; GitLab CI, Woodpecker, Drone and Forgejo Actions are open-source alternatives with the same job-graph model.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/pipeline.py        your work: nine stubbed tasks
examples/pipeline.py       reference implementation
examples/pipeline_demo.py  one pipeline read three ways
tests/test_pipeline.py     grouped by what the analysis decides
tests/run_tests.sh         suite entry point
expected-output/           real captured output and measured values
requirements/              pinned dependency
```

## How to run

```bash
python3 examples/pipeline_demo.py   # time it, review it, price two changes
bash tests/run_tests.sh             # run the suite
```

To work on the exercise, edit `starter/pipeline.py`, then copy it over the reference:

```bash
cp starter/pipeline.py examples/pipeline.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/pipeline_demo.py` takes an eight-job pipeline, computes the critical path and the runner minutes, prints when each job finishes, reviews it for never-firing gates and missing caches, prices the removal of each useless job against a cache on the critical path, and then re-triggers the same jobs under `pull_request_target` to show what that exposes.

`bash tests/run_tests.sh` runs `pytest` over twenty-seven tests grouped by what the analysis decides: timing, critical path, graph validity, review, secrets and removal.

## Expected output

```text
  wall clock   12.7 min   along checkout -> install -> integration -> deploy
  runner time  22.2 min billed
--- what removing each never-firing gate would buy ---
  licence-scan   NOT on the critical path   wall 12.7 -> 12.7 (saves 0.0)   runner minutes saved 2.4
  docs-build     NOT on the critical path   wall 12.7 -> 12.7 (saves 0.0)   runner minutes saved 3.1
--- what caching the install would buy instead ---
  wall 12.7 -> 9.0 min   saves 3.7 min per run
```

Deleting both useless jobs: 0.0 minutes. One cache on the critical path: 3.7 minutes.

## Validation steps

1. `bash tests/run_tests.sh` reports `27 passed`.
2. Runner minutes must exceed wall clock whenever any work is parallel. If they are equal everywhere, `finish_times` is accumulating across every job rather than along dependency edges.
3. Removing an off-critical-path job must save `0.0` of wall clock. Any other answer means the critical path is wrong.
4. Removing a job must re-point its dependants onto its dependencies, or the saving is overstated.
5. `secrets-exposed-to-forks` must fire on `pull_request_target` and **not** on `pull_request`.

## Tests

Twenty-seven tests in six groups:

- **timing** — a lone job; dependent jobs adding up; independent jobs in parallel; waiting for the slowest dependency; an undefined dependency not blocking.
- **critical path** — the longest chain rather than the sum; runner minutes exceeding wall clock; the path being a real chain; an empty workflow.
- **graph** — cycles detected, acyclic graphs clean, timing a cycle raising, undefined needs reported.
- **review** — never-firing gates; slow jobs without caches; quick jobs left alone; a cycle suppressing everything else.
- **secrets** — `pull_request_target` with secrets reported; `pull_request` not; `pull_request_target` without secrets not.
- **removal** — jobs dropped, dependants re-pointed, a missing job raising, and the off-path versus on-path saving.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: `pull_request_target` runs with your secrets against code a fork controls, third-party actions run their code with your token, and a scanner that has never reported anything is a control that does not exist.

## Extension exercises

1. **Add a concurrency limit.** Real accounts have a finite number of runners. Recompute wall clock with only two available and see how much of the parallelism was theoretical — for most pipelines it is a great deal.
2. **Add a matrix.** Model `strategy.matrix` expanding one job into several, and find where the runner-minute cost of a matrix outweighs the wall-clock saving.
3. **Analyse your own workflow.** Read job durations from a recent run and failure rates from how often each job actually went red this quarter. Most teams have never looked at the second number, and it is the one that tells you which gates to delete.

## Navigation

- [Lesson](../../../../content/sections/deployment-mlops-and-security/day-335-ci-cd-with-github-actions/README.md)
- Previous: Day 334 — Cloud Options and Free Tiers
- Next: Day 336 — A Containerized AI Deployment
