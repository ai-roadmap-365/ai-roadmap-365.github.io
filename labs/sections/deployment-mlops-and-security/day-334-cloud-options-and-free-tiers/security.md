# Security notes — Day 334

## What this lab does and does not touch

- **No cloud account, no credentials, no API calls, no spending.** The rate cards are literals in the demo. Nothing is provisioned.
- **No network.**
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## A free tier is a credential you are about to create

The security event of this day is not in the code. It is what happens twenty minutes after the lesson, when somebody signs up for a provider to try the numbers.

Three things go wrong at that moment, reliably:

- **A root account with no MFA.** The account you create in a hurry to test something becomes the account that owns production. Enable MFA before anything else, and create a separate non-root user for day-to-day work.
- **A long-lived access key on a laptop.** `~/.aws/credentials` and its equivalents outlive the experiment by years. Prefer short-lived credentials, and delete keys created "just to try it".
- **A key committed to a repository.** This is how most cloud-account compromises begin, and automated scanners find a pushed key within minutes. Day 330's point about layers applies here too — removing it in a later commit does not remove it from history.

## Free tiers are the target, not a safe corner

An account with a free tier and a card attached is worth compromising precisely because the attacker's spending is not capped by the free allowance — it is capped by your card. Crypto-mining on stolen cloud credentials is a routine, industrialised business, and it favours new accounts with weak hygiene.

**Set a budget alert before you deploy anything.** Every major provider offers them free. Day 327 built the per-request cap for model spend; this is the same control at the account level, and it is the difference between a surprising bill and a ruinous one.

## Egress pricing has a security dimension

The cost model here prices egress because it dominates at scale. It is also the mechanism by which a compromised endpoint becomes expensive: an attacker who can make your service return large responses is spending your egress budget, and rate limits usually count *requests* rather than *bytes*.

If a response size can be influenced by input, cap the bytes as well as the calls.

## What this model deliberately does not do

It prices a workload. It does not check that the option can **serve** it — the model will happily quote a single 1 vCPU VM for twenty million requests a month, which it could not do. Cost is one input to a hosting decision; capacity, reliability and blast radius are others, and a cheap option that falls over is not cheap.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
