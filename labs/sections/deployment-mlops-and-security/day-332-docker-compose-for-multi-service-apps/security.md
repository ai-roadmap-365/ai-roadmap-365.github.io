# Security notes — Day 332

## What this lab does and does not touch

- **No Docker or Compose required and neither is invoked.** The input is a parsed service graph. Nothing is started, pulled or networked.
- **No network**, no credentials, no registry login.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## Publishing a port is the decision people make by accident

`ports: ["5432:5432"]` on a database does not "expose it to the API" — the services already reach each other on the Compose network by name. What it does is bind the port on the **host**, which on a cloud VM with a permissive security group means the internet.

The distinction is worth being precise about, because the wrong mental model produces the wrong file:

- **`expose`** and plain service-to-service traffic need no host binding at all. `api` reaches `postgres:5432` because they share a network.
- **`ports`** publishes to the host. Use it for the one or two services that genuinely take outside traffic.
- **`127.0.0.1:5432:5432`** binds to loopback only, which is what you usually want when you need a port for local debugging.

The lab's port-conflict check only looks at the host side, and that is the same reason: the host side is the side with consequences.

## Dependency conditions are an availability control

A service that starts before its database can answer does not fail safely. It typically retries, logs an error, and — if the retry has no backoff — hammers the dependency exactly while it is trying to come up. A slow start becomes a failed start.

`condition: service_healthy` plus a real healthcheck is the fix, and it is worth treating as a reliability control rather than a nicety. Day 342 covers what happens when this is missing during an incident, which is when the ordering matters most and is least likely to be tested.

## Secrets do not belong in the file

`environment:` values live in the Compose file, which lives in Git. Use `env_file:` for local development with the file gitignored, or Docker secrets, or inject from the orchestrator in production. A `POSTGRES_PASSWORD` committed to a repository is the most common finding in any first review of a Compose stack.

## What a healthcheck should actually check

A healthcheck that returns 200 whenever the process is alive tells you the process is alive, which the container runtime already knew. A useful one verifies the thing a dependant is about to rely on — that the database accepts a connection, that the model is loaded, that the vector index is open.

An unhealthy service that reports healthy is worse than no healthcheck, because now something is waiting on a signal that means nothing.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
