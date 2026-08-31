# Security notes — Day 330

## What this lab does and does not touch

- **No Docker required and none is invoked.** The lab parses Dockerfile text and models the cache rule. Nothing is built, pulled, or run in a container.
- **No network.** The Dockerfiles are strings in the demo.
- **No credentials**, no API key, no registry login.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.** Worth stating plainly, because installing Docker Desktop is neither, and this lab deliberately does not ask you to.

## Why the linter's three security rules are the ones it has

**An unpinned base image.** `FROM python` or `FROM python:latest` resolves to whatever that tag points at on the day you build. A rebuild six months later silently gets a different operating system, a different OpenSSL, and a different set of vulnerabilities. Pin to a specific tag, and pin to a digest when the build must be reproducible.

**A container running as root.** Without a `USER` instruction the process runs as uid 0 inside the container. If it is ever able to write to a mounted host path, or if a kernel escape exists, root inside is a much worse starting position than an unprivileged uid. Adding `USER 10001` costs one line.

**A package index left in the image.** `apt-get install` without `rm -rf /var/lib/apt/lists/*` **in the same layer** ships the index. Removing it in a later layer does not shrink the image — the bytes are still in the earlier layer, and anyone who pulls the image can read them. That is the same mechanism by which a secret `COPY`d and later deleted remains fully recoverable.

## The layer rule is a security property, not only a speed one

Every layer is kept. `COPY .env .` followed by `RUN rm .env` produces an image where the file is gone from the final filesystem and completely present in the layer beneath it, readable with `docker save` and a tar extractor.

This is the single most common way credentials escape into a registry. The fix is not to delete the file later; it is never to copy it in — use a `.dockerignore`, a build secret, or a runtime environment variable.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
