#!/usr/bin/env bash
# Tests for the Day 005 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies that the committed sample files are what they claim to be
# (checked by content, not by name), that the reference walkthrough runs
# and shows the expected byte sequences, and that the learner's starter
# script at least runs (held to the strict standard once every
# placeholder has been replaced).
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
samples="${lab_dir}/examples/samples"
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

contains() {  # contains <haystack> <needle>
  case "$1" in *"$2"*) return 0 ;; *) return 1 ;; esac
}

echo "Checking sample files exist ..."
for f in hello.txt unicode.txt tiny.png; do
  [ -s "${samples}/${f}" ] && check "samples/${f} exists and is non-empty" "yes" \
                           || check "samples/${f} exists and is non-empty" "no"
done

echo "Checking 'file' identifies each sample by content ..."
contains "$(file "${samples}/hello.txt")" "ASCII text" \
  && check "hello.txt is ASCII text" "yes" || check "hello.txt is ASCII text" "no"
contains "$(file "${samples}/unicode.txt")" "UTF-8" \
  && check "unicode.txt is UTF-8 text" "yes" || check "unicode.txt is UTF-8 text" "no"
contains "$(file "${samples}/tiny.png")" "PNG image data" \
  && check "tiny.png is PNG image data" "yes" || check "tiny.png is PNG image data" "no"

echo "Checking the exact bytes with xxd ..."
png_sig="$(xxd -p -l 8 "${samples}/tiny.png" | tr -d '\n')"
[ "${png_sig}" = "89504e470d0a1a0a" ] \
  && check "tiny.png starts with the PNG magic bytes 89 50 4e 47 0d 0a 1a 0a" "yes" \
  || check "tiny.png starts with the PNG magic bytes 89 50 4e 47 0d 0a 1a 0a" "no"
uni_hex="$(xxd -p "${samples}/unicode.txt" | tr -d '\n')"
contains "${uni_hex}" "c3a9" \
  && check "unicode.txt contains the 2-byte sequence c3 a9 (e-acute)" "yes" \
  || check "unicode.txt contains the 2-byte sequence c3 a9 (e-acute)" "no"
contains "${uni_hex}" "e282ac" \
  && check "unicode.txt contains the 3-byte sequence e2 82 ac (euro sign)" "yes" \
  || check "unicode.txt contains the 3-byte sequence e2 82 ac (euro sign)" "no"
contains "${uni_hex}" "f09f8e89" \
  && check "unicode.txt contains the 4-byte sequence f0 9f 8e 89 (emoji)" "yes" \
  || check "unicode.txt contains the 4-byte sequence f0 9f 8e 89 (emoji)" "no"
hello_hex="$(xxd -p "${samples}/hello.txt" | tr -d '\n')"
[ "${hello_hex}" = "48656c6c6f2c20776f726c64210a" ] \
  && check "hello.txt is exactly the 14 ASCII bytes of 'Hello, world!' + newline" "yes" \
  || check "hello.txt is exactly the 14 ASCII bytes of 'Hello, world!' + newline" "no"

echo "Checking content beats extension ..."
tmp="$(mktemp -d)"
cp "${samples}/tiny.png" "${tmp}/disguised.txt"
contains "$(file "${tmp}/disguised.txt")" "PNG image data" \
  && check "'file' still sees PNG content behind a .txt name" "yes" \
  || check "'file' still sees PNG content behind a .txt name" "no"
rm -rf "${tmp}"

echo "Running the reference walkthrough (examples/inspect_bytes.sh) ..."
if output="$(bash "${lab_dir}/examples/inspect_bytes.sh" 2>&1)"; then
  check "reference walkthrough exits successfully" "yes"
  contains "${output}" "8950 4e47" \
    && check "walkthrough output shows the PNG magic bytes" "yes" \
    || check "walkthrough output shows the PNG magic bytes" "no"
  contains "${output}" "c3a9" \
    && check "walkthrough output shows the e-acute bytes" "yes" \
    || check "walkthrough output shows the e-acute bytes" "no"
  contains "${output}" "PNG image data" \
    && check "walkthrough shows 'file' identifying the PNG" "yes" \
    || check "walkthrough shows 'file' identifying the PNG" "no"
else
  check "reference walkthrough exits successfully" "no"
  echo "${output}" | sed 's/^/    /'
fi

echo "Running your starter script (starter/inspect_bytes.sh) ..."
if s_output="$(bash "${lab_dir}/starter/inspect_bytes.sh" 2>&1)"; then
  check "starter script exits successfully" "yes"
else
  check "starter script exits successfully" "no"
  echo "${s_output}" | sed 's/^/    /'
  s_output=""
fi
if contains "$(cat "${lab_dir}/starter/inspect_bytes.sh")" "not completed yet"; then
  echo "Note: starter still has unfinished exercises — structure checked only."
  contains "${s_output}" "=== Byte detective: my own run ===" \
    && check "starter prints its header" "yes" || check "starter prints its header" "no"
else
  contains "${s_output}" "8950 4e47" \
    && check "your run shows the PNG magic bytes (exercise 3)" "yes" \
    || check "your run shows the PNG magic bytes (exercise 3)" "no"
  contains "${s_output}" "c3a9" \
    && check "your run shows the e-acute bytes (exercise 2)" "yes" \
    || check "your run shows the e-acute bytes (exercise 2)" "no"
  contains "${s_output}" "ASCII text" \
    && check "your run shows 'file' trusting content over the .png name (exercise 4)" "yes" \
    || check "your run shows 'file' trusting content over the .png name (exercise 4)" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
