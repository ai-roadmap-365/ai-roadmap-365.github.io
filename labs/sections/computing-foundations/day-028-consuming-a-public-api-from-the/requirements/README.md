# Dependencies — Day 028 lab

**`curl` and `python3`** — both preinstalled on macOS and mainstream Linux
(and available on Windows 10+ / WSL). No package installs, no accounts, and
**no API key**: Open-Meteo is a free, open, no-key weather API.

- `curl` — sends the HTTP request.
- `python3` — parses the JSON response and prints the report (standard library
  only; nothing to `pip install`).
- `jq` — **optional**. The client parses with `python3` by default; `jq` is
  used only in a commented one-line alternative. Install it if you want to try
  that line: `brew install jq` (macOS) or your package manager (Linux).

The lab reaches the free public service `https://api.open-meteo.com`, so it
needs network access for a live lookup. With no network it degrades gracefully:
the client prints a clear error and exits non-zero, and the test suite verifies
the parser against the committed `examples/sample-response.json` and skips (never
fails) the live check. No sudo required.
