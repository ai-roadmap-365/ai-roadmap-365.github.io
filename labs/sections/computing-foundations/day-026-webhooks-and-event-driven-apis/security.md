# Security notes — Day 026 lab

- **Use a fake secret.** This lab's secret, `whsec_demo_do_not_use_in_production`,
  is deliberately fake and public. A real webhook secret is a credential
  exactly like an API key: keep it out of source code, out of logs, and out of
  shared terminals. Never commit a real secret to a repository.
- **Verifying signatures is what prevents forged webhooks.** A receiver's URL
  is public — anyone who learns it can `POST` to it, including an attacker
  forging a "payment succeeded" event. The security is entirely in
  *recomputing the HMAC over the body and comparing it*. A receiver that skips
  verification trusts anyone. In production, compare signatures with a
  constant-time check and reject deliveries with a stale timestamp to blunt
  replay attacks.
- **Always use HTTPS for a real receiver.** Serve the endpoint over HTTPS
  (Day 19's TLS) so the payload and signature cannot be read or altered on the
  wire. This lab only *simulates* a receiver, so it hosts nothing public.
- **Never send real secrets to an echo service.** `httpbin.org` echoes back
  whatever you send it. The lab sends only a non-sensitive sample payload and
  a fake signature. Do not post real tokens, keys, or personal data to any
  echo endpoint.
- **What the scripts do:** compute a hash locally and make one ordinary `POST`
  to a public test service. No `sudo`, no files written outside the lab, no
  data of yours sent beyond the sample payload.
