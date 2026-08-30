# Lab — Day 360: Monitoring and Cost Controls

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Monitoring and Cost Controls
- **Day number:** 360 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-360-monitoring-and-cost-controls
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-360-monitoring-and-cost-controls` when the site is running.
<!-- generated-links:end -->

## Purpose

Build windowed metrics, alert rules and cost anomaly detection, then run them over traffic with three problems hidden in it — none of which raises a single error.

Requests carry a logical timestamp and the traffic is seeded, so every percentile and every alert is exactly reproducible.

## Learning objectives

- Compute nearest-rank percentiles and explain why the mean hides a long tail.
- Measure a quality signal alongside availability, and see the failure only it catches.
- Compare spend against a rolling median baseline rather than a fixed cap.
- Refuse to judge a window too small to be evidence.
- Distinguish symptom alerts from cause alerts.

## Prerequisites

- Day 359, "Deploying Your Capstone" — monitoring is the other half of that job.
- Day 327, "Cost Engineering for AI Systems", for the spend concepts.
- Comfortable with Python dataclasses, enums and list comprehensions.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network. The lesson discusses Prometheus, Grafana, OpenTelemetry, Langfuse and Arize Phoenix as the real options — all of which compute the same four signals this lab computes with a dictionary and a sort.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/monitoring.py         your work: percentile, windows, evaluate,
                              rolling_baseline
examples/monitoring.py        reference implementation
examples/monitoring_demo.py   25 minutes of traffic with three problems in it
tests/test_monitoring.py      grouped by signal
tests/run_tests.sh            suite entry point
expected-output/              real captured output and measured values
requirements/                 pinned dependency
```

## How to run

```bash
python3 examples/monitoring_demo.py   # five windows, three problems
bash tests/run_tests.sh               # run the suite
```

To work on the exercise, edit `starter/monitoring.py`, then copy it over the reference:

```bash
cp starter/monitoring.py examples/monitoring.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/monitoring_demo.py` generates twenty-five logical minutes of seeded traffic containing a latency problem, a quality problem and a cost problem, buckets it into five-minute windows, and evaluates the alert rules against each — carrying a rolling baseline forward so the cost rule has something to compare against.

`bash tests/run_tests.sh` runs `pytest` over twenty-two tests grouped by signal: percentiles, windows, small samples, latency, errors, quality, cost and severity.

## Expected output

```text
[  0-5  ) n=20  p50=678   p95=1253   err=0% ungrounded=0% spend=$0.0300
  OK    healthy: all signals within budget
[  5-10 ) n=20  p50=906   p95=1434   err=0% ungrounded=0% spend=$0.0300
  OK    healthy: all signals within budget
[ 10-15 ) n=20  p50=5470  p95=8573   err=0% ungrounded=0% spend=$0.0300
  PAGE  latency_slo: p95 8573ms exceeds 4000ms
[ 15-20 ) n=20  p50=738   p95=1311   err=0% ungrounded=40% spend=$0.0300
  WARN  ungrounded_answers: 40% of answers cited nothing
[ 20-25 ) n=20  p50=968   p95=1365   err=0% ungrounded=0% spend=$0.4000
  PAGE  cost_anomaly: spend $0.4000 is 13.3x the $0.0300 baseline
```

Read the `err` column: zero in every window, including all three with real problems. `expected-output/FIELDS.md` explains each field.

## Validation steps

1. `bash tests/run_tests.sh` reports `22 passed`.
2. Confirm the fourth window warns on groundedness while its error rate is zero — that is the failure conventional monitoring cannot see.
3. A window of two failed requests must report `insufficient_sample`, not a page. A 100 percent error rate over two requests is not evidence.
4. A spend spike with no baseline must produce no cost alert. A first window has nothing to compare against.

## Tests

Twenty-two tests in eight groups:

- **percentiles** — nearest rank rather than banker's rounding; empty input; and the case showing p95 over twenty samples cannot see a single outlier while p99 can.
- **windows** — bucketing by logical minute, empty traffic, and an empty window reporting zeros rather than raising.
- **small samples** — a tiny window is not judged; the same rate alerts once the sample is large enough.
- **latency**, **errors**, **quality**, **cost** — one group per rule, including that ungrounded answers warn while the error rate is zero.
- **severity** — the worst severity wins, and the worst of nothing is OK.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials — and the lesson covers why a cost anomaly is often the first sign of abuse, and why traces are the highest-risk store in an AI system.

## Extension exercises

1. **Burn-rate alerting.** Alert on the rate of error-budget consumption rather than a single window, so a fast severe spike pages and a slow mild elevation warns.
2. **Cardinality protection.** Allow labels but bound the number of distinct combinations, collapsing the rest into `other` — then demonstrate the explosion you are preventing.
3. **A quality baseline.** Compare groundedness against its own rolling baseline rather than a fixed budget, so a system that is normally 85 percent grounded alerts on a drop rather than on an absolute value.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-360-monitoring-and-cost-controls/README.md)
- Previous: Day 359 — Deploying Your Capstone
- Next: Day 361 — Security Review of Your Capstone
