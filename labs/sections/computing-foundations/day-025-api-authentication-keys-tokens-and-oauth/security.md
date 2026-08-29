# Security notes — Day 025 lab

**CRITICAL: this lab uses only fake credentials against a public test server.
Nothing here is a real secret, and nothing here should ever be a real secret.**

- **Only fake credentials.** Every value the scripts send — `user:pass`,
  `token-example-123`, `demo-key`, `token-from-env-example` — is an obviously
  fake placeholder. httpbin.org's auth endpoints accept *any* credentials, so
  the lab proves how each scheme works without any real key existing.
- **Never put a real API key in a script.** A key pasted into source code is
  one accidental `git push` away from the entire internet. Read real keys from
  an environment variable at runtime; the literal string must never appear in a
  file you might commit, share, or screenshot.
- **Never commit a `.env` file.** Store real keys in a `.env` file and add that
  file to `.gitignore` so git never tracks it. Commit only a `.env.example`
  that lists the variable *names* with empty values.
- **Rotate leaked keys immediately.** The instant a real key appears in any
  public place — a repository, a log, a chat, a screenshot — treat it as
  burned: revoke it at the provider and issue a new one. Deleting the commit is
  not enough, because automated scanners find committed keys within minutes and
  the key may already be copied elsewhere.
- **Least privilege.** When a provider lets you scope a key (read-only, one
  project, a spend cap), create the narrowest key that does the job so a leak
  has the smallest possible blast radius.
- **Always use TLS.** The lab only ever contacts `https://` URLs. A credential
  sent over plain HTTP — including Basic auth, whose base64 encoding hides
  nothing — is exposed to anyone on the network path.
- **What the scripts do:** send HTTP requests with `curl` to `httpbin.org` and
  print the responses. They write no files, need no elevated privileges, and
  contain no real secret. Read them before running — a habit this course
  reinforces for every script.
