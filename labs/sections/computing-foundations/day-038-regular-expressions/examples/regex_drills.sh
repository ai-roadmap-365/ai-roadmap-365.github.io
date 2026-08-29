#!/usr/bin/env bash
# Day 038 lab — worked regex drills with grep -E and sed -E.
#
# This is the completed REFERENCE script. It runs entirely offline against the
# committed sample file examples/samples/data.txt and demonstrates the four
# everyday regex jobs: extract, count, extract-with-groups, and reformat.
# Read each pattern's explanation, run the script, then rebuild it yourself in
# starter/regex_drills.sh.
#
# We use grep -E (extended regex) and sed -E throughout, and POSIX character
# classes like [0-9] and [[:alnum:]] rather than the PCRE shorthands \d and \w,
# because the POSIX forms behave the same in BSD grep/sed (macOS) and GNU
# grep/sed (Linux). See troubleshooting.md for the dialect differences.
set -euo pipefail

# Resolve the sample file relative to this script, so the drills run from any
# working directory.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sample="${script_dir}/samples/data.txt"

echo "=== Drill 1: extract every email address ==="
# Pattern, piece by piece:
#   [[:alnum:]._%+-]+   one or more letters/digits/dot/underscore/percent/plus/hyphen  (the local part)
#   @                   a literal @ sign
#   [[:alnum:].-]+      one or more letters/digits/dot/hyphen                           (the domain name)
#   \.                  a LITERAL dot (escaped — an unescaped . matches any character)
#   [[:alpha:]]{2,}     two or more letters                                            (the top-level domain)
# -o prints only the matched text, not the whole line.
grep -E -o '[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}' "${sample}"
echo

echo "=== Drill 2: count lines that contain a YYYY-MM-DD date ==="
# [0-9]{4}-[0-9]{2}-[0-9]{2}  four digits, hyphen, two digits, hyphen, two digits.
# -c counts MATCHING LINES rather than printing them. Note: this checks the
# SHAPE of a date, not whether the month and day are real calendar values.
grep -E -c '[0-9]{4}-[0-9]{2}-[0-9]{2}' "${sample}"
echo

echo "=== Drill 3: extract every IP-ish address ==="
# ([0-9]{1,3}\.){3}   a group of "1-3 digits then a literal dot", repeated 3 times
#   [0-9]{1,3}        a final 1-3 digit number
# This matches the SHAPE of an IPv4 address. It also matches impossible octets
# like 999.999.999.999 — good enough to extract from logs you trust, not to
# validate untrusted input.
grep -E -o '([0-9]{1,3}\.){3}[0-9]{1,3}' "${sample}"
echo

echo "=== Drill 4: reformat a date field with capture groups (sed backreferences) ==="
# Turn YYYY/MM/DD into YYYY-MM-DD.
#   ([0-9]{4})/([0-9]{2})/([0-9]{2})   capture year, month, day into groups 1, 2, 3
#   \1-\2-\3                           rebuild them joined by hyphens
# We use '#' as the sed delimiter instead of the usual '/' so the slashes in the
# date do not clash with sed's own syntax.
echo '2026/07/12' | sed -E 's#([0-9]{4})/([0-9]{2})/([0-9]{2})#\1-\2-\3#'
echo

echo "=== Done. Compare these results with the counts in the README. ==="
