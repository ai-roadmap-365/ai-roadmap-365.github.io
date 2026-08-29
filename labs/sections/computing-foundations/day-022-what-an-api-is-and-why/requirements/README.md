# Dependencies — Day 022 lab

**`curl` and `python3` only** — both preinstalled on macOS and mainstream
Linux (and available on Windows 10+ / WSL). No package installs, no accounts,
no API keys.

- `curl` sends the HTTP requests.
- `python3 -m json.tool` pretty-prints the JSON responses. It is part of the
  Python standard library, so nothing extra is needed.
- `jq` is **optional**. Some people like it for JSON, but this lab deliberately
  does **not** require it, so the scripts run on a stock machine.

The lab reaches three free public APIs — `jsonplaceholder.typicode.com`,
`httpbin.org`, and `api.open-notify.org` — so it needs network access to show
live output. With no network it degrades gracefully: the scripts print a clear
message and the tests skip (never fail) the live checks. No sudo required.
