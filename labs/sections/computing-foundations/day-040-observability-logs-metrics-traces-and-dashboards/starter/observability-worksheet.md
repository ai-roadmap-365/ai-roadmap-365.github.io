# Observability worksheet — Day 040

Fill this in from a real run of your completed `starter/observe.sh` (or the
reference `examples/observe.sh`). Keep it — it is the template you will reuse
when you instrument a real service later.

## The metrics from my run

| Metric | My value |
| --- | --- |
| Total requests | |
| Error count | |
| Error rate (%) | |
| p95 latency (ms) | |
| p50 latency (ms) | |

## The one thing a dashboard should alert on

Write the single alert you would set for this service. State it as a **symptom
the user feels**, not an internal cause, and give a concrete threshold and a
duration.

- Alert when: ______________________________________________
- Because (the user impact): ________________________________

Example shape: "Page when the error rate stays above 5% for 5 minutes, because
that means more than one user in twenty is seeing failures."

## If this service suddenly felt slow, which pillar would I check first?

In three or four sentences, name which of the three pillars (metrics, traces,
or logs) you would consult first, and what each would tell you next.

______________________________________________________________
______________________________________________________________
______________________________________________________________

## One thing that surprised me

One or two sentences.
