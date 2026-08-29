#!/usr/bin/env bash
# Tests for the Day 059 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Verifies the reference package (examples/wordstats) by IMPORTING its modules
# and asserting behaviour, by running it as `python3 -m wordstats`, by proving
# each responsibility module loads on its own (no circular imports), and by
# checking the module cache imports a module only once. It then checks the
# learner's starter package — structurally while the exercises are unfinished,
# and to the same strict standard once they are complete. No network, no
# prompts. Exits 0 only if every check passes.
set -u

# Keep the working tree clean: no __pycache__ directories from importing.
export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
examples="${lab_dir}/examples"
starter="${lab_dir}/starter"
failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

# assert_py <label> <dir-with-package> <python code>
# Runs the code with <dir> prepended to sys.path; passes when it exits 0.
assert_py() {
  local label="$1" dir="$2" code="$3"
  if python3 -c "import sys; sys.path.insert(0, '${dir}')
${code}" >/dev/null 2>&1; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

# assert_run <label> <dir-with-package> <expect_exit> <needle> [stdin]
# Runs `python3 -m wordstats` from <dir> (so the package is found on the path);
# if a 5th argument is given it is piped in as stdin, otherwise sample.txt is
# passed as a file argument. Checks the exit code and that output contains the
# needle.
assert_run() {
  local label="$1" dir="$2" expect_exit="$3" needle="$4" stdin="${5:-}"
  local out code
  if [ -n "${stdin}" ]; then
    out="$(printf '%s\n' "${stdin}" | (cd "${dir}" && python3 -m wordstats) 2>&1)"
  else
    out="$( (cd "${dir}" && python3 -m wordstats sample.txt) 2>&1)"
  fi
  code=$?
  if [ "${code}" -eq "${expect_exit}" ] && printf '%s' "${out}" | grep -qF "${needle}"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (exit ${code}, expected ${expect_exit}; output: ${out})"
  fi
}

# All the behaviour a finished package must have, run against a package dir.
run_pkg_checks() {
  local dir="$1" label="$2"
  echo "Testing package in ${label} ..."
  # The public API is importable from the package root (via __init__.py).
  assert_py "import wordstats, __version__ == 1.0.0" "${dir}" \
    "import wordstats; assert wordstats.__version__ == '1.0.0'"
  # from-import of a name re-exported by __init__.py.
  assert_py "from wordstats import tokenize -> ['hello','hello','world']" "${dir}" \
    "from wordstats import tokenize; assert tokenize('Hello, HELLO world!') == ['hello', 'hello', 'world'], tokenize('Hello, HELLO world!')"
  # Submodule function, imported directly.
  assert_py "wordstats.stats.count_words counts correctly" "${dir}" \
    "from wordstats.stats import count_words; assert count_words(['x','y','x']) == {'x': 2, 'y': 1}"
  # Ties break alphabetically -> deterministic.
  assert_py "top_n orders by count then alphabetically" "${dir}" \
    "from wordstats.stats import top_n; assert top_n(['b','a','b','a','c'], 2) == [('a', 2), ('b', 2)], top_n(['b','a','b','a','c'], 2)"
  # import ... as ... binds the module under a new name.
  assert_py "import wordstats.stats as st (import-as)" "${dir}" \
    "import wordstats.stats as st; assert st.count_words(['q']) == {'q': 1}"
  # The module cache: importing twice yields the very same module object.
  assert_py "module imported once (sys.modules cache)" "${dir}" \
    "import wordstats.tokens as a; import wordstats.tokens as b; import sys; assert a is b and 'wordstats.tokens' in sys.modules"
  # tokens.py stands alone: loaded outside the package it still works, proving
  # it does not import its siblings (no circular import).
  assert_py "tokens.py is self-contained (no sibling import)" "${dir}" \
    "import importlib.util as u; s=u.spec_from_file_location('t', '${dir}/wordstats/tokens.py'); m=u.module_from_spec(s); s.loader.exec_module(m); assert m.tokenize('A a') == ['a', 'a']"
  assert_py "stats.py is self-contained (no sibling import)" "${dir}" \
    "import importlib.util as u; s=u.spec_from_file_location('s', '${dir}/wordstats/stats.py'); m=u.module_from_spec(s); s.loader.exec_module(m); assert m.count_words(['a','a']) == {'a': 2}"
  # report() is importable and pure — the payoff of the __main__ guard.
  assert_py "report() importable and pure (guard holds main back)" "${dir}" \
    "from wordstats.__main__ import report; r = report('a a b'); assert r.startswith('3 words, 2 unique'), r"
  # Runnable as a program: file argument and standard input.
  assert_run "python3 -m wordstats sample.txt -> counts" "${dir}" 0 "19 words, 10 unique"
  assert_run "python3 -m wordstats sample.txt -> top word" "${dir}" 0 "1. the: 6"
  assert_run "python3 -m wordstats (stdin)" "${dir}" 0 "1. red: 3" "red red blue green red blue"
}

# --- Reference package: always tested strictly ---
run_pkg_checks "${examples}" "examples/"

# --- Learner starter ---
echo "Testing starter/ ..."
starter_valid="yes"
for f in "${starter}/single_file.py" "${starter}/wordstats/__init__.py" \
         "${starter}/wordstats/tokens.py" "${starter}/wordstats/stats.py" \
         "${starter}/wordstats/__main__.py"; do
  python3 -c "compile(open('${f}').read(), '${f}', 'exec')" 2>/dev/null || starter_valid="no"
done
check "starter files are valid Python" "${starter_valid}"

if grep -rq 'NotImplementedError' "${starter}/wordstats"; then
  echo "Note: starter/wordstats still has unfinished exercises — testing structure only."
  grep -q 'def tokenize' "${starter}/wordstats/tokens.py" && check "starter defines tokenize" "yes" || check "starter defines tokenize" "no"
  grep -q 'def count_words' "${starter}/wordstats/stats.py" && check "starter defines count_words" "yes" || check "starter defines count_words" "no"
  grep -q 'def top_n' "${starter}/wordstats/stats.py" && check "starter defines top_n" "yes" || check "starter defines top_n" "no"
  grep -q 'def report' "${starter}/wordstats/__main__.py" && check "starter defines report" "yes" || check "starter defines report" "no"
  test -f "${starter}/wordstats/__init__.py" && check "starter has wordstats/__init__.py" "yes" || check "starter has wordstats/__init__.py" "no"
else
  run_pkg_checks "${starter}" "starter/"
  grep -q '__name__ == "__main__"' "${starter}/wordstats/__main__.py" && check "starter has the main guard" "yes" || check "starter has the main guard" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
