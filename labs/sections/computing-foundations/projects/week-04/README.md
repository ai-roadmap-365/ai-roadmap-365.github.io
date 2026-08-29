# Week 04 project — Weather Command-Line Dashboard

This week you learned what APIs are and how to consume them robustly: REST,
JSON, authentication, webhooks, rate limits, pagination, and error handling.
This project combines all of it into one real tool.

## What you are building

A command-line weather dashboard: given a place (or coordinates), it calls a
free public weather API, parses the JSON response, handles failures and rate
limits gracefully, and prints a clean daily report. It should feel like a
small, dependable program — not a fragile one-liner.

Build on the Day 28 lab's `weather.sh` (Open-Meteo, no key required) and
extend it.

## Requirements

Your dashboard must demonstrate this week's skills:

- **A real API call** to a free public API (Open-Meteo needs no key; or
  another free API — declare any key in a gitignored `.env` per Day 25, and
  never commit it).
- **JSON parsing** (Day 24) — extract the fields you need with `python3 -m
  json.tool` / a python one-liner or `jq`.
- **Error handling** (Day 27) — a failed request, a non-2xx status, or a
  missing field must produce a clear message, not a crash.
- **Rate-limit / retry politeness** (Day 27) — if you loop over multiple
  places, add a small delay and cap retries; honor `Retry-After` if present.
- **A readable report** — current conditions plus at least a short forecast,
  formatted for a human.
- **A short README** for your tool: how to run it, what it needs, and one
  example run.

## Steps

1. Start from `day-028-.../examples/weather.sh` (or write your own).
2. Add multi-place support (a list of locations) with polite pacing.
3. Add robust error handling for network failure, non-2xx, and missing
   fields.
4. Format a clean report (current temp, wind, and a short forecast).
5. Write the tool's README and test it on real places.
6. Validate against the checklist below.

## Expected output

- Running the tool for a valid place prints a clean current-conditions
  report with real numbers from the API.
- Running it with the network down (or a bad place) prints a clear,
  friendly error and exits non-zero — it does not crash or hang.
- Running it for several places produces a report for each, with a small
  delay between calls.

## Validation

- [ ] The tool calls a real, free public API and parses the JSON response.
- [ ] A network failure or bad input yields a clear message, not a stack
      trace, and a non-zero exit.
- [ ] A missing field is handled gracefully.
- [ ] Multiple-place mode paces its requests (a delay/backoff) and caps
      retries.
- [ ] No API key (if any) is hardcoded or committed — it lives in an env
      var / gitignored `.env`.
- [ ] The report is readable and shows real values.

## Troubleshooting

- Open-Meteo needs no key and is a good default. If you use a key-based API,
  keep the key in an env var (Day 25) and add `.env` to `.gitignore`.
- URL-encode query parameters (spaces, commas) — Day 28 covers this.
- If a place name doesn't resolve, geocode it first (Open-Meteo has a free
  geocoding endpoint) or accept latitude/longitude directly.
- Be polite: don't hammer the API in a tight loop — add a delay and cap
  retries (Day 27), or you may get rate-limited.
