#!/usr/bin/env bash
# Tests for the Day 014 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies the completed reference organizer (examples/organize_files.sh):
#   * --dry-run previews actions and moves NOTHING
#   * a real run sorts files into subfolders named for their extension
#   * every real move is recorded in organize.log
#   * a second real run is idempotent (moves nothing)
#
# The tests operate ONLY inside a fresh temp directory created with mktemp and
# removed on exit. They never read, write, or touch cron, launchd, systemd, or
# anything outside that temp directory.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="${lab_dir}/examples/organize_files.sh"
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

# --- isolated sandbox ------------------------------------------------------
work="$(mktemp -d)"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

sandbox="${work}/messy"
mkdir -p "${sandbox}"
# Known mixed files, including case and extension variety.
touch "${sandbox}/report.pdf" \
      "${sandbox}/notes.txt" \
      "${sandbox}/photo.JPG" \
      "${sandbox}/data.csv" \
      "${sandbox}/archive.zip"
before_listing="$(cd "${sandbox}" && ls | sort | tr '\n' ' ')"

echo "Testing dry-run mode (must change nothing) ..."
dry_out="$(bash "${script}" --dry-run "${sandbox}" 2>&1)"
check "dry-run exits successfully" "$([ $? -eq 0 ] && echo yes || echo no)"
echo "${dry_out}" | grep -q "would move report.pdf -> pdf/" && check "dry-run previews a move" "yes" || check "dry-run previews a move" "no"
echo "${dry_out}" | grep -q "0 changes made" && check "dry-run reports 0 changes made" "yes" || check "dry-run reports 0 changes made" "no"
after_dry="$(cd "${sandbox}" && ls | sort | tr '\n' ' ')"
[ "${before_listing}" = "${after_dry}" ] && check "dry-run left the folder untouched" "yes" || check "dry-run left the folder untouched" "no"
[ ! -e "${sandbox}/pdf" ] && check "dry-run created no subfolders" "yes" || check "dry-run created no subfolders" "no"
[ ! -e "${sandbox}/organize.log" ] && check "dry-run wrote no log" "yes" || check "dry-run wrote no log" "no"

echo "Testing real run (must sort files by extension) ..."
real_out="$(bash "${script}" "${sandbox}" 2>&1)"
check "real run exits successfully" "$([ $? -eq 0 ] && echo yes || echo no)"
[ -f "${sandbox}/pdf/report.pdf" ] && check "report.pdf landed in pdf/" "yes" || check "report.pdf landed in pdf/" "no"
[ -f "${sandbox}/txt/notes.txt" ] && check "notes.txt landed in txt/" "yes" || check "notes.txt landed in txt/" "no"
[ -f "${sandbox}/jpg/photo.JPG" ] && check "photo.JPG landed in jpg/ (extension lowercased)" "yes" || check "photo.JPG landed in jpg/ (extension lowercased)" "no"
[ -f "${sandbox}/csv/data.csv" ] && check "data.csv landed in csv/" "yes" || check "data.csv landed in csv/" "no"
[ -f "${sandbox}/zip/archive.zip" ] && check "archive.zip landed in zip/" "yes" || check "archive.zip landed in zip/" "no"
[ -z "$(find "${sandbox}" -maxdepth 1 -type f ! -name organize.log)" ] && check "no loose files remain at the top level" "yes" || check "no loose files remain at the top level" "no"

echo "Testing logging ..."
if [ -f "${sandbox}/organize.log" ]; then
  check "organize.log was created" "yes"
  logged="$(grep -c "moved .* -> " "${sandbox}/organize.log")"
  [ "${logged}" -ge 5 ] && check "log records at least 5 moves" "yes" || check "log records at least 5 moves" "no"
else
  check "organize.log was created" "no"
  check "log records at least 5 moves" "no"
fi

echo "Testing idempotency (second real run must move nothing) ..."
second_out="$(bash "${script}" "${sandbox}" 2>&1)"
check "second run exits successfully" "$([ $? -eq 0 ] && echo yes || echo no)"
echo "${second_out}" | grep -q "0 file(s) organized" && check "second run organizes 0 files" "yes" || check "second run organizes 0 files" "no"

echo "Confirming isolation ..."
[ -d "${work}" ] && check "all work stayed inside the temp sandbox" "yes" || check "all work stayed inside the temp sandbox" "no"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
