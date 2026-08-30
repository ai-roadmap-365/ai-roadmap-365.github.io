# Security notes — Day 358

## What this lab does and does not touch

- **No network.** The token stream is a generator over a fixed list. No test opens a socket.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No real clock.** Time is a logical tick counter, so the lab cannot be affected by, or affect, system timing.

## Why streaming makes escaping harder, and what to do about it

This lab renders plain strings, so nothing here is exploitable. A real interface renders into a document, and incremental rendering changes the threat model in a specific way:

**A sanitiser written to process a complete document sees a partial one.** A tag that arrives split across two tokens — `<scr` then `ipt>` — is not a tag when either half is examined alone. Naive "sanitise the buffer each time" logic can therefore pass content that would have been caught in a single pass over the finished text.

The rule is: **escape on every append, and escape the token you are adding rather than re-processing the accumulated buffer.** Treat model output as untrusted text throughout, never as markup, and never as HTML you assemble by concatenation.

## Whole-response checks conflict with streaming

Streaming means the first tokens are visible before the last ones exist. Any check that needs the complete response — a moderation pass, a policy filter, a schema validation — cannot run before the user has already read part of the answer.

This is a genuine trade-off rather than a bug, and it has three honest resolutions:

- **Block for content that must be checked.** Accept the perceived-latency cost where it is warranted.
- **Check incrementally** where the check permits it, accepting that a violation may be briefly visible before it is caught.
- **Stream to a holding area** the user does not see until a check passes, which is blocking with extra steps and sometimes the clearest way to describe it.

Choose deliberately. Streaming by default, then discovering the moderation pass has nowhere to run, is the failure this note exists to prevent.

## Partial and cancelled responses are still content

A partial answer left on screen after an error, and a cancelled response the user stopped reading, were both generated. They may be in your logs, your traces and your cost records. They carry the same retention, privacy and logging obligations as a complete answer — a point that is easy to miss because neither "finished".

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
