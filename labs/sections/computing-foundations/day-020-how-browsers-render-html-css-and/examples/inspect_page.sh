#!/usr/bin/env bash
# Day 020 lab — static inspection of a web page's structure.
#
# Reads an HTML file with plain command-line tools (grep, sed, sort, wc) and
# reports its structure: the <title>, how many elements it contains, which
# element types appear, and whether it has CSS (<style>) and JS (<script>).
# No browser and no network are involved — this is a static view of the
# source, the complement to the live DOM you inspect in the browser.
#
# Usage:  bash examples/inspect_page.sh [path-to-html]
# Default path is examples/page/index.html relative to the lab directory.
set -euo pipefail

# Resolve the default file relative to this script's lab directory so the
# command works from anywhere.
lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
file="${1:-${lab_dir}/examples/page/index.html}"

if [ ! -f "${file}" ]; then
  echo "Error: file not found: ${file}" >&2
  exit 1
fi

echo "=== Static page inspection: ${file} ==="

# Title: the text between <title> and </title> (single line in this page).
title="$(sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' "${file}" | head -n 1)"
echo "Title: ${title}"

# Element (opening/void) tags: <name ...> but not closing tags (</name>) and
# not the <!doctype> declaration. Each element has exactly one opening tag,
# so this count equals the number of elements — comparable to the browser's
# document.querySelectorAll('*').length.
tag_names="$(grep -oE '<[a-zA-Z][a-zA-Z0-9]*' "${file}" | sed 's/<//')"
element_count="$(printf '%s\n' "${tag_names}" | grep -c . || true)"
echo "HTML elements (opening and void tags): ${element_count}"

echo "Distinct element types used:"
printf '%s\n' "${tag_names}" | sort | uniq -c | sed 's/^/  /'

# CSS and JavaScript blocks: the presentation and behavior layers.
if grep -q '<style' "${file}"; then
  echo "Has <style> block (CSS / presentation): yes"
else
  echo "Has <style> block (CSS / presentation): no"
fi

if grep -q '<script' "${file}"; then
  echo "Has <script> block (JavaScript / behavior): yes"
else
  echo "Has <script> block (JavaScript / behavior): no"
fi

echo "=== End of inspection ==="
