#!/usr/bin/env bash
# Day 024 lab — completed reference: work with JSON using only python3.
#
# Demonstrates the four skills the starter asks you to practise:
#   1. validate a JSON file            (python3 -m json.tool)
#   2. extract a nested field          (python3 one-liner; jq equivalent shown)
#   3. pretty-print a JSON file        (python3 -m json.tool)
#   4. show a broken file being rejected, with its real error
#
# Everything runs offline. Run from the lab directory:
#   bash examples/json_tools.sh
set -euo pipefail

good="examples/samples/config.json"
broken="examples/samples/broken.json"

echo "=== 1. Validate the good file ==="
# `python3 -m json.tool` parses its input and reprints it; it fails loudly
# (non-zero exit) if the input is not valid JSON.
if python3 -m json.tool "${good}" > /dev/null; then
  echo "OK: ${good} is valid JSON"
else
  echo "UNEXPECTED: ${good} failed to parse" >&2
  exit 1
fi
echo

echo "=== 2. Extract a nested field (coordinates.lat) ==="
# Python one-liner: load the file, walk into coordinates, print lat.
python3 -c "import json; print(json.load(open('${good}'))['coordinates']['lat'])"
# jq equivalent (if you have jq installed):
#   jq '.coordinates.lat' examples/samples/config.json
echo

echo "=== 3. Extract the first sensor (sensors[0]) and count top-level keys ==="
python3 -c "import json; d=json.load(open('${good}')); print(d['sensors'][0]); print(len(d), 'top-level keys')"
# jq equivalent:
#   jq '.sensors[0]' examples/samples/config.json
#   jq 'keys | length' examples/samples/config.json
echo

echo "=== 4. Pretty-print the good file ==="
python3 -m json.tool "${good}"
echo

echo "=== 5. The broken file is rejected ==="
# We EXPECT this to fail. Capture the error and show it, then continue.
if python3 -m json.tool "${broken}" > /dev/null 2> /tmp/day024_err.txt; then
  echo "UNEXPECTED: ${broken} parsed but should be invalid" >&2
  exit 1
else
  echo "As expected, ${broken} is invalid JSON. Parser said:"
  sed 's/^/    /' /tmp/day024_err.txt
  rm -f /tmp/day024_err.txt
fi
echo
echo "Done. The good file round-trips; the broken file (a trailing comma) is refused."
