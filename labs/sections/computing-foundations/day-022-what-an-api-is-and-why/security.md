# Security notes — Day 022 lab

- **What it does:** sends ordinary GET requests to three free, public,
  no-authentication test APIs (`jsonplaceholder.typicode.com`, `httpbin.org`,
  `api.open-notify.org`) and reads the responses. No data of yours is sent
  beyond a normal request; no sudo; no files written outside the lab.
- **Public, no-auth APIs only.** These three need no key on purpose. Do not add
  authentication where none is asked for, and never invent or paste a key.
- **An API key is a secret, like a password.** Real APIs (next week) require a
  key or token in a header. Whoever holds your key can call the API *as you*, on
  your bill. Never commit a key to a repository, paste it into a screenshot or
  forum, or put it in a shared URL.
- **Never send secrets to an echo service.** `httpbin.org` reflects your request
  back to you, so anything you send is visible in the response. This lab sends
  only harmless sample values (`course`, `day`). Do not send real tokens,
  passwords, or personal data to any echo service.
- **Every API call transmits data to someone else's computer.** For these demos
  that is nothing sensitive, but the habit to build now is to know exactly what
  each request sends before you send it.
- **Only call services you are allowed to.** These three publish open APIs for
  exactly this use. Probing or hammering servers you do not own or have
  permission to test can violate their terms or the law; the retry limits in
  these scripts are deliberately gentle.
