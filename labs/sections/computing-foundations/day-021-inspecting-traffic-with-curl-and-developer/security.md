# Security notes — Day 021 lab

- **What it does:** sends ordinary GET requests to two public test services
  (`example.com`, `httpbin.org`) and reads the responses. No data of yours is
  sent beyond a normal request; no sudo; no files written outside the lab.
- **Never send real secrets to test services.** `httpbin.org` echoes back
  whatever you send. The lab uses only non-sensitive sample values. Do not
  post real API keys, tokens, or passwords to any echo service.
- **`curl -v` output can contain sensitive headers** (cookies, Authorization)
  if you point it at a site you are logged into. Redact those before sharing
  a capture. The lab targets only anonymous public endpoints.
- **Only inspect hosts you are allowed to.** Probing or scanning servers you
  do not own or have permission to test can be against their terms or the law.
