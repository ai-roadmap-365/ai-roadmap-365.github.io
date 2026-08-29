#!/usr/bin/env bash
# Day 011 lab — completed reference: explore your shell environment safely.
#
# Everything here runs inside this script (already a child of your shell), and
# the variable/PATH experiments are wrapped in a subshell "( ... )" so they
# CANNOT change your real environment. Reading system info only; writes nothing.
set -euo pipefail
shopt -s expand_aliases   # allow alias expansion inside this non-interactive script

echo "=== Environment Inspection ==="

# --- The most important environment variables ---
echo "HOME:  ${HOME:-<unset>}"
echo "USER:  ${USER:-$(id -un)}"
echo "SHELL: ${SHELL:-<unset>}"
echo "LANG:  ${LANG:-<unset>}"

# --- PATH, one directory per line ---
echo "PATH directories (one per line):"
# tr replaces each ':' separator with a newline so PATH reads as a list.
echo "${PATH}" | tr ':' '\n' | sed 's/^/  - /'
path_count="$(echo "${PATH}" | tr ':' '\n' | grep -c .)"
echo "PATH contains ${path_count} directories."

# --- Subshell variable demo: export flows DOWN to children, never back UP ---
echo "--- Subshell variable demo ---"
(
  demo_var="hello from a subshell"
  export demo_var
  # A brand-new child bash process inherits the exported value:
  bash -c 'echo "  child process sees demo_var = ${demo_var}"'
)
# Outside the subshell demo_var was never set, so it is empty here — proof that
# nothing leaked into the real environment.
echo "  after subshell, demo_var = '${demo_var:-<empty, did not leak>}'"

# --- Alias demo: shorthand for a longer command ---
echo "--- Alias demo ---"
alias greet='echo "  alias greet ran: hello"'
greet

# --- Command resolution: how PATH turns a name into a program ---
echo "--- Command resolution ---"
echo "  command -v ls  -> $(command -v ls)"
echo "  type cd        -> $(type cd)"

echo "=== End of inspection ==="
