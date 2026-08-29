# Required report sections (all platforms)

A correct run of `inspect_ports.sh` prints, in order:

1. `=== Ports and Connections ===`
2. `Generated on: YYYY-MM-DD`
3. `Operating system kernel: Darwin` (macOS) or `Linux`
4. `--- Listening TCP ports ---` followed by a table with columns
   `PORT  CLASS  LIKELY SERVICE  PROCESS` (one row per listening TCP port;
   the exact ports depend on what your machine is running)
5. `--- Well-known vs ephemeral ---` with the three IANA ranges
6. `--- Loopback connection test ---` with one OPEN and one closed probe
   against `127.0.0.1`
7. `=== End of report ===`

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, 2026-07-12). **Your ports will differ** — that is the whole point;
the set of listening ports is a property of your machine, not a fixed answer.

## Platform differences

- **macOS** uses `lsof -nP -iTCP -sTCP:LISTEN`. The `PROCESS` column shows
  the command name (e.g. `ControlCe`, `node`, `rapportd`). Ports `5000` and
  `7000` are commonly held by the macOS AirPlay receiver / Control Center.
- **Linux** uses `ss -tlnp` (from `iproute2`), falling back to `ss -tlnH`
  for parsing, then `netstat -tln` (from `net-tools`) if `ss` is absent. The
  kernel line reads `Linux`; the `PROCESS` column comes from `ss`'s
  `users:(("name",pid=...))` field (only shown for your own processes, or all
  processes under `sudo` — this lab never uses `sudo`, so you may see fewer
  process names).
- On **either** platform, if a service is bound only to the IPv6 loopback
  `[::1]`, the IPv4 `nc -z 127.0.0.1` probe will not reach it; the script
  says so honestly and suggests probing `::1` instead. This is expected
  behaviour, not a bug.
- **Windows**: use `netstat -an | findstr LISTENING` in PowerShell, or run
  the script unchanged inside WSL (which behaves as Linux).
