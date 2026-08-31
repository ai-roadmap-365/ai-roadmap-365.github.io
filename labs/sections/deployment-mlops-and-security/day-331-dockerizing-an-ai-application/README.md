# Day 331 Lab: Dockerizing an AI Application

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dockerizing an AI Application
- **Day number:** 331 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-331-dockerizing-an-ai-application
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-331-dockerizing-an-ai-application` when the site is running.
<!-- generated-links:end -->

## Purpose

Work out how big an AI image will be, and what is making it big — before pulling twenty gigabytes to find out.

Packaging an AI application is not packaging a web application with a longer requirements file. Three things dominate: build tooling that is never needed at run time, a framework that is gigabytes before your code exists, and model weights that are frequently larger than everything else combined.

You will discover that the famous optimisation is the smaller one.

## Learning objectives

- Compute an image's size from stages, and explain why only the final stage ships.
- Separate build-only components from runtime ones, which is what makes multi-stage work.
- Separate runtime components from data, which is what makes the larger saving possible.
- Convert image size into the unit that is felt: rollout time across a fleet.
- Recognise that most Docker guidance was written for applications without weights.

## Prerequisites

- Day 330, "Docker Fundamentals" — layers, stages and the build cache.
- Comfortable with Python dataclasses and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU, no container runtime, no model download. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

**Docker is not required and no weights are downloaded.** The 13.5 GB in the demo is a number in a table — which is the point, since you should not have to move that much data to decide whether you should.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. For the real thing, Podman and Buildah build the same OCI images without a daemon, and `docker buildx` supports build secrets and cache mounts that keep a package cache out of the shipped layers.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/image_plan.py     your work: ten stubbed tasks
examples/image_plan.py    reference implementation
examples/image_demo.py    the same service packaged three ways
tests/test_image_plan.py  grouped by what the plan decides
tests/run_tests.sh        suite entry point
expected-output/          real captured output and measured values
requirements/             pinned dependency
```

## How to run

```bash
python3 examples/image_demo.py   # size three packagings and compare
bash tests/run_tests.sh          # run the suite
```

To work on the exercise, edit `starter/image_plan.py`, then copy it over the reference:

```bash
cp starter/image_plan.py examples/image_plan.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/image_demo.py` sizes three packagings of one AI service — single stage, multi-stage, and multi-stage with the weights mounted — reports what is making each one big, and compares what each change bought in megabytes and in rollout seconds.

`bash tests/run_tests.sh` runs `pytest` over twenty tests grouped by what the plan decides: sizing, pull cost, review and comparison.

## Expected output

```text
--- what each change bought ---
  multi-stage       21128 ->  18053 MB  (3075 MB, 1.17x)
  mount the weights 18053 ->   4553 MB  (13500 MB, 3.97x)
  both              21128 ->   4553 MB  (16575 MB, 4.64x)
  rollout to 20 nodes: 16902s -> 3642s
```

Read the second line against the first. The multi-stage build — the optimisation every Docker tutorial teaches — is the **smaller** win by a factor of four.

## Validation steps

1. `bash tests/run_tests.sh` reports `20 passed`.
2. Only the final stage may count toward the size. If the builder's four gigabytes appear in the total, multi-stage will appear to buy nothing.
3. `cuda-devel` is BUILD and `cuda-runtime` is RUNTIME. Swapping them produces either a broken image or a needlessly enormous one.
4. An unknown component must contribute `0`, not raise.
5. A `final_stage` naming a stage that does not exist must raise `KeyError` rather than silently using the first stage.

## Tests

Twenty tests in four groups:

- **sizing** — a stage is its base plus its components; unknown components contribute nothing; only the final stage ships; carried components count; an unknown final stage raises.
- **pull cost** — time scales with size and with link speed; zero bandwidth does not divide by zero; a rollout pays once per node; zero or negative nodes cost nothing.
- **review** — build tooling in the final image is caught, including when carried; tooling confined to a builder is not; baked-in weights are reported with what they cost; a fat base is reported; a clean plan is clean.
- **compare** — savings and ratio; comparing a plan with itself saves nothing; moving the weights out beats the multi-stage build.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: a smaller image is also a smaller attack surface, build tooling in a runtime image is a compiler in production, and baking a model you may not redistribute into an image you push is a licence question wearing engineering clothes.

## Extension exercises

1. **Add layer-level granularity.** Model each component as its own layer and compute what a *rebuild* transfers rather than what a first pull transfers. A registry that already holds most layers changes the picture considerably.
2. **Price it.** Add an egress cost per gigabyte and compute what the 21 GB image costs per rollout across a fleet. Compare against the cost of the object storage the weights would have lived in.
3. **Size your own.** Take a real AI service you have built, list its components with a purpose for each, and run it through the review. The interesting output is not the total — it is which single component you had never thought of as optional.

## Navigation

- [Lesson](../../../../content/sections/deployment-mlops-and-security/day-331-dockerizing-an-ai-application/README.md)
- Previous: Day 330 — Docker Fundamentals
- Next: Day 332 — Docker Compose for Multi-Service Apps
