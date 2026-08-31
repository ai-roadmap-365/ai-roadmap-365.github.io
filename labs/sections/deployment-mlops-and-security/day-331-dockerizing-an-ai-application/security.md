# Security notes — Day 331

## What this lab does and does not touch

- **No Docker required and none is invoked.** The input is a described build. Nothing is pulled, built or run.
- **No network**, no credentials, no registry login.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No model weights are downloaded.** The 13.5 GB in the demo is a number in a table, which is the point — you should not need to move that much data to reason about whether you should.

## A smaller image is a smaller attack surface

The size argument and the security argument point the same way, which is unusual and worth using.

**Build tooling in a runtime image is a compiler in production.** `cuda-devel`, `gcc`, `make` and the headers exist to produce artefacts. Left in the final image they give anyone who achieves code execution a full toolchain to build with. A multi-stage build removes them for a reason that has nothing to do with megabytes.

**A slim base has fewer packages to have vulnerabilities.** Most CVEs reported against an application image are in components the application never calls. The cheapest way to stop being affected is not to ship them.

**Every layer is kept — including the one with the weights.** If a model is licensed such that you may not redistribute it, baking it into an image you push to a registry is redistribution, and pushing to a public registry is publication. This is a licence question that looks like an engineering decision.

## Weights deserve their own answer

The demo's third plan mounts the weights rather than baking them in. Three consequences beyond size:

- **The mount is now a supply-chain input.** Whatever writes to that volume can replace your model. Day 347 covers this properly; the short version is that a checksum on load is cheap and worth it.
- **A public image no longer contains a private model.** Separating them means an image leak is not a model leak.
- **Rotating the model no longer requires rebuilding the image**, which removes the temptation to rebuild in a hurry without re-running the checks.

## Run as a non-root user, and mean it

Day 330's linter checks for `USER`. It matters more here: an AI service typically has a writable cache directory, a mounted model volume and a network listener. Root inside the container plus a writable mount is the combination that turns a container escape from theoretical into practical.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
