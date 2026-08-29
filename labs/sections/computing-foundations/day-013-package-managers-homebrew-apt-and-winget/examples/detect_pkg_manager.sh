#!/usr/bin/env bash
# Day 013 lab — completed reference implementation.
#
# Detects which package managers are available on THIS machine and runs one
# safe, READ-ONLY query against each one it finds. It never installs, removes,
# or upgrades anything, never uses sudo, and needs no network connection.
#
# Detected: brew, apt, apt-get, winget, pip, pip3, npm.
set -u

echo "=== Package Manager Report ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: $(uname -s)"
echo

found=0

# have <name> -> prints the resolved path if the command exists, else nothing.
have() {
  command -v "$1" 2>/dev/null
}

# header <name> -> if <name> exists, print the FOUND line and return 0.
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

# query <description> <command...> -> label and run a read-only query, indented.
query() {
  local desc="$1"
  shift
  echo "  read-only query: ${desc}"
  "$@" 2>&1 | sed 's/^/    /' | head -n 6
}

# --- System package managers -------------------------------------------
if header brew; then
  query "brew --version" brew --version
  query "brew list | head" bash -c 'brew list 2>/dev/null | head -n 5'
  echo
fi

if header apt; then
  query "apt-cache policy (configured repositories)" apt-cache policy
  echo
elif header apt-get; then
  query "apt-cache policy (configured repositories)" apt-cache policy
  echo
fi

if header winget; then
  query "winget --version" winget --version
  echo
fi

# --- Language package managers -----------------------------------------
if header pip; then
  query "pip --version" pip --version
  echo
elif header pip3; then
  query "pip3 --version" pip3 --version
  echo
fi

if header npm; then
  query "npm --version" npm --version
  echo
fi

echo "----------------------------------------"
if [ "${found}" -eq 0 ]; then
  echo "No package managers detected on this machine."
  echo "That is a valid result: on macOS you may not have Homebrew yet; on"
  echo "minimal Linux, apt should be present. Nothing was installed."
else
  echo "Detected ${found} package manager(s) above (read-only)."
  echo "Nothing was installed, removed, or upgraded."
fi
echo "=== End of report ==="
