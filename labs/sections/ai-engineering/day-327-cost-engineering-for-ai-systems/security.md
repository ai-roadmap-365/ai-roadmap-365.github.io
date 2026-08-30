# Security notes — Day 327

## What this lab does and does not touch

- **No network.** The model is simulated and prices are a constant table. No test opens a socket.
- **No credentials and no spend.** `requires_api_key` is `false`. Running this lab costs nothing.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## Unbounded spend is a security problem, not just a budgeting one

The spend cap in this lab looks like housekeeping. In production it is a control, and its absence is an exploitable weakness — OWASP tracks it as **unbounded consumption** in the LLM Top 10.

Three ways spend goes unbounded:

- **A retry loop.** A transient failure, an automatic retry, a failure again. Nothing in the loop knows what it has already cost.
- **A recursive agent.** A tool-using agent that can invoke itself, or two agents that call each other, has no natural termination.
- **A hostile client.** Anything a legitimate user can trigger, an attacker can trigger deliberately and repeatedly. This is a **denial-of-wallet** attack: the target is the budget rather than the CPU, and it is often cheaper to mount than a traditional denial of service.

Prompt injection makes the third worse: text inside a retrieved document can induce expensive behaviour, so the attacker does not even need to reach your endpoint directly.

The mitigations are per-request caps, per-user and per-tenant budgets, a maximum tool-call depth, and alerting on spend rate rather than only on the total. A cap that is checked *before* the call is the only one that bounds the worst case; checking afterwards is an audit.

## Caching is user data

A response cache stores prompts and completions, which are user content. Two consequences:

- **Key on tenant as well as content.** A shared cache keyed only on prompt text serves one tenant's response to another when prompts collide, which is a data leak with a very ordinary-looking cause.
- **Retention rules apply.** Cached prompts and responses inherit whatever deletion and retention obligations the original data has. A right-to-erasure request that clears the database and leaves the cache has not been honoured.

Semantic caching, in the extension exercise, sharpens both problems: near-matches hit across users more readily than exact matches do.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
