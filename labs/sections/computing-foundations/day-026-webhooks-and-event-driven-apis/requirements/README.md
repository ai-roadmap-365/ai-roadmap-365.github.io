# Dependencies — Day 026 lab

**`curl` and `openssl` only** — both preinstalled on macOS and mainstream
Linux (and available on Windows 10+ / WSL). No package installs, no accounts,
no API keys.

- `curl` — makes the sample webhook delivery (a `POST`) to a public echo
  service so you can see what a receiver receives.
- `openssl` — computes the HMAC-SHA-256 signature that authenticates a
  webhook, exactly as a real sender and receiver would.

The lab reaches one free public test service — `https://httpbin.org` — for the
live delivery step, so that step needs network access. Everything else (the
signature computation, the verify-and-compare, the retry simulation) is
**local** and works offline. With no network the scripts print a clear message
and the tests **skip** (never fail) the live delivery check, still verifying
the HMAC locally. No `sudo` required.
