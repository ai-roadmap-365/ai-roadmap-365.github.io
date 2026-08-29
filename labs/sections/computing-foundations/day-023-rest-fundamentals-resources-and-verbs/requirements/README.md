# Dependencies — Day 023 lab

**`curl` only** — preinstalled on macOS and mainstream Linux (and available on
Windows 10+ / WSL). `python3` is optional: it only pretty-prints the JSON with
`python3 -m json.tool`, and the scripts fall back to raw output when it is
absent. No package installs, no accounts, no API keys.

The lab reaches one free public REST API — `https://jsonplaceholder.typicode.com`
— so it needs network access to show live output. With no network it degrades
gracefully: the scripts print a clear message and the tests skip (never fail)
the live checks. No sudo required.

Note that JSONPlaceholder **fakes** its writes: a `POST`, `PUT`, or `DELETE`
returns a realistic status code and body, but nothing is stored server-side.
That is intentional and safe for practice — you can run the CRUD cycle as many
times as you like without changing anything.
