# Day 028 lab — Build a Weather CLI

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Consuming a Public API from the Command Line
- **Day number:** 28 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-028-consuming-a-public-api-from-the
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-028-consuming-a-public-api-from-the` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 28's lesson turns a week of API theory into one motion: read the docs, form
the request, send it, parse the reply, handle errors, present the result. This
lab makes it real. You build a small but genuinely useful **weather client**
from scratch — it calls the free, no-key Open-Meteo API for a latitude and
longitude, parses the JSON, and prints a clean current-conditions report. No
API key is required, and the client fails gracefully when the network is down.

## Learning objectives

- Form an Open-Meteo request URL with a correct query string.
- Send the request with `curl` and capture the JSON reply.
- Parse nested JSON fields (`current.temperature_2m`, `current.wind_speed_10m`)
  with `python3` (with the `jq` equivalent shown).
- Handle a failed request and a missing field so the client never prints
  garbage or crashes.
- Run a test suite that verifies the parser offline against a saved response
  and the live fetch when online.

## Prerequisites

- The Day 28 lesson, and days 22–27 (the APIs and the Web category).
- A terminal with `curl` and `python3` (both preinstalled on macOS and Linux).
- Network access for a live lookup (the lab degrades gracefully offline).

## Supported operating systems

- **macOS** and **Linux** — fully supported (`curl` and `python3` preinstalled).
- **Windows** — `curl` ships with Windows 10+ and `python3` is a free install;
  or run the scripts unmodified inside WSL.

## Hardware requirements

Any computer with an internet connection. The lab only makes ordinary web
requests and runs a few lines of Python.

## Required software

- `curl` — to send the request.
- `python3` — to parse the JSON and print the report.
- `jq` — optional, only for the commented one-line parse alternative.

See `requirements/README.md`.

## Free and open-source options

Everything here is free and open source. `curl`, `python3`, and `jq` are all
open source, and Open-Meteo, Open Notify, and JSONPlaceholder are free public
APIs with no account or key required. Nothing in this lab costs money.

## Installation

None beyond the preinstalled tools. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-028-consuming-a-public-api-from-the
```

## File structure

```text
day-028-consuming-a-public-api-from-the/
├── README.md
├── metadata.yml
├── starter/
│   ├── weather.sh                ← YOUR working file (5 exercises)
│   └── weather-worksheet.md      ← record your captured values
├── examples/
│   ├── weather.sh                ← completed reference client
│   └── sample-response.json      ← a real captured Open-Meteo response (fixed data)
├── tests/
│   └── run_tests.sh
├── expected-output/
│   └── sample-run.txt            ← real captured run (success + offline error)
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished client first (needs network)
bash examples/weather.sh              # default location (Berlin)
bash examples/weather.sh 48.85 2.35   # any latitude / longitude

# 2. Complete the five exercises in the starter, then run it
bash starter/weather.sh

# 3. Check your work (works online or offline)
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/weather.sh [LAT] [LON]` — the finished client. It builds the
  Open-Meteo request URL, fetches it with `curl -s --max-time 15`, parses the
  `current` object with `python3`, and prints time, temperature, and wind. With
  no arguments it uses a default location; pass a latitude and longitude to look
  up anywhere. If the request fails it prints a clear error and exits non-zero.
- `bash starter/weather.sh` — the same client with five numbered exercises to
  complete: build the URL, send the request, read the temperature, read the
  wind (handling a missing field), and present the report.
- `bash tests/run_tests.sh` — always runs structure checks and a **parse check**
  that drives the real client against the committed `sample-response.json` with
  no network, then — when online — does a **live fetch** and confirms a numeric
  temperature comes back. Offline, the live check is skipped (never failed).
  Exits 0 on success.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for a
real captured run. A successful lookup looks like:

```text
Weather for 52.52, 13.41
  Time:        2026-07-12T12:30
  Temperature: 29.5 °C
  Wind:        16.9 km/h
```

Your time, temperature, and wind will differ with the weather and the day.
Offline, the client prints the error shown in the sample file instead.

## Validation steps

1. `bash examples/weather.sh 52.52 13.41` prints a numeric temperature and wind.
2. Passing your own latitude and longitude changes the location in the output.
3. Complete all five exercises in `starter/weather.sh`; it produces the same
   shape of report.
4. With the network off, the client prints a clear error and exits non-zero.
5. `bash tests/run_tests.sh` prints `0 failure(s)` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `14 checks, 0 failure(s), 0 skip(s).` Offline the
live-fetch check is skipped (`... 1 skip(s).`) and the run still exits 0,
because the parse logic is verified against the committed sample response.

## Cleanup

Nothing to clean up — the scripts only make web requests and write no files.
Reset your edited starter with `git checkout -- starter/weather.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — unquoted URLs, `null`
temperatures, missing `jq`, offline behavior, and reading the raw response.

## Security notes

See [security.md](security.md). Short version: Open-Meteo needs no key, so
there is no secret to leak here — but if you later switch to a key-based API,
keep the key in an environment variable (Day 25), never in the script.

## Extension exercises

1. Add a third measurement (`relative_humidity_2m`) to the query string, the
   parse, and the report.
2. Make the client resilient to a partial response: if `current` is present but
   a field is missing, print `unavailable` for that line (the reference already
   does this — confirm it, then extend it to your new field).
3. Rewrite the fetch-and-parse in a few lines of `python3` using only the
   standard library (`urllib.request` to fetch, `json` to parse), and add a
   comment marking where an `Authorization` header would go for a key-based API.

## Navigation

- **Previous day:** Day 27 — Rate Limits, Pagination, and Error Handling.
- **Next day:** Day 29 — begins the next category (see the course schedule).
