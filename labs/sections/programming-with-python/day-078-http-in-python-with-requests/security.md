# Security notes — Day 078 lab

Today is the first day your code talks to another machine, so the security
notes stop being theoretical.

## What this lab does and does not reach

Every socket this lab opens goes to `127.0.0.1` — the loopback interface,
which never leaves your computer — on a port the operating system assigns at
run time. No hostname is ever resolved. No packet leaves the machine.

That is enforced, not merely stated. `tests/sitecustomize.py` replaces
`socket.socket.connect`, `socket.socket.connect_ex` and `socket.getaddrinfo`
so that any attempt to reach an address that is not the loopback interface
raises `NetworkBlocked` immediately. Section 5 of `tests/run_tests.sh` runs
the whole example suite under that guard, and then proves the guard is not
vacuous by confirming that a request to a public site under the same guard is
refused.

The one moment the lab needs the internet is the initial
`pip install -r requirements/requirements.txt`.

## The server binds loopback only

`CountingServer(("127.0.0.1", 0), DemoHandler)` binds the loopback address.
Had it bound `0.0.0.0`, the server would have been reachable from every other
machine on your network — a coffee-shop Wi-Fi network included. That one
string is the difference between a private fixture and an open service, and it
is worth remembering the next time a framework's quick-start tells you to bind
`0.0.0.0` "so you can test from your phone".

The server also has no authentication, no input validation worth the name, and
`/control/reset` will happily be called by anyone who can reach it. It is a
test fixture. Do not deploy it, and do not copy it into anything real.

## Secrets

`make_session()` reads `READINGS_TOKEN` from the environment and adds an
`Authorization: Bearer …` header only if it is set. Nothing in this lab
contains a token, and the one test that exercises the header sets
`READINGS_TOKEN=not-a-real-secret` through pytest's `monkeypatch` fixture, so
it exists for the duration of one test and nowhere else.

The rule this rehearses is worth stating plainly, because it is the rule
people break first and regret longest:

- **Never write a credential into a source file.** Source files get committed,
  pushed, copied into issue reports, and pasted into chat windows. A token in
  git history is a token you must rotate, and rewriting history does not help
  because the old objects have already been fetched.
- Read credentials from the environment, or from a file outside the
  repository, or from a secrets manager.
- Add a `.env` file to `.gitignore` *before* you create it, not after.
- Assume any token in a URL query string is in somebody's access log. Put
  credentials in headers, never in the path or the query.
- When you log a request for debugging, log the URL and the status — not the
  headers. `Authorization` and `Cookie` are the two you will leak.

## Transport security

This lab uses plain HTTP because it talks to itself over loopback, where there
is nothing to intercept. **Anything that leaves your machine must use HTTPS.**
Over plain HTTP, every header — including `Authorization` — travels as
readable text past every device between you and the server.

`requests` verifies TLS certificates by default. `verify=False` turns that off
and reduces HTTPS to obfuscation: the traffic is encrypted to whoever
answered, which may be an attacker. If a corporate proxy is intercepting your
traffic, point `requests` at that proxy's certificate bundle with
`verify="/path/to/ca-bundle.pem"` or the `REQUESTS_CA_BUNDLE` environment
variable. The correct response to a certificate error is to fix the trust
chain, never to disable the check.

## Redirects and where your credentials go

A redirect can send you to a different host. `requests` deliberately strips the
`Authorization` header when a redirect crosses hosts, which is the behaviour
you want — but it is worth knowing that the protection exists, because
hand-rolled redirect handling frequently forgets it and forwards your bearer
token to whatever the first server named in its `Location` header.

`allow_redirects=False` is the right setting whenever you care about the
difference between where you asked and where you ended up.

## Denial of service, in both directions

**Against you.** A response with no `Content-Length` and an endless body will
fill your memory if you call `.content`. Streaming with `iter_content` and a
bounded chunk size, as exercise 6 does, is the defence — combined with a limit
on how many bytes you are willing to accept before giving up.

**Against them.** A retry loop with no backoff, no jitter and no attempt cap
is a small denial-of-service tool aimed at whoever you are calling. If a
server returns 429 it is asking you to slow down; honouring `Retry-After` is
both correct and the fastest route back to being served. This is the same
argument Day 79 will make about scraping, and it is worth internalising once
rather than twice.

## Trust the body no more than the sender

`response.json()` parses whatever arrived. Nothing guarantees the shape you
expect — not the status code, not the `Content-Type`, and certainly not the
documentation. Every field you read from a response is input from another
party's machine. Validate it before it reaches anything that matters, which is
precisely the job Day 82's pydantic models will do properly.
