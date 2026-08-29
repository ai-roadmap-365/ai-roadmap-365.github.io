# Troubleshooting — Day 021 lab

## httpbin.org returns 503 / times out

`httpbin.org` is a shared free service and sometimes returns gateway errors
under load. The example script already retries transient 5xx and, for the
headers demo, falls back cleanly. If it keeps failing, wait a minute and
re-run, or point the command at `https://example.com` (for the non-echo
checks). A 503 is itself a valid teaching case — it is a real server error.

## `curl -v` prints a lot — where is the request vs the response?

Lines starting with `*` are connection notes, `>` are the request headers you
sent, and `<` are the response headers you got back. The example filters to
just those with `grep -E '^[*<>]'`.

## A redirect doesn't seem to work

Use `-L` to make curl follow the `Location` header; without it curl stops at
the 3xx and shows only the first response. `curl -IL <url>` follows redirects
and shows headers only.

## The timings look tiny or zero

`curl -w` reports cumulative seconds from the start: `time_appconnect` (TLS
done) ≥ `time_connect` (TCP done) ≥ `time_namelookup` (DNS done). On a warm
connection these can all be small — that is normal.

## Offline

The scripts and tests detect no network and exit 0 with a clear message.
Connect to the internet to see live output.
