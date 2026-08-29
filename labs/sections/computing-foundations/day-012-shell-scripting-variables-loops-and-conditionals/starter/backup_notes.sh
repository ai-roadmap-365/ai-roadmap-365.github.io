#!/usr/bin/env bash
# Day 012 lab — YOUR working file. Build backup_notes.sh step by step.
#
# This skeleton already runs, but it is deliberately incomplete: five numbered
# exercises below add one real feature each. Complete them in order. After each
# one, run the script to see your progress:
#
#     bash starter/backup_notes.sh examples/sample-notes
#
# The finished result should match examples/backup_notes.sh and pass the tests
# (bash tests/run_tests.sh). Try each exercise yourself before peeking.
set -euo pipefail

# ===========================================================================
# Exercise 1 — Accept a directory argument, with a sensible default.
# Replace the line below so that `target` is the first argument ($1), or "."
# (the current directory) when no argument is given. Use the ${1:-default}
# form:   target="${1:-.}"
# ---------------------------------------------------------------------------
target="."
# ===========================================================================

# ===========================================================================
# Exercise 2 — Validate the input.
# Right now the script trusts whatever it is given. Add a conditional that
# checks the target is a directory, and if not, prints an error to standard
# error and exits with a non-zero code. Uncomment and complete:
#
#   if [ ! -d "${target}" ]; then
#     echo "Error: '${target}' is not a directory" >&2
#     exit 1
#   fi
# ===========================================================================

# ===========================================================================
# Exercise 3 — Write the extension_of function.
# This helper should print the extension of a filename, or "(no extension)"
# when there is no dot. Replace the stub body below with:
#
#   local name="$1"
#   if [ "${name}" = "${name%.*}" ]; then
#     echo "(no extension)"
#   else
#     echo "${name##*.}"
#   fi
# ---------------------------------------------------------------------------
extension_of() {
  echo "file" # <-- replace this stub with the real logic (Exercise 3)
}
# ===========================================================================

# ===========================================================================
# Exercise 4 — Loop over the files and count them.
# Fill in the loop body so that, for each REGULAR file in "${target}", it:
#   (a) skips non-files with:   [ -f "${path}" ] || continue
#   (b) adds one to total:      total=$((total + 1))
#   (c) records the extension:  append extension_of "$(basename "${path}")"
#       to the `extensions` variable, one per line (see examples/ for the
#       exact idiom).
# ---------------------------------------------------------------------------
total=0
extensions=""
for path in "${target}"/*; do
  : # <-- replace this no-op with the loop body (Exercise 4)
done
# ===========================================================================

# --- Print the report -----------------------------------------------------
echo "=== Notes summary ==="
echo "Directory: ${target}"
echo "Total files: ${total}"
echo "By extension:"
if [ "${total}" -eq 0 ]; then
  echo "  (none)"
else
  # =========================================================================
  # Exercise 5 — Print the by-extension breakdown.
  # Turn the collected `extensions` into sorted counts. Replace the echo
  # stub below with the pipeline:
  #
  #   printf '%s' "${extensions}" | sort | uniq -c | while read -r count ext; do
  #     echo "  ${ext}: ${count}"
  #   done
  # -------------------------------------------------------------------------
  echo "  (fill in Exercise 5 to see the breakdown)"
  # =========================================================================
fi
echo "=== End of summary ==="
