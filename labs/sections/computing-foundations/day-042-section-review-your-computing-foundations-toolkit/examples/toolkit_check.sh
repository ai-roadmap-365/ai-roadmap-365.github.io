#!/usr/bin/env bash
# Day 042 lab — Computing Foundations Toolkit Check (completed reference).
#
# A capstone for Course 1: it inspects your own machine for the core tools
# you learned across days 1-41, reports each tool's version and the day that
# taught it, then runs three live skill checks that exercise skills from
# across the section (make a git repo, run a shell pipeline, query SQLite).
# It is read-only on your real files, needs no network, and degrades
# gracefully when a tool is missing — telling you which day covers it.
#
# Usage:  bash examples/toolkit_check.sh
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

# report_tool <label> <version-string-or-empty> <maps-to-note>
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

# --- shell (Day 8) ---
shell_path="${SHELL:-}"
[ -z "${shell_path}" ] && shell_path="$(command -v bash || true)"
report_tool "shell" "${shell_path}" "maps to Day 8: Meet the Terminal"

# --- git (Day 30) ---
if command -v git >/dev/null 2>&1; then
  report_tool "git" "$(git --version)" "maps to Day 30: Git Fundamentals"
else
  report_tool "git" "" "maps to Day 30: Git Fundamentals — install git to continue the course"
fi

# --- curl (Day 21) ---
if command -v curl >/dev/null 2>&1; then
  report_tool "curl" "$(curl --version 2>/dev/null | head -n 1 | cut -d' ' -f1-2)" "maps to Day 21: Inspecting Traffic with curl"
else
  report_tool "curl" "" "maps to Day 21: Inspecting Traffic with curl"
fi

# --- python3 (used across the course from Day 15 on) ---
if command -v python3 >/dev/null 2>&1; then
  report_tool "python3" "$(python3 --version 2>&1)" "maps to Day 15+: used across the course"
else
  report_tool "python3" "" "maps to Day 15+: install python3 before Course 2"
fi

# --- sqlite3 (Day 39) ---
if command -v sqlite3 >/dev/null 2>&1; then
  report_tool "sqlite3" "$(sqlite3 --version 2>/dev/null | cut -d' ' -f1)" "maps to Day 39: Data Storage"
else
  report_tool "sqlite3" "" "maps to Day 39: Data Storage — brew/apt install sqlite3"
fi

# --- editor (Day 36): prefer $EDITOR, else look for a common one ---
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

# skill_result <label> <ok:yes/no> <days>
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

# Skill 1: version control — init a throwaway repo and commit (Days 29-30).
git_skill="no"
if command -v git >/dev/null 2>&1; then
  tmp_repo="$(mktemp -d "${TMPDIR:-/tmp}/toolkit-check-tmp.XXXXXX")"
  if (
    cd "${tmp_repo}" &&
    git init -q &&
    echo "hello foundations" > note.txt &&
    git add note.txt &&
    git -c user.name='Toolkit Check' -c user.email='check@example.com' commit -q -m 'first commit' &&
    git log --oneline | grep -q 'first commit'
  ) >/dev/null 2>&1; then
    git_skill="yes"
  fi
  rm -rf "${tmp_repo}"
fi
skill_result "git init + commit works" "${git_skill}" "Days 29-30"

# Skill 2: the command line — build a pipeline and count matching lines (Days 10-12).
pipe_skill="no"
count="$(printf 'apple\nbanana\napricot\ncherry\n' | grep '^a' | wc -l | tr -d ' ')"
[ "${count}" = "2" ] && pipe_skill="yes"
skill_result "shell pipeline works" "${pipe_skill}" "Days 10-12"

# Skill 3: storage — create and query an in-memory SQLite table (Day 39).
sql_skill="no"
if command -v sqlite3 >/dev/null 2>&1; then
  answer="$(sqlite3 ':memory:' 'CREATE TABLE t(x INTEGER); INSERT INTO t VALUES (42); SELECT x FROM t;' 2>/dev/null)"
  [ "${answer}" = "42" ] && sql_skill="yes"
fi
skill_result "sqlite query works" "${sql_skill}" "Day 39"

echo
echo "-- Readiness --"
echo "Tools present: ${tools_present} / ${tools_total}   Skills passed: ${skills_passed} / ${skills_total}"

# Core tools that Course 2 truly needs: git, python3, and a shell + pipeline.
if [ "${git_skill}" = "yes" ] && [ "${pipe_skill}" = "yes" ] && command -v python3 >/dev/null 2>&1; then
  echo "You are ready for Course 2. Nice work finishing the foundations."
else
  echo "Almost there — revisit the day(s) shown next to any [--] line above, then re-run."
fi
echo "=== End of check ==="
