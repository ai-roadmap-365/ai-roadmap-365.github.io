#!/usr/bin/env bash
# Day 013 lab — YOUR working file.
#
# This starter already prints the report header and detects package managers
# for you. Your task is the four numbered exercises below: each asks you to add
# ONE safe, READ-ONLY query for a manager. Every command you add must be
# read-only — no install, no remove, no upgrade, no sudo, no network required.
#
# The completed reference version is examples/detect_pkg_manager.sh — try the
# exercises yourself first, then compare.
set -u

echo "=== Package Manager Report ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: $(uname -s)"
echo

found=0

have() { command -v "$1" 2>/dev/null; }

header() {
  local path
  path="$(have "$1")"
  if [ -n "${path}" ]; then
    found=$((found + 1))
    echo "FOUND: $1 -> ${path}"
    return 0
  fi
  return 1
}

query() {
  local desc="$1"; shift
  echo "  read-only query: ${desc}"
  "$@" 2>&1 | sed 's/^/    /' | head -n 6
}

# --- System package managers -------------------------------------------
if header brew; then
  # Exercise 1 (Homebrew): add a read-only query that prints Homebrew's version.
  #   Use exactly:  query "brew --version" brew --version
  echo "  (exercise 1: add the brew --version query here)"
  echo
fi

if header apt || header apt-get; then
  # Exercise 2 (apt): add a read-only query that shows the configured repositories
  # WITHOUT changing anything. Use exactly:
  #   query "apt-cache policy" apt-cache policy
  echo "  (exercise 2: add the apt-cache policy query here)"
  echo
fi

if header winget; then
  # Exercise 3 (winget): add a read-only query that prints winget's version.
  #   Use exactly:  query "winget --version" winget --version
  echo "  (exercise 3: add the winget --version query here)"
  echo
fi

# --- Language package managers -----------------------------------------
if header pip || header pip3; then
  # Exercise 4 (pip): add a read-only query that prints pip's version. Use the
  # name that exists on your machine, for example:
  #   query "pip3 --version" pip3 --version
  echo "  (exercise 4: add the pip/pip3 --version query here)"
  echo
fi

if header npm; then
  query "npm --version" npm --version
  echo
fi

echo "----------------------------------------"
if [ "${found}" -eq 0 ]; then
  echo "No package managers detected on this machine."
  echo "That is a valid result: nothing was installed."
else
  echo "Detected ${found} package manager(s) above (read-only)."
  echo "Nothing was installed, removed, or upgraded."
fi
echo "=== End of report ==="
