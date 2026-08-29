#!/usr/bin/env bash
# Day 008 lab — completed reference implementation: a guided tour of your shell.
#
# Prints, in clearly labelled sections: which shell is running, your default
# shell, the shell process, your prompt string, and the output of a handful of
# everyday commands (pwd, echo, date, whoami, history, type). Every command is
# read-only — it inspects your session and changes nothing.
#
# Works in bash and zsh on macOS and Linux. Run it with:
#   bash examples/shell_tour.sh
set -u

echo "=== Shell Tour ==="
echo "Generated on: $(date '+%Y-%m-%d')"

echo
echo "--- Which shell am I running? ---"
# $0 is the name of the shell (or script) currently running.
echo "Current shell (echo \$0): $0"
# $SHELL is your DEFAULT login shell, which may differ from the one running now.
echo "Default shell (echo \$SHELL): ${SHELL:-unknown}"
# ps -p $$ shows the process of the current shell ($$ is its process id).
echo "Shell process (ps -p \$\$):"
ps -p $$ | sed 's/^/    /'

echo
echo "--- What does my prompt look like? ---"
# PS1 is the prompt-string template. In a non-interactive script it is often
# empty; run 'echo \"\$PS1\"' directly in your interactive shell to see it.
if [ -n "${PS1:-}" ]; then
  echo "Prompt string (echo \"\$PS1\"): ${PS1}"
else
  echo "Prompt string (echo \"\$PS1\"): (empty in this non-interactive run — try it in your interactive shell)"
fi

echo
echo "--- A handful of everyday commands ---"
echo "Working directory (pwd): $(pwd)"
echo "Echo demo (echo hello): $(echo hello)"
echo "Date (date): $(date)"
echo "User (whoami): $(whoami)"

echo
echo "--- Recent command history (history | tail) ---"
# 'history' is a shell built-in; in a non-interactive script the list may be
# empty. This is expected — the point is that your INTERACTIVE shell records it.
hist_output="$(history 2>/dev/null | tail || true)"
if [ -n "${hist_output}" ]; then
  echo "${hist_output}" | sed 's/^/    /'
else
  echo "    (no history in this non-interactive run — run 'history | tail' in your terminal)"
fi

echo
echo "--- What kind of thing is 'echo'? ---"
# 'type' tells you whether a name is a built-in, a program on disk, or an alias.
echo "type echo: $(type echo)"

echo
echo "=== End of tour ==="
