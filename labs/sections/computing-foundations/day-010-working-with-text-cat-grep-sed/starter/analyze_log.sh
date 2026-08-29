#!/usr/bin/env bash
# Day 010 lab — YOUR working file. Build four pipelines that analyze the
# sample web access log, then fill in text-pipelines-worksheet.md with the
# answers your script prints.
#
# Each exercise below names the EXACT tools to use. Replace the placeholder
# after each `=` (or the `echo` line) with a single pipeline. When a value is
# captured into a variable, wrap the pipeline in "$( ... )".
#
# Run it as you go to see your progress:
#   bash starter/analyze_log.sh
# When every exercise is done, check your work:
#   bash tests/run_tests.sh
set -euo pipefail

# The sample log lives beside the reference script, in examples/samples/.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
log="${here}/examples/samples/access.log"

echo "=== Log Analysis Report ==="
echo "Log file: ${log}"

# ---------------------------------------------------------------------------
# Exercise 1 — TOTAL REQUESTS.
# Each line of the log is one request. Count the lines.
# Tools: wc -l  (feed the file on stdin with `< "${log}"` so wc prints only
#        the number). Wrap the pipeline in "$( ... )" and trim spaces with
#        `| tr -d ' '`.
# Replace the word REPLACE_ME below.
total="REPLACE_ME"
echo "Total requests: ${total}"

# ---------------------------------------------------------------------------
# Exercise 2 — TOP 5 IP ADDRESSES.
# Field 1 of each line is the client IP. Build this pipeline:
#   awk '{print $1}' "${log}" | sort | uniq -c | sort -rn | head -n 5
# (awk prints the IP column, sort groups duplicates, uniq -c counts each run,
#  sort -rn ranks by count highest-first, head keeps the top 5.)
# Replace the echo line below with that pipeline.
echo "Top 5 IP addresses (count  IP):"
echo "REPLACE_ME: build the awk | sort | uniq -c | sort -rn | head pipeline"

# ---------------------------------------------------------------------------
# Exercise 3 — NUMBER OF 404s.
# The HTTP status code is field 9. Print only the lines whose status is 404,
# then count them.
# Tools: awk '$9 == 404' "${log}" | wc -l   (trim spaces with tr -d ' ').
# Replace the word REPLACE_ME below.
not_found="REPLACE_ME"
echo "404 responses: ${not_found}"

# ---------------------------------------------------------------------------
# Exercise 4 — COUNT OF UNIQUE PATHS.
# Field 7 is the requested path. Count how many DISTINCT paths appear.
# Tools: awk '{print $7}' "${log}" | sort -u | wc -l   (sort -u removes
#        duplicates; wc -l counts what is left). Trim spaces with tr -d ' '.
# Replace the word REPLACE_ME below.
unique_paths="REPLACE_ME"
echo "Unique paths: ${unique_paths}"

echo "=== End of report ==="
