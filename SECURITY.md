# Security policy

## What this repository is

A course: written lessons and hands-on labs. There is no deployed service, no
database holding anyone's data, and no user accounts. That limits the security
surface considerably — but not to nothing.

## Reporting a vulnerability

Please report privately through
[GitHub Security Advisories](https://github.com/ai-roadmap-365/ai-roadmap-365.github.io/security/advisories/new)
rather than opening a public issue.

Include what you found, which file or lab it is in, and how to reproduce it.
You can expect an acknowledgement within a few days.

## What is worth reporting

- **A lab that does something dangerous** — deletes outside its own directory,
  needs `sudo` without saying why, opens a network listener that is not bound
  to `127.0.0.1`, or writes outside the workspace.
- **A committed secret** — an API key, token or password anywhere in the
  history. `validate:secrets` scans every tracked file on every run, but a
  scanner is not a proof.
- **Personal data** — any real email address, name or record that should not be
  there. Every person, address and record in the seed data is invented; if one
  looks real, tell me.
- **A lab teaching an insecure pattern without flagging it** — for example
  building SQL by string concatenation or disabling certificate verification,
  outside a section that is explicitly demonstrating the danger. Several
  lessons *do* demonstrate attacks deliberately, always against a throwaway
  local target and always labelled.
- **A supply-chain problem** in a pinned dependency in any `requirements/`.

## What is not a vulnerability here

- A lab that fails on your machine — that is a bug, and an ordinary issue is
  the right place for it.
- A lesson demonstrating an insecure practice on purpose, where the text says
  so and the target is a local throwaway.

## Safety rules every lab already follows

- Runs offline unless `metadata.yml` declares `requires_network: true`
- Never needs `sudo`
- Writes only inside its own directory or a temporary directory
- Binds test servers to `127.0.0.1` on an ephemeral port
- Reads any credential from the environment, never from a file in the repo
- Cleans up after itself, with the cleanup commands listed in `metadata.yml`
