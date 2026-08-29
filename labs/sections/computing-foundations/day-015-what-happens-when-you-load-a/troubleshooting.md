# Troubleshooting — Day 015 lab

## `dig: command not found`

`dig` is not installed. Install it (`sudo apt install dnsutils` on
Debian/Ubuntu, `sudo dnf install bind-utils` on Fedora/RHEL), or use a
built-in alternative that does the same DNS lookup:

```bash
nslookup example.com
host example.com
```

## `ping` shows no replies, "Request timeout", or "Operation not permitted"

Two common causes, neither meaning the site is down:

- Many networks and servers **block ping (ICMP) on purpose**. Confirm the site
  is really reachable with `curl` instead — it uses ordinary web traffic.
- In some **containers** `ping` needs extra privileges (`CAP_NET_RAW`). Either
  run the container with that capability or just skip the ping value; the rest
  of the lab is unaffected.

## `curl: (6) could not resolve host`

The DNS stop failed. Check the spelling of the host name and your internet
connection, then run `dig` (or `nslookup`) on the same name to confirm whether
resolution is the problem.

## The `curl` timings are all `0.000000s`

`curl` could not reach the host — usually you are offline, or a proxy or
firewall blocked the request. Reconnect and retry. The reference script detects
this and prints a "could not complete the request" note instead of misleading
zeros.

## Tests report checks "skipped"

That is expected when you are **offline**: the structural checks still run and
pass, and the live network checks are skipped with a message. Re-run with a
connection to see `12 checks, 0 failure(s), 0 skipped.`

## The starter still prints `PENDING-exercise-N`

Those lines mark the four exercises you have not finished yet. Open
`starter/trace_page_load.sh`, find each `PENDING-exercise-N` echo, and replace
it with the command named in the comment just above it.

## Windows: `bash` / `dig` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the Linux path). In
native PowerShell the nearest equivalents are `Resolve-DnsName example.com`
(DNS), `Test-Connection example.com` (round-trip time), and
`curl.exe -w "..."` (timings).
