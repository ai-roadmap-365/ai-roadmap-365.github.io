# Troubleshooting — Day 028 lab

## The command prints nothing, or only part of the URL is used

The URL contains `&` and `?`. In the shell a bare `&` means "run in the
background", so an **unquoted** URL is cut off after the first parameter. Always
wrap the URL in double quotes, exactly as the scripts do:

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m"
```

If the raw `curl` also prints nothing, your network may be down — add
`--max-time 15` so it fails fast instead of hanging.

## The temperature comes back as `null` or `unavailable`

You asked for a measurement the response does not contain, or the `current=`
list is misspelled. Field names are case-sensitive and must match the docs:
`current=temperature_2m,wind_speed_10m`. Run the raw `curl` and look at the
`current` object to see exactly which fields the API returned.

## `jq: command not found`

`jq` is **optional** in this lab — the client parses with `python3`, which is
preinstalled. Install `jq` only to try the commented one-line alternative:
`brew install jq` (macOS) or your Linux package manager.

## `python3: command not found`

Install Python 3 (free) from your OS package manager or python.org, or run the
lab inside WSL on Windows. The parser uses only the standard library, so no
extra packages are needed.

## The API returns an error object instead of weather

If you send an invalid latitude/longitude, Open-Meteo returns a JSON object
with an `error` field and no `current`. The client detects the missing
`current` object and prints "Error: the response did not include current
conditions." — check that your coordinates are numbers in the valid range
(latitude −90 to 90, longitude −180 to 180).

## Offline

The client prints a clear error and exits non-zero when it cannot reach the
service. The test suite skips the live fetch (never fails it) and still passes,
because it verifies the parser against the committed
`examples/sample-response.json`. Reconnect to see a live lookup.
