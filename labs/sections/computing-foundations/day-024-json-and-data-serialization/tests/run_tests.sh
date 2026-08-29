#!/usr/bin/env bash
# Tests for the Day 024 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies real behavior with no network:
#   - the valid sample parses cleanly (exit 0)
#   - the broken sample fails to parse (non-zero exit)
#   - field extraction returns the known value (coordinates.lat == 26.9124)
#   - the sample has the expected number of top-level keys (7)
#   - the completed example script runs end to end
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${lab_dir}"
good="examples/samples/config.json"
broken="examples/samples/broken.json"
failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

# python3 must be available (the whole lab depends on it).
if command -v python3 > /dev/null 2>&1; then
  check "python3 is available" "yes"
else
  check "python3 is available" "no"
  echo
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi

# 1. Valid sample parses (exit 0).
if python3 -m json.tool "${good}" > /dev/null 2>&1; then
  check "valid sample parses cleanly" "yes"
else
  check "valid sample parses cleanly" "no"
fi

# 2. Broken sample fails to parse (non-zero exit).
if python3 -m json.tool "${broken}" > /dev/null 2>&1; then
  check "broken sample is rejected" "no"
else
  check "broken sample is rejected" "yes"
fi

# 3. Field extraction returns the known nested value.
lat="$(python3 -c "import json; print(json.load(open('${good}'))['coordinates']['lat'])" 2>/dev/null)"
if [ "${lat}" = "26.9124" ]; then
  check "coordinates.lat extracts to 26.9124" "yes"
else
  check "coordinates.lat extracts to 26.9124 (got '${lat}')" "no"
fi

# 4. Known top-level key count.
keys="$(python3 -c "import json; print(len(json.load(open('${good}'))))" 2>/dev/null)"
if [ "${keys}" = "7" ]; then
  check "sample has 7 top-level keys" "yes"
else
  check "sample has 7 top-level keys (got '${keys}')" "no"
fi

# 5. Known first array element.
first="$(python3 -c "import json; print(json.load(open('${good}'))['sensors'][0])" 2>/dev/null)"
if [ "${first}" = "temperature" ]; then
  check "sensors[0] extracts to 'temperature'" "yes"
else
  check "sensors[0] extracts to 'temperature' (got '${first}')" "no"
fi

# 6. The completed example script runs end to end.
if bash examples/json_tools.sh > /dev/null 2>&1; then
  check "examples/json_tools.sh runs successfully" "yes"
else
  check "examples/json_tools.sh runs successfully" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
