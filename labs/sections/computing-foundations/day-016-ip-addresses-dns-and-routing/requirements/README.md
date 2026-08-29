# Dependencies — Day 016 lab

This lab needs a POSIX shell and two small network tools. Both are free and
open source.

## `dig` (DNS lookup)

- **macOS:** ships with the system on most versions. If missing,
  `brew install bind` provides it.
- **Debian / Ubuntu:** `sudo apt install dnsutils`
- **Fedora / RHEL:** `sudo dnf install bind-utils`
- **Fallback:** `nslookup` is preinstalled almost everywhere (including
  Windows) and answers the same basic questions, just with less detail. The
  scripts prefer `dig`; if it is absent they tell you to use `nslookup`.

## `traceroute` (route tracing)

- **macOS:** preinstalled (`/usr/sbin/traceroute`).
- **Debian / Ubuntu:** `sudo apt install traceroute`
- **Fedora / RHEL:** `sudo dnf install traceroute`
- **Windows:** use the built-in `tracert` command instead.

> Note: `traceroute` can be **slow** (it waits for each hop) and is often
> **rate-limited or blocked** by intermediate networks, which shows up as
> `* * *` lines. That is expected, not a failure. The lab's scripts cap it at
> a few hops with a short per-hop timeout so it never hangs.

## Optional, for the extension exercises

- `whois` — domain and IP registration lookups (`sudo apt install whois` on
  Debian/Ubuntu; preinstalled on macOS).
- `ping` — reachability checks (preinstalled on macOS, Linux, and Windows).

## Network

This lab **requires network access** for its live queries. Run offline, every
script and the test suite still execute and report clearly (network checks are
skipped, not failed) — but you will not see real addresses or hops until you
are online.

There is deliberately no `requirements.txt`/`package.json`: everything here is
a system utility.
