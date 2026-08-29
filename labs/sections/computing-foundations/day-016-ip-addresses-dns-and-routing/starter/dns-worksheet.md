# DNS and Routing worksheet — Day 016

Fill in every value using `bash starter/explore_dns.sh` (once you have
completed the four exercises) or the individual commands from the lesson's
hands-on section. Use `example.com` for the first column; optionally repeat
for one more site of your choice in the second.

| Field | example.com | (your choice) |
| --- | --- | --- |
| Date measured | | |
| A record — first IPv4 address | | |
| Is that A-record address public or private? | | |
| AAAA record present? (yes / no) | | |
| One AAAA (IPv6) address, if any | | |
| MX record (address, `0 .` null MX, or "none") | | |
| Number of hops from traceroute to the host | | |
| Your default gateway (hop 1 of traceroute) | | |

## How the lookup happened, in my own words

Write 4–6 sentences narrating the journey for `example.com`: your request to
the resolver, the resolver walking root → TLD → authoritative, the address
coming back, and your packets hopping to it. Use your own captured numbers,
and state explicitly whether the final address is public or private and how
you can tell.

## One thing that surprised me

One or two sentences (for example: a hop that stayed silent as `* * *`, a
domain with no MX record, or how few hops it took to cross the world).
