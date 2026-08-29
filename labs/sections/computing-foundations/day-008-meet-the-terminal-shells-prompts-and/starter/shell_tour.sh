#!/usr/bin/env bash
# Day 008 lab — YOUR shell tour.
#
# This starter already prints the section headers and the demonstration lines
# (the shell process, your prompt string, a history sample, and 'type echo').
# Your job is the five numbered exercises below: replace each `unknown` with the
# single command shown in the comment, wrapped in $(...) so its output is
# captured. The finished reference version is in examples/shell_tour.sh — try it
# yourself first, then run this, then run the tests.
set -u

echo "=== Shell Tour ==="
echo "Generated on: $(date '+%Y-%m-%d')"

echo
echo "--- Which shell am I running? ---"

# Exercise 1: set current_shell using the command:  echo $0
#   ($0 is the name of the shell or script running right now.)
current_shell="unknown"

# Exercise 2: set default_shell using the command:  echo $SHELL
#   ($SHELL is your DEFAULT login shell — it may differ from the one running now.)
default_shell="unknown"

echo "Current shell (echo \$0): ${current_shell}"
echo "Default shell (echo \$SHELL): ${default_shell}"
echo "Shell process (ps -p \$\$):"
ps -p $$ | sed 's/^/    /'

echo
echo "--- What does my prompt look like? ---"
if [ -n "${PS1:-}" ]; then
  echo "Prompt string (echo \"\$PS1\"): ${PS1}"
else
  echo "Prompt string (echo \"\$PS1\"): (empty in this non-interactive run — try it in your interactive shell)"
fi

echo
echo "--- A handful of everyday commands ---"

# Exercise 3: set here using the command:  pwd
#   (pwd prints the working directory — the folder the shell is standing in.)
here="unknown"

# Exercise 4: set today using the command:  date
#   (date takes no options and no arguments; it prints the current date/time.)
today="unknown"

# Exercise 5: set me using the command:  whoami
#   (whoami prints your username — the identity your commands act as.)
me="unknown"

echo "Working directory (pwd): ${here}"
echo "Echo demo (echo hello): $(echo hello)"
echo "Date (date): ${today}"
echo "User (whoami): ${me}"

echo
echo "--- Recent command history (history | tail) ---"
hist_output="$(history 2>/dev/null | tail || true)"
if [ -n "${hist_output}" ]; then
  echo "${hist_output}" | sed 's/^/    /'
else
  echo "    (no history in this non-interactive run — run 'history | tail' in your terminal)"
fi

echo
echo "--- What kind of thing is 'echo'? ---"
echo "type echo: $(type echo)"

echo
echo "=== End of tour ==="
