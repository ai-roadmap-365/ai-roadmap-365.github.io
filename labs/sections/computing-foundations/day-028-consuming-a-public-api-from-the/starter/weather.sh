#!/usr/bin/env bash
# Day 028 starter — Build a Weather CLI.
#
# Complete the five exercises below to build the client piece by piece. Each
# names the exact code to write. The finished reference is in
# ../examples/weather.sh — try it yourself first, then compare.
#
# Run from the lab directory:
#   bash starter/weather.sh              # default location
#   bash starter/weather.sh 48.85 2.35   # any latitude / longitude
set -u

DEFAULT_LAT="52.52"   # Berlin
DEFAULT_LON="13.41"
LAT="${1:-$DEFAULT_LAT}"
LON="${2:-$DEFAULT_LON}"

API="https://api.open-meteo.com/v1/forecast"

# Exercise 1: build the request URL (the query string).
# A query string starts with ? and joins name=value pairs with &.
# Replace the placeholder with:
#   URL="${API}?latitude=${LAT}&longitude=${LON}&current=temperature_2m,wind_speed_10m"
URL="REPLACE_ME_EXERCISE_1"

# Exercise 2: send the request with curl and capture the reply.
# Replace the placeholder body with a real fetch (quote the URL!):
#   body="$(curl -s --max-time 15 "${URL}")"
fetch() {
  # Exercise 2 — your turn: return the JSON reply from curl for "${URL}".
  echo ""
}

# Exercise 5 (error handling): if the reply is empty, report a clear error.
# This is written for you so the client fails gracefully while you build it.
main() {
  local body
  body="$(fetch)" || body=""
  if [ -z "${body}" ]; then
    echo "Error: could not reach the weather service (no network or the request timed out)." >&2
    echo "Check your connection and try again." >&2
    exit 1
  fi
  present "${body}"
}

# Exercises 3 & 4: parse the JSON and present the report.
present() {
  local body="$1"
  WEATHER_JSON="${body}" WEATHER_LAT="${LAT}" WEATHER_LON="${LON}" python3 <<'PY'
import os, sys, json

raw = os.environ.get("WEATHER_JSON", "")
lat = os.environ.get("WEATHER_LAT", "")
lon = os.environ.get("WEATHER_LON", "")

try:
    data = json.loads(raw)
except ValueError:
    print("Error: the service did not return valid JSON.", file=sys.stderr)
    sys.exit(2)

current = data.get("current")
if not isinstance(current, dict):
    print("Error: the response did not include current conditions.", file=sys.stderr)
    sys.exit(3)

units = data.get("current_units", {})

# Exercise 3: read the temperature from the JSON.
#   Replace None below with: current.get("temperature_2m")
temperature = None  # <-- Exercise 3

# Exercise 4: read the wind, and handle a MISSING field gracefully.
#   Replace None below with: current.get("wind_speed_10m")
#   The helper already prints "unavailable" when a value is None.
wind = None  # <-- Exercise 4

def show(value, unit_key):
    if value is None:
        return "unavailable"
    unit = units.get(unit_key, "")
    return f"{value} {unit}".strip()

print(f"Weather for {lat}, {lon}")
print(f"  Time:        {current.get('time', 'unavailable')}")
print(f"  Temperature: {show(temperature, 'temperature_2m')}")
print(f"  Wind:        {show(wind, 'wind_speed_10m')}")
PY
}

main "$@"
