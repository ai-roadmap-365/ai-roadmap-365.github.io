# Reading the monitoring output

## A window line

    [ 15-20 ) n=20  p50=738   p95=1311   err=0% ungrounded=40% spend=$0.0300

| Field | Meaning |
| --- | --- |
| `[a-b)` | The window, half-open on the right. |
| `n` | Requests in it. Below the minimum sample, the window is not judged at all. |
| `p50` / `p95` | Latency percentiles in milliseconds. Never a mean — a long tail has an unremarkable average. |
| `err` | Share of requests that failed outright. |
| `ungrounded` | Share of answers that cited nothing. **These requests succeeded.** |
| `spend` | Cost over the window, compared against a rolling median of recent windows. |

## An alert line

      PAGE  cost_anomaly: spend $0.4000 is 13.3x the $0.0300 baseline

| Part | Meaning |
| --- | --- |
| severity | `OK`, `WARN` or `PAGE`. Page for what a user feels now; warn for what needs attention today. |
| name | The rule that fired. |
| detail | The measured values, so the alert is actionable without opening a dashboard. |

## The five rules

| Rule | Severity | Catches |
| --- | --- | --- |
| `insufficient_sample` | OK | Nothing — it *prevents* judging a window too small to be evidence. |
| `latency_slo` | PAGE | p95 above the objective. |
| `error_budget` | PAGE | Failures above the agreed allowance. |
| `ungrounded_answers` | WARN | Answers citing nothing. The AI-specific failure. |
| `cost_anomaly` | PAGE | Spend far above the recent norm. Needs a baseline; a first window has none. |

## What to notice

Run the demo and read the `err` column: **it is 0% in every window**, including the three with real problems. That is the argument for measuring more than availability, made with data rather than assertion.
