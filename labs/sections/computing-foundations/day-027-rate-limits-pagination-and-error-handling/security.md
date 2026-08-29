# Security notes — Day 027 lab

This lab makes only outbound HTTPS `GET` requests to two well-known public test
servers, needs no API key, no account, and no elevated privileges, and writes
nothing outside its own console output (plus a short-lived temp file for
response headers, which it deletes). Still, the topic itself is about being a
good citizen of other people's servers, so the security lessons are the point.

## Be a polite client

- **Honor rate limits.** When a server returns `429`, back off — do not hammer
  it harder. When it sends a `Retry-After` header, wait exactly that long; you
  cannot guess better than the server just told you.
- **Always add jitter.** A fleet of clients that all retry at the same instant
  is a self-inflicted denial-of-service (the "thundering herd"). A small random
  component on every wait spreads the load and lets the server recover.
- **Always cap your retries.** An uncapped retry loop against a struggling
  server looks exactly like an attack and can get your IP or key blocked. This
  lab's loop has a hard `MAX_ATTEMPTS` and a per-request `--max-time` for
  exactly this reason.
- **Identify yourself honestly** in real projects (a descriptive `User-Agent`)
  and read each API's terms — some forbid scraping or set explicit request
  ceilings.

## Handle errors and their bodies carefully

- **Do not log secrets.** Error responses sometimes include internal details,
  tokens, or user data. Log what you need to debug and redact the rest; never
  paste a raw error dump containing credentials into a public issue.
- **Never retry a non-idempotent write blindly.** Retrying a "create" or
  "charge" request after a timeout can duplicate the action, because the first
  attempt may have succeeded even though the response never arrived. Use an
  idempotency key or do not retry it.

## What this lab does not do

- No credentials are sent or stored.
- No inbound connections are opened; nothing listens on a port.
- The only local write is a temporary header file created with `mktemp` and
  removed immediately after use.
