#!/usr/bin/env bash
# Day 010 lab — reference solution: analyze a web access log with pipelines.
#
# Every question below is answered by ONE pipeline of small tools connected
# with `|`. Read each pipeline left to right: the output of each command
# becomes the input (stdin) of the next. Nothing here modifies the log file;
# the pipelines only read it and print a report to standard output.
#
# Run from the lab directory:
#   bash examples/analyze_log.sh
set -euo pipefail

# Locate the sample log relative to THIS script, so the command works no
# matter which directory you launch it from.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log="${here}/samples/access.log"

echo "=== Log Analysis Report ==="
echo "Log file: ${log}"

# 1. How many requests are in the log? Each line is one request, so counting
#    lines counts requests. `wc -l` counts newlines; `< file` feeds the file
#    in on standard input so wc prints only the number (no filename).
total="$(wc -l < "${log}" | tr -d ' ')"
echo "Total requests: ${total}"

# 2. Which clients (IP addresses) made the most requests?
#    - awk '{print $1}'  -> print field 1 (the IP) of every line
#    - sort              -> group identical IPs next to each other
#    - uniq -c           -> collapse each run of duplicates to "count value"
#    - sort -rn          -> sort by that count, highest first (-r) numerically (-n)
#    - head -n 5         -> keep only the top 5 rows
echo "Top 5 IP addresses (count  IP):"
awk '{print $1}' "${log}" | sort | uniq -c | sort -rn | head -n 5

# 3. How many "404 Not Found" responses were served? In this log the status
#    code is field 9. `awk '$9==404'` prints only matching lines; piping to
#    `wc -l` counts them.
not_found="$(awk '$9 == 404' "${log}" | wc -l | tr -d ' ')"
echo "404 responses: ${not_found}"

# 4. How many DISTINCT paths were requested? Field 7 is the path.
#    `sort -u` sorts and removes duplicates in one step; `wc -l` counts what
#    remains — the number of unique paths.
unique_paths="$(awk '{print $7}' "${log}" | sort -u | wc -l | tr -d ' ')"
echo "Unique paths: ${unique_paths}"

# Bonus: list those unique paths, one per line, alphabetically.
echo "The unique paths were:"
awk '{print $7}' "${log}" | sort -u | sed 's/^/  - /'

echo "=== End of report ==="
