# Security notes — Day 323

## What this lab does and does not touch

- **No network.** The source and the index are in-memory Python objects. No test opens a socket, and `requires_network` is `false` in `metadata.yml`.
- **No credentials.** There is no API key, token or account anywhere in this lab.
- **No writes outside this directory.** The pipeline holds its state in memory. The only files created are `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/` — all inside this lab directory and all removable with the documented cleanup commands.
- **No `sudo`, no global installs.** Dependencies go into a local virtual environment.

## What the lesson says about real pipelines, which this lab deliberately simulates

A production ingestion pipeline is a genuinely sensitive component, and it is worth understanding why even though this lab exercises none of it:

- **It holds credentials for every source it reads.** That makes it a high-value target. Grant the narrowest read-only scope each source supports, and keep those credentials out of the repository.
- **Extraction parses untrusted input.** A PDF, an archive or an office document is an attack surface — decompression bombs and malformed structures are real. In production, run extractors with memory and time limits, and preferably in a sandbox. This lab's `extract()` raises a plain exception instead, which is the behaviour you must handle either way.
- **Ingestion is where personal data enters the system**, so it is the right place to redact it, and the right place to honour deletion. A source record deleted for legal reasons must be removed from the index and any cache; a deletion that does not propagate is a compliance failure rather than a stale cache.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
