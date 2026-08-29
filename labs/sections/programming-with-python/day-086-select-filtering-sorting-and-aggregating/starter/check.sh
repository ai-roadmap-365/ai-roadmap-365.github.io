#!/usr/bin/env bash
# Score starter/exercises.sql against the required answers.
#
# Run from the lab directory:
#   bash starter/check.sh
#
# Exits 0 when all twelve are right, non-zero otherwise. The required answers
# are printed in the exercise comments too — nothing here is hidden. What is
# hidden is the QUERY, which is the part you are meant to write.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
db="${lab_dir}/examples/library.db"

if [ ! -f "${db}" ]; then
  echo "Building the database first (it was missing)."
  bash "${lab_dir}/examples/build_db.sh" >/dev/null || exit 1
fi

# label -> required answer. Same twelve values as the exercise comments.
expected_labels="ex01 ex02 ex03 ex04 ex05 ex06 ex07 ex08 ex09 ex10 ex11 ex12"
expected_for() {
  case "$1" in
    ex01) echo "15" ;;
    ex02) echo "10" ;;
    ex03) echo "2" ;;
    ex04) echo "4" ;;
    ex05) echo "4.16" ;;
    ex06) echo "4" ;;
    ex07) echo "Ledger of Tides" ;;
    ex08) echo "6" ;;
    ex09) echo "Ada Fenwick" ;;
    ex10) echo "3" ;;
    ex11) echo "28.0" ;;
    ex12) echo "4" ;;
    *)    echo "" ;;
  esac
}

actual="$(sqlite3 "${db}" < "${lab_dir}/starter/exercises.sql" 2>&1)" || {
  echo "Your exercises.sql did not run. SQLite said:"
  echo "${actual}"
  exit 1
}

right=0
wrong=0
echo "Exercise   your answer                required"
echo "---------  -------------------------  -------------------------"
for label in ${expected_labels}; do
  want="$(expected_for "${label}")"
  got="$(printf '%s\n' "${actual}" | grep "^${label}|" | head -1 | cut -d'|' -f2-)"
  if [ -z "${got}" ]; then
    got="(no ${label} line)"
  fi
  if [ "${got}" = "${want}" ]; then
    printf '%-9s  %-25s  %-25s  ok\n' "${label}" "${got}" "${want}"
    right=$((right + 1))
  else
    printf '%-9s  %-25s  %-25s  WRONG\n' "${label}" "${got}" "${want}"
    wrong=$((wrong + 1))
  fi
done

echo
echo "${right} correct, ${wrong} still wrong."
[ "${wrong}" -eq 0 ] || exit 1
echo "All twelve. Every one of them ran and lied to you before you fixed it."
