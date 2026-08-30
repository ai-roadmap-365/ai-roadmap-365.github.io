# Lab — Day 359: Deploying Your Capstone

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Deploying Your Capstone
- **Day number:** 359 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-359-deploying-your-capstone
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-359-deploying-your-capstone` when the site is running.
<!-- generated-links:end -->

## Purpose

Implement the release path — preflight, health, canary, promotion and rollback — and watch the same defect cost a different amount depending on which gate catches it.

There is no container runtime and no cloud here. What is modelled is the decision structure of a deployment, which is where deployments actually go wrong.

## Learning objectives

- Build a preflight gate that reports every blocker at once and deploys nothing when it fails.
- Separate liveness from readiness, and check dependencies.
- Decide a canary on an error budget rather than on elapsed time.
- Implement rollback as a reversible pointer swap.
- Explain why an irreversible migration blocks the whole path.

## Prerequisites

- Day 358, "Frontend and User Experience".
- Comfortable with Python dataclasses and enums.
- Familiar with the idea of a container image and a health endpoint, though neither is used directly.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU, no container runtime. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network. The lesson discusses Docker Compose, Kubernetes, Nomad, Argo Rollouts and Flagger as the real open-source options, and Fly.io, Railway, Render and Cloud Run as managed ones with free tiers.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/release.py         your work: preflight, deploy, rollback
examples/release.py        reference implementation
examples/release_demo.py   five deployments and a rollback
tests/test_release.py      grouped by gate
tests/run_tests.sh         suite entry point
expected-output/           real captured output and measured values
requirements/              pinned dependency
```

## How to run

```bash
python3 examples/release_demo.py   # five releases, each stopping differently
bash tests/run_tests.sh            # run the suite
```

To work on the exercise, edit `starter/release.py`, then copy it over the reference:

```bash
cp starter/release.py examples/release.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/release_demo.py` attempts the same version five ways — clean, failing tests, an irreversible migration, a process that starts but cannot serve, and a canary over its error budget — printing each event and the resulting state, then demonstrates a rollback after a successful promotion.

`bash tests/run_tests.sh` runs `pytest` over seventeen tests grouped by gate: preflight, health, canary and rollback.

## Expected output

```text
--- clean release ---
  deploying    rolling out v1.1.0
  canary       10% of traffic
  promoted     v1.1.0 at 100%
  => promoted live=v1.1.0 traffic_to_new=100%
--- irreversible migration ---
  blocked      migration is not reversible
  => blocked live=v1.0.0 traffic_to_new=0%
--- starts but cannot serve ---
  deploying    rolling out v1.1.0
  rolled_back  health check failed: readiness
  => rolled_back live=v1.0.0 traffic_to_new=0%
--- canary exceeds error budget ---
  deploying    rolling out v1.1.0
  canary       10% of traffic
  rolled_back  error rate 9.0% exceeds budget 2.0%
  => rolled_back live=v1.0.0 traffic_to_new=0%
```

`expected-output/FIELDS.md` explains each field and the cost gradient across the gates.

## Validation steps

1. `bash tests/run_tests.sh` reports `17 passed`.
2. A blocked build must leave `live` unchanged and `traffic_to_new` at zero — preflight deploys nothing at all.
3. Roll back twice and confirm you return to the newer version. If the second rollback does nothing, you are discarding rather than swapping.
4. Confirm the readiness failure never reaches a `canary` event. A failed health check must not route traffic.

## Tests

Seventeen tests in four groups:

- **preflight** — a clean build passes; failing tests, an irreversible migration and an unpinned image each block; blockers accumulate; a blocked build deploys nothing.
- **health** — a process that starts but cannot serve is rolled back, an unreachable dependency is rolled back, every failing signal is named, and a failed check never reaches canary.
- **canary** — a healthy release is promoted through canary, one over budget is rolled back, one inside budget is promoted, and only a fraction of traffic is exposed before the decision.
- **rollback** — returns to the previous version, is itself reversible, and reports rather than crashes when there is nothing to return to.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials — and the lesson covers why pinning an image digest is a supply-chain control rather than a style preference.

## Extension exercises

1. **A cost gate.** Block a release whose estimated cost per thousand requests has risen more than a stated percentage. An AI release can be entirely correct and still double the bill.
2. **Canary analysis over a window.** Decide on a sequence of per-minute samples with a minimum sample count, then report the request volume below which the analysis cannot distinguish a 2 percent error rate from a 9 percent one.
3. **Feature flags.** Separate deploy from release, so a version can ship dark and be exposed independently.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-359-deploying-your-capstone/README.md)
- Previous: Day 358 — Frontend and User Experience
- Next: Day 360 — Monitoring and Cost Controls
