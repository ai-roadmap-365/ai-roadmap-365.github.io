#!/usr/bin/env bash
# Tests for the Day 020 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the committed HTML page is well-formed enough to render and
# that the static inspector reads it correctly (title and element count).
# No browser and no network are used — everything is local text processing.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
page="${lab_dir}/examples/page/index.html"
inspector="${lab_dir}/examples/inspect_page.sh"
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

echo "Checking the committed page: ${page}"
if [ -f "${page}" ]; then
  check "page file exists" "yes"
else
  check "page file exists" "no"
  echo
  echo "${checks} checks, ${failures} failure(s)."
  exit 1
fi

# The page must contain the structural elements the lesson describes.
for needle in "<html" "<head" "<title" "<style" "<script" "<body" "<button"; do
  if grep -q "${needle}" "${page}"; then
    check "page contains ${needle}> " "yes"
  else
    check "page contains ${needle}> " "no"
  fi
done

echo "Running the inspector: ${inspector}"
if output="$(bash "${inspector}" "${page}" 2>&1)"; then
  check "inspector exits successfully" "yes"
else
  check "inspector exits successfully" "no"
  echo "${output}" | sed 's/^/    /'
fi

# Title extraction must match the page's actual <title>.
expected_title="Tiny Web Page: Structure, Style, and Behavior"
if echo "${output}" | grep -qF "Title: ${expected_title}"; then
  check "inspector extracts the correct title" "yes"
else
  check "inspector extracts the correct title" "no"
fi

# Element count must be exactly 10 (the page has one of each element type).
count_line="$(echo "${output}" | sed -n 's/^HTML elements (opening and void tags): //p')"
if [ "${count_line}" = "10" ]; then
  check "inspector counts 10 elements" "yes"
else
  check "inspector counts 10 elements (got '${count_line}')" "no"
fi

# The inspector must detect both the CSS and the JS blocks.
echo "${output}" | grep -q "Has <style> block (CSS / presentation): yes" \
  && check "inspector detects the <style> block" "yes" \
  || check "inspector detects the <style> block" "no"
echo "${output}" | grep -q "Has <script> block (JavaScript / behavior): yes" \
  && check "inspector detects the <script> block" "yes" \
  || check "inspector detects the <script> block" "no"

# The distinct-types list must include the key elements.
for el in html head title style body h1 button script; do
  echo "${output}" | grep -qE "[0-9]+ ${el}$" \
    && check "distinct types list includes ${el}" "yes" \
    || check "distinct types list includes ${el}" "no"
done

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
