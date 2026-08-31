# Day 334 Lab: Cloud Options and Free Tiers

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Cloud Options and Free Tiers
- **Day number:** 334 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-334-cloud-options-and-free-tiers
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-334-cloud-options-and-free-tiers` when the site is running.
<!-- generated-links:end -->

## Purpose

Price four ways of hosting the same AI endpoint, honestly, including the parts the pricing page leaves out.

A free tier is a real offer with an edge, and the edge is rarely where the headline suggests. The tier in this lab advertises two million free requests — a hundred times the workload's traffic — and ends at **1.25x**, because the egress allowance is a single gigabyte.

You will also find where the cheapest option at launch stops being the cheapest, which is lower than most people expect.

## Learning objectives

- Distinguish always-on billing from per-request billing, and say what each costs at zero traffic.
- Price compute, egress and storage separately, deducting free allowances from each.
- Compute headroom per dimension and identify which allowance binds first.
- Find the traffic multiple at which two options change places.
- State what a cost model does not tell you.

## Prerequisites

- Day 333, "Kubernetes Concepts".
- Comfortable with Python dataclasses and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

**No cloud account is required and nothing is spent.** The rate cards are literals in the demo. If you do create an account to check the numbers, read `security.md` first — the security event of this day is the account, not the code.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. For real deployments the genuinely free-tier-friendly options worth knowing are Cloudflare Workers, Fly.io, Railway, Render and Hugging Face Spaces; for self-hosting, k3s on a single small VM is often cheaper than any of them past the crossover.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/hosting_cost.py     your work: fourteen stubbed tasks
examples/hosting_cost.py    reference implementation
examples/cost_demo.py       four options, three traffic levels
tests/test_hosting_cost.py  grouped by what the model decides
tests/run_tests.sh          suite entry point
expected-output/            real captured output and measured values
requirements/               pinned dependency
```

## How to run

```bash
python3 examples/cost_demo.py   # price four options at launch, 50x and 1000x
bash tests/run_tests.sh         # run the suite
```

To work on the exercise, edit `starter/hosting_cost.py`, then copy it over the reference:

```bash
cp starter/hosting_cost.py examples/hosting_cost.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/cost_demo.py` prices a serverless free tier, a paid serverless plan, a small always-on VM and a managed container service against the same workload at three traffic levels, reports which allowance binds each free tier first, and bisects for the traffic multiple at which the ranking changes.

`bash tests/run_tests.sh` runs `pytest` over twenty-four tests grouped by what the model decides: workload arithmetic, always-on billing, per-request billing, egress, headroom, selection, crossover and the free ceiling.

## Expected output

```text
--- where the free tier ends, and why ---
  serverless-free-tier   free until   1.30x (26,000/mo)  binds on egress-gb at 1.25x
  the headline allowance is rarely the one that runs out first:
      egress-gb          1.25x current load
      requests         100.00x current load
--- where the ranking changes ---
  serverless-free-tier stops beating small-vm at 45.0x (899,599 requests/month)
```

The advertised constraint and the binding constraint differ by a factor of eighty.

## Validation steps

1. `bash tests/run_tests.sh` reports `24 passed`.
2. An always-on option must cost the same at zero traffic as at full traffic. If it scales with usage, the whole comparison collapses.
3. A per-request option must cost exactly zero at zero traffic — that is what scale-to-zero means.
4. `binding_constraint` must return `egress-gb`, not `requests`. Returning the advertised allowance means `headroom` is not taking a minimum.
5. Free allowances must clamp at zero. An option under its free tier must not earn you money.

## Tests

Twenty-four tests in eight groups:

- **workload** — compute seconds, egress, and scaling that grows storage more slowly than traffic.
- **always-on** — bills by the hour regardless of traffic, including at zero.
- **per-request** — costs nothing at zero; free seconds and free requests deducted from their own quantities; excess billed.
- **egress** — free allowance honoured, only the excess billed, and egress dominating compute at scale.
- **headroom** — a multiple per dimension, infinity for unused ones, the smallest one binding.
- **selection** — cheapest chosen; choosing from nothing raises.
- **crossover** — the launch winner losing at scale; `None` when prices match or one option always wins.
- **free ceiling** — `None` when never free, and located when it exists.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no account is used here, and the risk arrives when you create one — MFA before anything else, a budget alert before you deploy, and no long-lived key on a laptop.

## Extension exercises

1. **Add capacity.** Give each option a requests-per-second ceiling and refuse to price a workload it cannot serve. This removes the model's most misleading output — a single vCPU quoted for twenty million requests a month.
2. **Price your own workload.** Take a service you actually run, measure its request rate and response size, and put your provider's current rate card in. The interesting result is your own binding constraint.
3. **Add committed-use discounts and spot pricing.** Reserved instances change always-on economics substantially, and spot changes them again at the cost of being interrupted. Find where each moves the crossover.

## Navigation

- [Lesson](../../../../content/sections/deployment-mlops-and-security/day-334-cloud-options-and-free-tiers/README.md)
- Previous: Day 333 — Kubernetes Concepts
- Next: Day 335 — CI/CD with GitHub Actions
