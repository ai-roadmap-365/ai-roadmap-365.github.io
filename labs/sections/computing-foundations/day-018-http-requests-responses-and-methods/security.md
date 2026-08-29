# Security notes — Day 018 lab

- **What the scripts do:** send a handful of small HTTP requests with `curl` to
  **public test endpoints only** — `https://example.com` (a reserved example
  domain) and `https://httpbin.org` / `https://httpbingo.org` (free request-
  echo test services). They write no files, change no settings, and need no
  elevated privileges.

- **The POST body is non-sensitive sample data.** The only data this lab sends
  is `{"hello":"world"}` (or values you choose). An echo service like
  `httpbin.org` **reflects your entire request back** — body and headers — and
  logs traffic. That is fine for a throwaway sample, and it is exactly why the
  next rule matters.

- **Never send real secrets to a public echo service.** Do not put a real API
  key, password, token, or personal data in an `Authorization` header, a `-d`
  body, or a query string aimed at `httpbin.org` or any test endpoint — you
  would be handing your credential to a third party and its logs. When you
  start calling real model APIs, the token goes only to that provider's own
  `https://` endpoint, never to a test service.

- **Plain HTTP is not private.** This lab uses `https://` throughout. Anything
  sent over plain `http://` travels in readable text that anyone on the path
  can see — the reason tomorrow's lesson (HTTPS and TLS) exists. Make `https://`
  your default from today.

- **Read scripts before running them.** Both scripts here are short and
  commented; read them first. Running unread shell scripts that make network
  calls is a common way to get compromised — a habit this course reinforces.
