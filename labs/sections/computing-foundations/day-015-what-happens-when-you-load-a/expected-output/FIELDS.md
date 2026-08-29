# Required report fields (all platforms)

A correct run of `trace_page_load.sh` prints, in order:

1. `=== Request Journey Report ===`
2. `Host: <host name>`
3. `Generated on: YYYY-MM-DD`
4. `--- Stop 1: DNS lookup (name -> IP) ---` followed by one or more resolved
   IP addresses (or a clear "no address" note when offline).
5. `--- Stop 2: Round-trip time (ping -c 2) ---` followed by `ping` output with
   `time=` values (or a clear "blocked/failed" note — many networks block ping).
6. `--- Stop 3: Connection stages (curl -w timings) ---` followed by a line of
   the form `dns=<s> connect=<s> tls=<s> total=<s>` (or a "could not complete"
   note when offline).
7. `=== End of report ===`

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, `example.com`, 2026-07-12). Linux output has the same shape; only the
exact `ping` wording and the timing values differ.

## Online vs offline

- **Online:** Stops 1–3 show real values — a resolved IP, `time=` round trips,
  and a `dns=...total=...` timing line. `tests/run_tests.sh` prints
  `12 checks, 0 failure(s), 0 skipped.`
- **Offline (dig/ping/curl fail):** the report still prints all three stop
  headers with clear "unavailable" notes, and the tests skip the live-value
  checks and still exit 0 — `7 checks, 0 failure(s), 3 skipped.`
