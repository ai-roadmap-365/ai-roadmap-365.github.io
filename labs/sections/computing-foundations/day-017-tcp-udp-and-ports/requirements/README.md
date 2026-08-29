# Dependencies — Day 017 lab

**None that you have to install on a normal machine.** Every tool this lab
uses ships with macOS and mainstream Linux distributions:

- `bash` ≥ 3.2 (preinstalled on macOS and Linux)
- Standard utilities: `uname`, `date`, `awk`, `sort`
- **A listening-socket viewer** — one of:
  - `lsof` (preinstalled on macOS; `sudo apt install lsof` on Debian/Ubuntu)
  - `ss` (from `iproute2`, preinstalled on most modern Linux)
  - `netstat` (from `net-tools`; the last-resort fallback)
- **`nc` / netcat** for the loopback connection test:
  - macOS ships BSD `nc` at `/usr/bin/nc`
  - Linux: `sudo apt install netcat-openbsd` (Debian/Ubuntu) or
    `sudo dnf install nmap-ncat` (Fedora/RHEL) if it is missing

The script degrades gracefully: if no socket viewer is found it says so, and
if `nc` is missing it skips the probe with a clear message. Nothing here
needs `sudo`, a network connection to the outside world, an API key, or a
purchase — it only reads local state and probes `127.0.0.1`.
