#!/usr/bin/env bash
# Prove that four of the five tests next door are worthless.
#
#   bash examples/vacuous-demo/prove_it.sh
#
# It copies this directory to a temporary one, breaks `top_words` with a
# single sed, and runs the suite twice: once with only the four vacuous tests
# selected, once with the honest one. The first stays green on broken code.
# The second does not. Nothing in your working tree is modified.
set -u

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lab_dir="$(cd "${here}/../.." && pwd)"

resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found. See requirements/README.md." >&2
  exit 1
}

work="$(mktemp -d "${TMPDIR:-/tmp}/vacuous.XXXXXX")"
cp "${here}/textstats.py" "${here}/test_vacuous.py" "${here}/pytest.ini" "${work}/"

echo "Breaking top_words: ranked[:n] becomes ranked[: n - 1]"
sed -i.bak 's/return ranked\[:n\].*/return ranked[: n - 1]/' "${work}/textstats.py"
rm -f "${work}/textstats.py.bak"
echo

echo "--- the four vacuous tests, on the BROKEN module ---"
(cd "${work}" && "${pytest_bin}" . -q -k "not exactly_two_items")
vacuous_exit=$?
echo "exit: ${vacuous_exit}"
echo

echo "--- the one honest test, on the same BROKEN module ---"
(cd "${work}" && "${pytest_bin}" . -q -k "exactly_two_items" --tb=short)
honest_exit=$?
echo "exit: ${honest_exit}"
echo

rm -rf "${work}"

if [ "${vacuous_exit}" -eq 0 ] && [ "${honest_exit}" -ne 0 ]; then
  echo "Point made: four green tests, one broken function, zero warnings."
  exit 0
fi
echo "Unexpected: the demonstration did not behave as described." >&2
exit 1
