# Security notes — Day 359

## What this lab does and does not touch

- **No network.** There is no container runtime, no registry and no cloud. Only the decision structure is modelled.
- **No credentials.** No API key, token or account. `secrets_present` is a boolean flag on a dataclass, not a real secret.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## Why pinning an image digest is a security control

`preflight` blocks a build whose image is not pinned to a `sha256:` digest, and it is worth being explicit that this is not tidiness.

A tag such as `latest`, or even `v1.1.0`, is a **mutable pointer**. Whoever can push to the registry can change what that tag resolves to, at any time, including after your tests passed against it. A digest is the content hash: it either matches the bytes you tested or it does not exist.

The attack this prevents is a supply-chain one. An attacker who compromises a build account does not need to touch your repository — repointing a tag is enough, and everything downstream continues to look correct. Pinning means the artefact you deploy is provably the artefact you tested.

The same argument applies to base images in a Dockerfile and to dependencies in a lockfile.

## Secrets belong in the environment, never in the image

A container image is a distributable artefact. Anything baked into it travels with it — into the registry, into every cache, into anyone's `docker pull`, and into the layer history where a later `RUN rm` does not remove it.

`preflight` checks that required secrets are **present** rather than checking their values, which is the right shape: the deployment needs to know they were supplied, and should never handle them itself.

## Deployment is a privacy checkpoint

A new version may log new fields. Because a deployment is the moment that starts happening, it is the natural place to ask what the logs will now contain — before the data accumulates rather than after. That connects directly to Day 328: a store you did not know you created is a store your erasure path does not cover.

## Rollback is an availability control

The blunt version: an incident lasts exactly as long as the rollback takes. That makes rollback speed a security property, not just an operational convenience, and it is why the lab insists rollback be a pointer swap rather than a rebuild.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
