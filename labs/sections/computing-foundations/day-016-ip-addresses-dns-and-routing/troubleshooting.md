# Troubleshooting — Day 016 lab

## `dig: command not found`

Your system does not have BIND's tools installed. Install them
(`brew install bind` on macOS if missing; `sudo apt install dnsutils` on
Debian/Ubuntu; `sudo dnf install bind-utils` on Fedora), or fall back to the
preinstalled `nslookup`: `nslookup example.com`. The scripts detect a missing
`dig` and tell you this on each line rather than crashing.

## `traceroute: command not found` (Linux)

Install it: `sudo apt install traceroute` (Debian/Ubuntu) or
`sudo dnf install traceroute` (Fedora). On Windows the equivalent command is
`tracert`, which is already present.

## traceroute shows only `* * *`, or seems to hang

Many networks rate-limit or block the probes traceroute uses, so some (or all)
hops decline to answer and print `* * *`. This is normal and does not mean the
path is broken — if the final line reaches the destination, routing works. The
lab caps traceroute at 8 hops with a 2-second per-hop timeout so it always
finishes; you can also press Ctrl+C to stop early.

## `dig MX` returns nothing, or `0 .`

That is a real, valid answer. A domain may have no MX record, or it may
publish a "null MX" (`0 .`) meaning it accepts no email. Record it as "none"
or "null MX" on your worksheet rather than treating it as an error.

## The AAAA lookup is empty

Not every name has an IPv6 address. An empty AAAA answer means the domain has
no AAAA record (or you are offline), not that something is wrong. Note "no
AAAA" and move on.

## I changed a DNS record elsewhere and still see the old value

You are seeing a cached answer whose TTL has not expired. Wait for the TTL to
pass, or query an authoritative server directly (`dig @<authoritative-ns>
name`) to bypass the cache. This caching behavior is exactly what the lesson
describes.

## The script prints a private address in the traceroute

That is expected for the first hop or two: your home router and your ISP's
internal routers use private ranges (`192.168.x`, `10.x`). Only the public
hops in the middle and the destination are globally routable.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open your Linux distribution and follow the
Linux path), or run the commands by hand: `nslookup example.com` for the
lookups and `tracert example.com` for the path.

## Tests report checks were "skipped"

That means the test could not reach the network (no `dig`, or offline), so it
skipped the live-query checks and validated structure only. This is by design
and still counts as a pass — reconnect and rerun to exercise the network
checks.
