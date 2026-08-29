#!/usr/bin/env bash
# Day 042 lab — Computing Foundations Toolkit Check (YOUR working file).
#
# This starter already prints the report skeleton and detects your OS. Your
# job is the four numbered exercises below: each names the exact command to
# fill in, replacing the `FILL_ME_IN` placeholder. The completed reference is
# in examples/toolkit_check.sh — run that first, then rebuild these four
# pieces yourself. The script is read-only on your real files and needs no
# network.
#
# Usage:  bash starter/toolkit_check.sh
set -uo pipefail

os="$(uname -s)"
tools_present=0
tools_total=0
skills_passed=0
skills_total=0

echo "=== Computing Foundations Toolkit Check ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: ${os}"
echo
echo "-- Tool inventory --"

report_tool() {
  local label="$1" version="$2" note="$3"
  tools_total=$((tools_total + 1))
  if [ -n "${version}" ]; then
    tools_present=$((tools_present + 1))
    printf '[ok]   %-9s : %s (%s)\n' "${label}" "${version}" "${note}"
  else
    printf '[--]   %-9s : not found — %s\n' "${label}" "${note}"
  fi
}

# --- shell (already done for you, as a worked example) ---
shell_path="${SHELL:-}"
[ -z "${shell_path}" ] && shell_path="$(command -v bash || true)"
report_tool "shell" "${shell_path}" "maps to Day 8: Meet the Terminal"

# ===========================================================================
# Exercise 1: report the git version.
#   Replace FILL_ME_IN with the command that prints git's version:
#       git --version
#   Keep it inside the "$(...)" so its output becomes the version string.
# ===========================================================================
if command -v git >/dev/null 2>&1; then
  git_version="$(FILL_ME_IN)"
  report_tool "git" "${git_version}" "maps to Day 30: Git Fundamentals"
else
  report_tool "git" "" "maps to Day 30: Git Fundamentals — install git to continue"
fi

# --- curl, python3, sqlite3, editor (done for you) ---
if command -v curl >/dev/null 2>&1; then
  report_tool "curl" "$(curl --version 2>/dev/null | head -n 1 | cut -d' ' -f1-2)" "maps to Day 21: Inspecting Traffic with curl"
else
  report_tool "curl" "" "maps to Day 21: Inspecting Traffic with curl"
fi
if command -v python3 >/dev/null 2>&1; then
  report_tool "python3" "$(python3 --version 2>&1)" "maps to Day 15+: used across the course"
else
  report_tool "python3" "" "maps to Day 15+: install python3 before Course 2"
fi
if command -v sqlite3 >/dev/null 2>&1; then
  report_tool "sqlite3" "$(sqlite3 --version 2>/dev/null | cut -d' ' -f1)" "maps to Day 39: Data Storage"
else
  report_tool "sqlite3" "" "maps to Day 39: Data Storage — brew/apt install sqlite3"
fi
editor_found=""
if [ -n "${EDITOR:-}" ]; then
  editor_found="\$EDITOR=${EDITOR}"
else
  for e in nvim vim nano code emacs micro; do
    if command -v "${e}" >/dev/null 2>&1; then
      editor_found="found ${e} on PATH (\$EDITOR unset)"
      break
    fi
  done
fi
report_tool "editor" "${editor_found}" "maps to Day 36: Choosing an Editor"

echo
echo "-- Skill checks --"

skill_result() {
  local label="$1" ok="$2" days="$3"
  skills_total=$((skills_total + 1))
  if [ "${ok}" = "yes" ]; then
    skills_passed=$((skills_passed + 1))
    printf '[ok]   %-30s (%s)\n' "${label}" "${days}"
  else
    printf '[--]   %-30s (%s)\n' "${label}" "${days}"
  fi
}

# ===========================================================================
# Exercise 2: verify git works by making a throwaway repo and committing.
#   Fill the two placeholder lines inside the subshell:
#     - initialise a repo quietly:   git init -q
#     - commit the staged file:      git -c user.name='Toolkit Check' \
#                                        -c user.email='check@example.com' \
#                                        commit -q -m 'first commit'
#   (The -c flags supply an identity so the commit works even if you have no
#    global git config — a trick from the git week.)
# ===========================================================================
git_skill="no"
if command -v git >/dev/null 2>&1; then
  tmp_repo="$(mktemp -d "${TMPDIR:-/tmp}/toolkit-check-tmp.XXXXXX")"
  if (
    cd "${tmp_repo}" &&
    FILL_ME_IN &&
    echo "hello foundations" > note.txt &&
    git add note.txt &&
    FILL_ME_IN &&
    git log --oneline | grep -q 'first commit'
  ) >/dev/null 2>&1; then
    git_skill="yes"
  fi
  rm -rf "${tmp_repo}"
fi
skill_result "git init + commit works" "${git_skill}" "Days 29-30"

# ===========================================================================
# Exercise 3: a mini end-to-end that touches the command-line core.
#   Build a shell pipeline (Days 10-12) that filters the four words below to
#   those starting with 'a' and counts them. Replace FILL_ME_IN with:
#       printf 'apple\nbanana\napricot\ncherry\n' | grep '^a' | wc -l | tr -d ' '
#   The expected count is 2 (apple, apricot). This one line exercises text
#   tools, pipes, and counting — the command-line core of the section.
# ===========================================================================
pipe_skill="no"
count="$(FILL_ME_IN)"
[ "${count}" = "2" ] && pipe_skill="yes"
skill_result "shell pipeline works" "${pipe_skill}" "Days 10-12"

# Skill 3 (storage): create and query an in-memory SQLite table (done for you).
sql_skill="no"
if command -v sqlite3 >/dev/null 2>&1; then
  answer="$(sqlite3 ':memory:' 'CREATE TABLE t(x INTEGER); INSERT INTO t VALUES (42); SELECT x FROM t;' 2>/dev/null)"
  [ "${answer}" = "42" ] && sql_skill="yes"
fi
skill_result "sqlite query works" "${sql_skill}" "Day 39"

echo
echo "-- Readiness --"
echo "Tools present: ${tools_present} / ${tools_total}   Skills passed: ${skills_passed} / ${skills_total}"

# ===========================================================================
# Exercise 4: self-score. Print the readiness verdict. Replace the
# placeholder with a test that says you are ready only when the git and
# pipeline skills both passed AND python3 is installed:
#     [ "${git_skill}" = "yes" ] && [ "${pipe_skill}" = "yes" ] \
#        && command -v python3 >/dev/null 2>&1
# ===========================================================================
if FILL_ME_IN; then
  echo "You are ready for Course 2. Nice work finishing the foundations."
else
  echo "Almost there — revisit the day(s) shown next to any [--] line above, then re-run."
fi
echo "=== End of check ==="
