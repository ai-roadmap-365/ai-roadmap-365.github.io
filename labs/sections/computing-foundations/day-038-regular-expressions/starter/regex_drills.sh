#!/usr/bin/env bash
# Day 038 lab — YOUR regex drills.
#
# Four numbered exercises. Each has a pattern placeholder set to
# WRITE_YOUR_PATTERN_HERE. Replace each placeholder with a working extended
# regular expression, then run:  bash starter/regex_drills.sh
#
# Use grep -E and sed -E, and prefer POSIX classes ([0-9], [[:alpha:]]) over the
# PCRE shorthands \d and \w so your patterns work in both BSD (macOS) and GNU
# (Linux) tools. The completed reference is in examples/regex_drills.sh — try it
# yourself before peeking. Expected results are in the README's "Expected output".
set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sample="${script_dir}/../examples/samples/data.txt"

echo "=== Exercise 1: extract every phone-ish number ==="
# Phone numbers in the sample look like 555-0142, 555-0100, 867-5309, 234-5678.
# Write a pattern for "three digits, a hyphen, four digits" and pass it to
# grep -E -o. Expected: 5 matches.
EX1_PATTERN="WRITE_YOUR_PATTERN_HERE"   # hint: [0-9]{3}-[0-9]{4}
grep -E -o "${EX1_PATTERN}" "${sample}" || echo "(no matches yet — fill in EX1_PATTERN)"
echo

echo "=== Exercise 2: extract just the status codes from the log lines ==="
# The access-log lines end with a quoted request then a 3-digit status code,
# e.g.  "GET /health" 200 . Beware: several phone lines also end in digits, so
# a naive [0-9]{3}$ would match those too. First keep only log lines (they
# contain a quote followed by a space and three digits at end of line), then
# extract the trailing 3-digit code. Expected: 200 401 200 404 500.
EX2_SELECT="WRITE_YOUR_PATTERN_HERE"    # hint: " [0-9]{3}$   (selects log lines)
EX2_EXTRACT="WRITE_YOUR_PATTERN_HERE"   # hint: [0-9]{3}$     (pulls the code)
grep -E "${EX2_SELECT}" "${sample}" | grep -E -o "${EX2_EXTRACT}" || echo "(fill in EX2 patterns)"
echo

echo "=== Exercise 3: count how many lines are NOT comments ==="
# Comment lines begin with '#'. Use grep with -c (count) and -v (invert match)
# and an anchor to count every line that does NOT start with '#'. Expected: 16.
EX3_PATTERN="WRITE_YOUR_PATTERN_HERE"   # hint: ^#
grep -E -c -v "${EX3_PATTERN}" "${sample}" || echo "(fill in EX3_PATTERN)"
echo

echo "=== Exercise 4: reformat a day-first date with capture groups ==="
# Turn a day-first date like 12-07-2026 into ISO order 2026-07-12 by capturing
# the three fields and rebuilding them in a new order with backreferences.
# Fill in EX4_FIND (three capture groups) and EX4_REPLACE (\3-\2-\1).
EX4_FIND="WRITE_YOUR_PATTERN_HERE"      # hint: ([0-9]{2})-([0-9]{2})-([0-9]{4})
EX4_REPLACE="WRITE_YOUR_PATTERN_HERE"   # hint: \3-\2-\1
echo '12-07-2026' | sed -E "s#${EX4_FIND}#${EX4_REPLACE}#"
echo

echo "=== Done. Compare with the README's Expected output. ==="
