# Dependencies — Day 021 lab

**`curl` only** — preinstalled on macOS and mainstream Linux (and available
on Windows 10+ / WSL). No package installs, no accounts, no API keys.

The lab reaches two free public test services — `https://example.com` and
`https://httpbin.org` — so it needs network access to show live output. With
no network it degrades gracefully: the scripts print a clear message and the
tests skip (never fail) the live checks. No sudo required.
