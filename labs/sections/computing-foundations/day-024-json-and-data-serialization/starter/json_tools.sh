#!/usr/bin/env bash
# Day 024 lab — YOUR working file. Complete the four exercises below.
#
# The completed reference version is in examples/json_tools.sh — try each
# exercise yourself first, then compare. Everything runs offline with
# python3 (preinstalled on macOS and Linux). Run from the lab directory:
#   bash starter/json_tools.sh
#
# Each exercise names the exact command to use in its comment. The commands
# below are already filled in so the script runs; work through them one at a
# time, changing the keys and files to explore, and check your understanding
# against examples/json_tools.sh.
set -euo pipefail

good="examples/samples/config.json"
broken="examples/samples/broken.json"

echo "=== Exercise 1: validate the good file ==="
# Use: python3 -m json.tool "${good}"
# It reprints the file if valid and fails with a non-zero exit if not.
# --- your command below ---
python3 -m json.tool "${good}"
echo

echo "=== Exercise 2: extract a nested field (coordinates.lat) ==="
# Use a python3 one-liner that loads the file and prints coordinates -> lat.
# Template (fill in the two keys):
#   python3 -c "import json; print(json.load(open('${good}'))['coordinates']['lat'])"
# jq equivalent (optional): jq '.coordinates.lat' examples/samples/config.json
# --- your command below ---
python3 -c "import json; print(json.load(open('${good}'))['coordinates']['lat'])"
echo

echo "=== Exercise 3: pretty-print the good file ==="
# json.tool already pretty-prints. Print it indented to the screen.
# Use: python3 -m json.tool "${good}"
# --- your command below ---
python3 -m json.tool "${good}"
echo

echo "=== Exercise 4: spot the error in the broken file ==="
# Validate the BROKEN file. It SHOULD fail — read the error it prints.
# Use: python3 -m json.tool "${broken}"
# (We wrap it so the script does not stop on the expected failure.)
# --- your command below ---
if python3 -m json.tool "${broken}" > /dev/null 2>&1; then
  echo "Hmm — broken.json parsed, but it should be invalid. Check the file."
else
  echo "Correct: broken.json is invalid. Full error message:"
  python3 -m json.tool "${broken}" || true
fi
echo
echo "Now record your findings in starter/json-worksheet.md."
