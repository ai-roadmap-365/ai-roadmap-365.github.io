#!/usr/bin/env bash
# Day 028 lab — Build a Weather CLI (completed reference implementation).
#
# A small but genuinely useful API client. It reads a latitude and longitude
# (with a sensible default), calls the free, no-key Open-Meteo forecast API,
# parses the JSON reply, and prints a clean current-conditions report. A failed
# request and a missing field are both handled gracefully.
#
# Run from the lab directory:
#   bash examples/weather.sh              # default location (Berlin)
#   bash examples/weather.sh 48.85 2.35   # any latitude / longitude
#
# No API key is required — Open-Meteo is free and open. Network access is
# needed for a live lookup; offline, the script prints a clear error and exits
# non-zero. For testing, set WEATHER_SAMPLE_FILE to a saved JSON response and
# the same parser runs against that file instead of the network.
set -u

# --- Stage 1: read the docs → the endpoint and its parameters ---------------
# Docs: https://open-meteo.com/en/docs — GET /v1/forecast with latitude,
# longitude, and a `current` list of measurements. No key needed.
DEFAULT_LAT="52.52"   # Berlin
DEFAULT_LON="13.41"
LAT="${1:-$DEFAULT_LAT}"
LON="${2:-$DEFAULT_LON}"

API="https://api.open-meteo.com/v1/forecast"

# --- Stage 2: build the request → the URL with its query string -------------
# A query string starts with ? and joins name=value pairs with &.
URL="${API}?latitude=${LAT}&longitude=${LON}&current=temperature_2m,wind_speed_10m"

# --- Stage 3: send it → curl fetches the reply ------------------------------
# WEATHER_SAMPLE_FILE lets the tests drive the real parser offline against a
# committed response; normally we fetch live. --max-time fails fast on a hang.
fetch() {
  if [ -n "${WEATHER_SAMPLE_FILE:-}" ]; then
    cat "${WEATHER_SAMPLE_FILE}"
    return 0
  fi
  curl -s --max-time 15 "${URL}"
}

# --- Stages 4 & 6: parse the JSON and present the result --------------------
# Parsed here with python3 (preinstalled). The jq equivalent for one field is:
#   echo "$body" | jq '.current.temperature_2m'
# The python version also handles a missing field by printing "unavailable".
present() {
  local body="$1"
  WEATHER_JSON="${body}" WEATHER_LAT="${LAT}" WEATHER_LON="${LON}" python3 <<'PY'
import os, sys, json

raw = os.environ.get("WEATHER_JSON", "")
lat = os.environ.get("WEATHER_LAT", "")
lon = os.environ.get("WEATHER_LON", "")

# Parse the JSON; a non-JSON body is an error we report clearly.
try:
    data = json.loads(raw)
except ValueError:
    print("Error: the service did not return valid JSON.", file=sys.stderr)
    sys.exit(2)

# The measurements are nested under "current"; if that is missing, say so.
current = data.get("current")
if not isinstance(current, dict):
    print("Error: the response did not include current conditions.", file=sys.stderr)
    sys.exit(3)

units = data.get("current_units", {})

def field(name):
    """Return 'value unit', or 'unavailable' if the field is absent."""
    value = current.get(name)
    if value is None:
        return "unavailable"
    unit = units.get(name, "")
    return f"{value} {unit}".strip()

print(f"Weather for {lat}, {lon}")
print(f"  Time:        {current.get('time', 'unavailable')}")
print(f"  Temperature: {field('temperature_2m')}")
print(f"  Wind:        {field('wind_speed_10m')}")
PY
}

# --- Stage 5: handle errors → a failed request must not print garbage -------
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

main "$@"
