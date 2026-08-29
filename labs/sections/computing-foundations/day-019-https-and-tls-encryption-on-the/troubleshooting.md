# Troubleshooting — Day 019 lab

## `openssl s_client` seems to hang and never returns

`s_client` opens the connection and then waits for you to type an HTTP
request, so it looks frozen. The fix is the `</dev/null` at the end of the
command, which feeds it empty input so it disconnects immediately. Every
command in this lab already includes it — make sure you did not drop it.

## `openssl s_client` syntax varies by version

macOS has shipped LibreSSL as `/usr/bin/openssl`, while Homebrew installs
OpenSSL 3.x, and their flags differ slightly. The flags used here
(`-connect`, `-servername`, `-showcerts`, and `x509 -noout -subject -issuer
-dates -enddate`) work on both current builds. If your build rejects a flag,
run `openssl version` to see what you have and `openssl x509 -help` /
`openssl s_client -help` for the exact spelling it expects.

## `command not found: openssl` or `curl`

Both are normally preinstalled. On a minimal Linux container, install them
with your package manager (for example `apt install openssl curl`). On
Windows, use WSL or Git Bash, both of which include them.

## Empty output / `unable to load certificate`

The connection failed before a certificate arrived — usually no network, a
captive-portal Wi-Fi login, a proxy, or a firewall. First confirm plain
connectivity with `curl -I https://example.com`; if that fails too, the
problem is the network, not the lab. The scripts detect this and print an
`OFFLINE or host unreachable` message.

## `curl` prints no TLS lines after the `grep`

Your `curl` build may word the verbose lines slightly differently, so the
`grep` filter misses them. Drop the pipe and read the whole handshake:
`curl -vI https://example.com`. Look for the `TLS handshake`, `SSL
connection using ...`, and `Server certificate:` lines.

## The certificate expiry is only a few weeks away

That is normal. Modern certificates are deliberately short-lived — Let's
Encrypt issues 90-day certificates — and are renewed automatically. A near
expiry is only a problem when nobody automated the renewal.

## I get a certificate error against a site I chose

That is a real finding, not a bug in the lab. It usually means an expired
certificate, a missing intermediate in the chain, a clock skew on your
machine, or a self-signed certificate. Note which site and which message —
diagnosing it is exactly the skill this lesson builds.
