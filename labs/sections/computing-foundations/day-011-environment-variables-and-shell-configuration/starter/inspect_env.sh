#!/usr/bin/env bash
# Day 011 lab — YOUR working file: explore your shell environment safely.
#
# Four exercises are marked below. Each comment names the EXACT command to use.
# Replace each numbered placeholder with that command, then run:
#   bash starter/inspect_env.sh
# The completed reference is in examples/inspect_env.sh — try yours first.
#
# Everything runs inside this script (a child of your shell); the subshell
# "( ... )" experiment cannot touch your real environment.
set -euo pipefail
shopt -s expand_aliases   # allow alias expansion inside this non-interactive script

echo "=== Environment Inspection ==="

# The most important environment variables are already printed for you:
echo "HOME:  ${HOME:-<unset>}"
echo "USER:  ${USER:-$(id -un)}"
echo "SHELL: ${SHELL:-<unset>}"
echo "LANG:  ${LANG:-<unset>}"

# --- Exercise 1: print PATH one directory per line ---
# Use: echo "${PATH}" | tr ':' '\n'
echo "PATH directories (one per line):"
REPLACE_ME_1

# --- Exercise 2: export a variable inside the subshell so the child sees it ---
echo "--- Subshell variable demo ---"
(
  demo_var="hello from a subshell"
  # Exercise 2: mark demo_var for inheritance. Use: export demo_var
  REPLACE_ME_2
  bash -c 'echo "  child process sees demo_var = ${demo_var}"'
)
echo "  after subshell, demo_var = '${demo_var:-<empty, did not leak>}'"

# --- Exercise 3: define an alias, then call it ---
echo "--- Alias demo ---"
# Exercise 3: define an alias named greet. Use: alias greet='echo "  alias greet ran: hello"'
REPLACE_ME_3
greet

# --- Exercise 4: show which file PATH resolves for the ls command ---
echo "--- Command resolution ---"
# Exercise 4: print the resolved path of ls. Use: command -v ls
echo "  command -v ls  -> $(REPLACE_ME_4)"
echo "  type cd        -> $(type cd)"

echo "=== End of inspection ==="
