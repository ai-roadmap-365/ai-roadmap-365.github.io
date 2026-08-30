# Lab — Day 327: Cost Engineering for AI Systems

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Cost Engineering for AI Systems
- **Day number:** 327 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-327-cost-engineering-for-ai-systems
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-327-cost-engineering-for-ai-systems` when the site is running.
<!-- generated-links:end -->

## Purpose

Make the cost of an AI pipeline visible, then reduce it deliberately. You build a ledger that attributes spend per model, a router that sends easy work to a cheaper model, a context trimmer, and a spend cap that degrades before it refuses — then measure what each lever actually saves on the same workload.

Everything runs offline. Prices are a fixed table and tokens are estimated crudely; the accounting is real.

## Learning objectives

- Attribute spend per model rather than reporting a single total.
- Demonstrate that cache hit rate and cost saving are different measurements.
- Route requests to the cheapest adequate model and trim context to a token budget.
- Enforce a cap checked before the call, with degradation before refusal.
- Project cost per request to expected volume.

## Prerequisites

- Day 326, "Scaling Retrieval".
- Comfortable with Python dataclasses and dictionaries.
- No API key and no account — the model is simulated.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no spend — the price table is a constant in the source. The lesson discusses LiteLLM, Langfuse and Helicone as the real open-source options for budgets and cost observability.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/costs.py         your work: cost_of, route, trim_context,
                         unit_economics, Pipeline.answer
examples/costs.py        reference implementation
examples/costs_demo.py   runs one workload four ways
tests/test_costs.py      grouped by lever
tests/run_tests.sh       suite entry point
expected-output/         real captured output and measured values
requirements/            pinned dependency
```

## How to run

```bash
python3 examples/costs_demo.py   # compare the levers
bash tests/run_tests.sh          # run the suite
```

To work on the exercise, edit `starter/costs.py`, then copy it over the reference:

```bash
cp starter/costs.py examples/costs.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/costs_demo.py` runs the same six requests four ways — no cache, cached, cached with trimmed context, and under a budget too small to complete — printing total spend, spend by model, and cost per request for each, then projecting to a million requests.

`bash tests/run_tests.sh` runs `pytest` over twenty tests grouped by lever: accounting, cache, router, trim, budget and unit economics.

## Expected output

```text
workload: 6 requests, 3 of them the same question
no cache, full ctx     calls=6 cached=0 total=$0.0085  per_request=$0.00141
                       by model: large=$0.0073, small=$0.0012
cache, full ctx        calls=6 cached=2 total=$0.0079  per_request=$0.00131
                       by model: cache=$0.0000, large=$0.0073, small=$0.0006
cache, trimmed ctx     calls=6 cached=2 total=$0.0066  per_request=$0.00109
                       by model: cache=$0.0000, large=$0.0061, small=$0.0005
tight budget           STOPPED: request would cost $0.0036, only $0.0009 left
tight budget           calls=2 cached=0 total=$0.0006  per_request=$0.00030
                       by model: small=$0.0006
projection at 1M requests: $1,092 (from $0.00109 per request)
```

The second row is the one to study: a 33 percent cache hit rate produced a 7 percent saving, because the repeated question routed to the cheap model. `expected-output/FIELDS.md` works through the attribution.

## Validation steps

1. `bash tests/run_tests.sh` reports `20 passed`.
2. Run the demo and confirm the `tight budget` row stops rather than completing, and that its total is at or below the budget — never above.
3. Check the `by model` line includes `cache=$0.0000`. If cache hits are absent from the ledger rather than present at zero cost, your hit rate is invisible.

## Tests

Twenty tests in six groups:

- **accounting** — output costs more than input, cost is linear in tokens, the large model is an order of magnitude dearer, an unknown model raises rather than costing zero, and a token estimate is never zero.
- **cache** — a repeat is free, hits appear in the ledger, and different context is a different key.
- **router** — reasoning and long prompts go large, simple ones go small.
- **trim** — keeps what fits in priority order and stops rather than skipping ahead.
- **budget** — checked before spending, degrades before refusing, and `remaining` never goes negative.
- **unit economics** — scales linearly, handles zero requests, and attributes by model.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md` for each failure this lab is designed to produce.

## Security notes

See `security.md`. In short: no network, no credentials, no spend. The lesson treats unbounded spend as a security concern — a denial-of-wallet attack — rather than only a budgeting one.

## Extension exercises

1. **Per-tenant budgets.** Enforce a per-tenant cap alongside the global one, and prove both that one tenant cannot exhaust another's budget and that per-tenant limits do not sum to a safe global limit.
2. **Semantic caching.** Cache on similarity rather than exact match, and measure the wrong answers served at each threshold alongside the savings.
3. **Self-hosted crossover.** Add a fixed hourly cost for a self-hosted model and compute the request volume at which it beats per-token pricing.

## Navigation

- [Lesson](../../../../content/sections/ai-engineering/day-327-cost-engineering-for-ai-systems/README.md)
- Previous: Day 326 — Scaling Retrieval
- Next: Day 328 — Privacy in AI Systems
