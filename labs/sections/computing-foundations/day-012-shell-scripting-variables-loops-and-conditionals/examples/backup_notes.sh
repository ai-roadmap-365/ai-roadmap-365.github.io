#!/usr/bin/env bash
# Day 012 lab — completed reference implementation.
#
# backup_notes.sh — summarize a directory of notes before you archive it.
# It takes a directory as its first argument (defaulting to the current
# directory), counts the regular files in it, and prints a breakdown by file
# extension. This is the kind of inventory you would generate before backing
# up or cleaning out a folder.
#
# Usage:
#   bash backup_notes.sh [DIRECTORY]
#   bash backup_notes.sh            # summarizes the current directory
#   bash backup_notes.sh ~/notes    # summarizes ~/notes
set -euo pipefail

# --- Argument with a sensible default -------------------------------------
# Take the first argument, or fall back to "." (the current directory).
target="${1:-.}"

# --- Validate the input ---------------------------------------------------
# A tool that silently accepts nonsense is a trap: fail loudly instead.
if [ ! -d "${target}" ]; then
  echo "Error: '${target}' is not a directory" >&2
  exit 1
fi

# --- A small, reusable function -------------------------------------------
# Print the extension of a filename, or "(no extension)" when it has none.
extension_of() {
  local name="$1"
  if [ "${name}" = "${name%.*}" ]; then
    # No dot in the name at all (e.g. README).
    echo "(no extension)"
  else
    # Strip everything up to and including the last dot.
    echo "${name##*.}"
  fi
}

# --- Loop over the files, counting as we go -------------------------------
total=0
extensions=""
for path in "${target}"/*; do
  # Skip anything that is not a regular file (directories, or an empty dir
  # where the glob did not expand to a real path).
  [ -f "${path}" ] || continue
  total=$((total + 1))
  extensions="${extensions}$(extension_of "$(basename "${path}")")
"
done

# --- Print the report -----------------------------------------------------
echo "=== Notes summary ==="
echo "Directory: ${target}"
echo "Total files: ${total}"
echo "By extension:"
if [ "${total}" -eq 0 ]; then
  echo "  (none)"
else
  # sort groups identical extension lines together; uniq -c collapses each
  # group into "count extension"; the loop reformats it for the report.
  printf '%s' "${extensions}" | sort | uniq -c | while read -r count ext; do
    echo "  ${ext}: ${count}"
  done
fi
echo "=== End of summary ==="
