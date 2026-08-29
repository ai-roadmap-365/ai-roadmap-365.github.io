# Requirements — Day 027 lab

This lab needs only tools that ship with, or install in one step on, macOS and
Linux. There is **no API key and no account** — the test servers are free and
public.

## Required

- **bash** 3.2 or newer — preinstalled on macOS and Linux.
- **curl** — the HTTP client used for every request. Preinstalled on macOS and
  almost every Linux distribution. Check with `curl --version`.
- **python3** — used only to count the items in a JSON array (the pagination
  step). Check with `python3 --version`.
  - macOS: preinstalled, or `brew install python`.
  - Debian/Ubuntu: `sudo apt install python3`.
  - Fedora: `sudo dnf install python3`.
- Standard utilities `awk`, `sed`, `grep`, `mktemp` — all preinstalled.

## Network

- **Internet access** is required for the live parts (the 429/500/404 demos and
  pagination). The two public test servers are:
  - `https://httpbin.org` — returns any HTTP status you ask for.
  - `https://jsonplaceholder.typicode.com` — a free paginated posts API.
- **Offline is supported**: with no network, the script and the tests degrade
  to a self-test of the backoff logic (using a stubbed failing server, no
  network calls) and still exit 0. You lose only the live demonstrations.

## Windows

Use **WSL** (Windows Subsystem for Linux) and follow the Linux instructions, or
any environment providing `bash`, `curl`, and `python3`.
