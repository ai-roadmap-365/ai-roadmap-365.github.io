# Security notes — Day 335

## What this lab does and does not touch

- **No GitHub account, no runner, no workflow is executed.** The input is a described pipeline. Nothing is dispatched and no token is read.
- **No network**, no credentials.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## `pull_request_target` is the one to understand

This is the single most dangerous line in GitHub Actions, and it is dangerous because it looks like a small variation on a safe thing.

- **`pull_request`** checks out the fork's code and runs with a read-only token and **no secrets**. A hostile pull request can run whatever it likes and gain nothing.
- **`pull_request_target`** runs in the context of the *base* repository — with your secrets available — and exists so that a workflow can label or comment on a PR from a fork.

The trap is combining it with a checkout of the fork's code. At that point untrusted code executes with your repository secrets in the environment, and exfiltrating them is a one-line change to a test file or a `Makefile`. This has been used against real projects repeatedly.

The rule that survives: **`pull_request_target` may inspect a pull request; it must never run its code.** If you need both, split into two workflows — one that runs untrusted code with no secrets, one that reacts to the result.

The lab reports every secret-using job under a `pull_request_target` trigger for this reason.

## Least privilege for the token

`GITHUB_TOKEN` defaults to broad permissions in older repositories. Set them explicitly, at the top of the workflow and narrowed per job:

```yaml
permissions:
  contents: read
```

Then grant only what a specific job needs. A lint job needs nothing; a job that pushes a release needs `contents: write` and nothing else.

## Third-party actions are supply chain

`uses: some-org/some-action@v3` executes somebody else's code with your token. A tag is mutable — the author, or anyone who compromises them, can move `v3`. Pin to a full commit SHA for anything that touches secrets, and read what you are pinning.

This is Day 347's subject and it belongs here too, because CI is where most organisations run the most untrusted code with the most privilege.

## Caches are writable by the jobs that read them

A cache is keyed content that later runs restore and trust. A workflow that can be triggered from a fork and writes to a shared cache can poison what a later privileged run restores. Scope cache keys so untrusted runs cannot write to a key a trusted run reads.

## A gate that never fails is a security problem too

The lab reports jobs that have never failed. The framing is usually about time, and there is a security version: a scanner that has never reported anything is either configured wrongly or nobody reads its output. Both mean the control does not exist while appearing on the diagram.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
