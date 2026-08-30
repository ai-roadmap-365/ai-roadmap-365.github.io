# Security notes — Day 360

## What this lab does and does not touch

- **No network.** Requests are synthetic records with a logical timestamp. No test opens a socket.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No real user data.** The request records carry latency, cost and boolean flags — nothing identifying.

## A cost alert is a security control

The `cost_anomaly` rule looks like budgeting. In production it is frequently the **first detection** of an attack, and often the only one, because the traffic is otherwise well-formed.

Three cases it catches that nothing else does:

- **A leaked key.** Someone else is using your quota. Requests succeed, latency is fine, errors are zero — spend is the only signal that moves.
- **A scripted client.** A denial-of-wallet attempt, deliberately staying under rate limits so the requests look legitimate individually.
- **Prompt injection inducing recursion.** Text inside a retrieved document makes an agent call itself. Every individual call is valid.

This is why the rule pages rather than warns, and why it compares against a baseline: an attacker operating just above normal is exactly what a fixed threshold set generously will miss.

## Traces are the highest-risk store you own

Worth stating plainly, because it is easy to miss while thinking about metrics.

**Metrics are aggregates** — counts, percentiles, sums. They are safe to retain, cheap to store, and contain no personal data.

**Traces are not.** A trace captures the full prompt and the full completion, which means it contains whatever the user typed and whatever the system said back. In most AI systems traces are:

- the store with the most sensitive content,
- retained the longest, often by default rather than by decision,
- examined the least, so nobody notices what accumulated,
- and the one most often forgotten in a deletion path.

Everything from Day 328 applies to them. Set a retention period deliberately, include traces in the erasure path, and redact before writing rather than after.

## Cardinality is an availability problem

A label per user or per document identifier produces millions of distinct series. The consequence is not a bad dashboard — it is a metrics backend that becomes slow, then expensive, then unavailable, usually during the incident when you need it. Keep labels to a small bounded set, and cap them (extension exercise 2).

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
