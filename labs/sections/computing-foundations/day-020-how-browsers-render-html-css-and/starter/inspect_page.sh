#!/usr/bin/env bash
# Day 020 lab — YOUR static page inspector (starter).
#
# This skeleton already resolves the file path and prints the report frame.
# Your job is the four exercises below: replace each `unknown` assignment with
# the single command shown in the comment. The completed reference version is
# examples/inspect_page.sh — try to build yours before peeking.
#
# Usage:  bash starter/inspect_page.sh [path-to-html]
set -euo pipefail

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
file="${1:-${lab_dir}/examples/page/index.html}"

if [ ! -f "${file}" ]; then
  echo "Error: file not found: ${file}" >&2
  exit 1
fi

echo "=== Static page inspection: ${file} ==="

# Exercise 1 — extract the title.
# Command: sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' "${file}" | head -n 1
title="unknown"
echo "Title: ${title}"

# Exercise 2 — count the elements (opening/void tags: <name, but not </name).
# Command: grep -oE '<[a-zA-Z][a-zA-Z0-9]*' "${file}" | wc -l | tr -d ' '
element_count="unknown"
echo "HTML elements (opening and void tags): ${element_count}"

# Exercise 3 — list each distinct element type and how many times it appears.
# Command: grep -oE '<[a-zA-Z][a-zA-Z0-9]*' "${file}" | sed 's/<//' | sort | uniq -c
echo "Distinct element types used:"
echo "  unknown — replace this line with the command in Exercise 3"

# Exercise 4 — find the JavaScript block (the behavior layer).
# Command: grep -q '<script' "${file}" && echo yes || echo no
has_script="unknown"
echo "Has <script> block (JavaScript / behavior): ${has_script}"

echo "=== End of inspection ==="
