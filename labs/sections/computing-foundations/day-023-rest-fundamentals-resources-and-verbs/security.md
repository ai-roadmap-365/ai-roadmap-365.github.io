# Security notes — Day 023 lab

- **What it does:** sends ordinary REST requests (GET, POST, PUT, DELETE) to
  one public test API (`jsonplaceholder.typicode.com`) and reads the
  responses. No data of yours is stored anywhere — the service fakes its
  writes. No sudo; no files written outside the lab.
- **Never send real secrets to a practice API.** The sample bodies here are
  non-sensitive placeholder values (`"title":"my post"`). Do not post real API
  keys, tokens, passwords, or personal data to any public test service.
- **Keep credentials in headers, never in URLs.** A real REST API authenticates
  with a token in the `Authorization` header. URLs appear in logs, browser
  history, and proxies, so a secret in a path or query string
  (`/posts?token=...`) is a leak. This lab uses no credentials at all.
- **Predictable URLs are enumerable.** Because `/posts/1`, `/posts/2`, ... are
  guessable, a real server must authorize every request against the specific
  resource. When you build your own API, never assume that knowing a URL
  implies the right to access it.
- **Only call APIs you are allowed to.** Public test services like this one
  invite practice traffic; probing or hammering servers you do not own or have
  permission to test can violate their terms or the law.
