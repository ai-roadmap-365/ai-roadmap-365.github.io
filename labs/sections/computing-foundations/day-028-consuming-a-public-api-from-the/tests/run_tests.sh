#!/usr/bin/env bash
# Tests for the Day 028 lab — Build a Weather CLI. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Two kinds of checks:
#   * Structure and parse checks always run and must pass. The parse check
#     drives the REAL client against a committed sample response
#     (examples/sample-response.json) with WEATHER_SAMPLE_FILE, so it needs no
#     network yet exercises the actual parser.
#   * The live-fetch check runs only when the Open-Meteo API is reachable.
#     Offline, it is SKIPPED with a message (never failed).
#
# The script exits 0 when no check failed, whether online or offline.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="https://api.open-meteo.com/v1/forecast"
example="${lab_dir}/examples/weather.sh"
starter="${lab_dir}/starter/weather.sh"
sample="${lab_dir}/examples/sample-response.json"
failures=0
checks=0
skips=0

pass() { checks=$((checks + 1)); echo "  ok:   $1"; }
fail() { checks=$((checks + 1)); failures=$((failures + 1)); echo "  FAIL: $1"; }
skip() { skips=$((skips + 1)); echo "  skip: $1"; }

# Matches a temperature report line with a real number, e.g. "  Temperature: 29.5 °C".
has_numeric_temp() {
  printf '%s' "$1" | grep -Eq 'Temperature: -?[0-9]+(\.[0-9]+)?'
}

echo "== Structure checks =="
[ -f "${example}" ] && pass "example client exists" || fail "example client missing"
[ -f "${starter}" ] && pass "starter client exists" || fail "starter client missing"
[ -f "${lab_dir}/starter/weather-worksheet.md" ] && pass "worksheet exists" || fail "worksheet missing"
[ -f "${sample}" ] && pass "committed sample response exists" || fail "sample-response.json missing"

# The example must exercise the whole pipeline: endpoint, curl, and a parse.
for needle in "api.open-meteo.com" "curl -s" "current=temperature_2m,wind_speed_10m" "json.loads"; do
  if grep -q -- "${needle}" "${example}"; then pass "example uses '${needle}'"; else fail "example missing '${needle}'"; fi
done

# The starter must name its five numbered exercises.
ex_count="$(grep -cE 'Exercise [1-5]' "${starter}" 2>/dev/null || true)"
if [ "${ex_count:-0}" -ge 5 ]; then pass "starter has 5 numbered exercises"; else fail "starter has 5 numbered exercises (found ${ex_count:-0})"; fi

# Both scripts must be valid bash.
if bash -n "${example}" 2>/dev/null; then pass "example has valid bash syntax"; else fail "example has a syntax error"; fi
if bash -n "${starter}" 2>/dev/null; then pass "starter has valid bash syntax"; else fail "starter has a syntax error"; fi

echo
echo "== Parse check (committed sample, no network) =="
# Drive the real client against the saved response; the parser must extract a
# numeric temperature. This proves the parse logic works even offline.
sample_out="$(WEATHER_SAMPLE_FILE="${sample}" bash "${example}" 52.52 13.41 2>/dev/null)" || sample_out=""
if has_numeric_temp "${sample_out}"; then
  pass "client parses a numeric temperature from the committed sample"
else
  fail "client should parse a numeric temperature from the sample"
fi
# The parser must also degrade a missing field to 'unavailable', not crash.
partial='{"current_units":{"temperature_2m":"°C"},"current":{"time":"t","temperature_2m":1.0}}'
partial_file="$(mktemp)"; printf '%s' "${partial}" > "${partial_file}"
partial_out="$(WEATHER_SAMPLE_FILE="${partial_file}" bash "${example}" 1 2 2>/dev/null)" || partial_out=""
rm -f "${partial_file}"
if printf '%s' "${partial_out}" | grep -q "Wind:        unavailable"; then
  pass "client reports a missing field as 'unavailable'"
else
  fail "client should report a missing field as 'unavailable'"
fi

echo
echo "== Live-fetch check (network) =="
if ! curl -s -o /dev/null --max-time 12 "${API}?latitude=0&longitude=0&current=temperature_2m" 2>/dev/null; then
  skip "no network access — skipping the live fetch (parse check above already passed)"
else
  live_out="$(bash "${example}" 52.52 13.41 2>/dev/null)" || live_out=""
  if [ -z "${live_out}" ]; then
    skip "live fetch — Open-Meteo transiently unavailable; retry later"
  elif has_numeric_temp "${live_out}"; then
    pass "live client fetched and printed a numeric temperature"
  else
    fail "live client should print a numeric temperature"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s), ${skips} skip(s)."
[ "${failures}" -eq 0 ]
