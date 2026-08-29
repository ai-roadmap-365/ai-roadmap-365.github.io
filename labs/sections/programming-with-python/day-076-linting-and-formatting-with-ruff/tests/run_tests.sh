#!/usr/bin/env bash
# Tests for the Day 076 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# What this suite proves, in order:
#
#   * the messy module WORKS — its pytest suite is green before anything
#     touches it, so we have a ground truth to protect;
#   * `ruff format` changes how it reads and NOT what it does — the same
#     suite is still green on a formatted copy, and formatting a second
#     time changes nothing (idempotence);
#   * `ruff check` finds the eight rule codes this lab is built around,
#     asserted by CODE rather than by the wording of the message;
#   * the safe autofix refuses to touch the real bug (B006) and the unsafe
#     autofix does fix it — the distinction the lesson turns on;
#   * the cleaned module is clean under the project's own configuration,
#     passes the same behaviour tests, and no longer shares a basket;
#   * `--check` mode fails on the messy file and passes on the clean one,
#     which is the shape both tools take in continuous integration;
#   * a `# noqa` comment with a specific code suppresses exactly that code.
#
# No network at test time, non-interactive, deterministic. Exits 0 only if
# every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

# The rule families this lab teaches. Kept in one variable so the harness
# and the exercises can never drift apart.
SELECT="E,F,I,B,SIM,UP"

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

# Resolve a tool: an explicit override, then this lab's .venv, then whatever
# is on PATH. Fails loudly with instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

ruff_bin="$(resolve_tool ruff "${RUFF:-}")" || {
  echo "FAIL: ruff not found." >&2
  install_hint
  echo "  Or point this suite at an existing ruff: RUFF=/path/to/ruff bash tests/run_tests.sh" >&2
  exit 1
}

# run_pytest <dir> — runs the suite in <dir>, quiet, leaving no cache behind.
run_pytest() {
  (cd "$1" && "${pytest_bin}" -q -p no:cacheprovider >/dev/null 2>&1)
}

# scratch_copy <src_dir> — copies a directory's .py files to a fresh temp
# directory and echoes its path. The caller removes it.
scratch_copy() {
  local src="$1" dest
  dest="$(mktemp -d "${TMPDIR:-/tmp}/ruff-lab.XXXXXX")"
  cp "${src}"/*.py "${dest}/"
  echo "${dest}"
}

echo "Day 076 — Linting and Formatting with Ruff"
echo "  ruff:   $("${ruff_bin}" --version)"
echo "  pytest: $("${pytest_bin}" --version 2>&1 | head -1)"
echo

# --------------------------------------------------------------------------
echo "Ground truth: the messy module works"
# --------------------------------------------------------------------------

if run_pytest "${lab_dir}/examples/messy"; then
  check "the messy module's pytest suite passes before any tool touches it" "yes"
else
  check "the messy module's pytest suite passes before any tool touches it" "no"
fi

messy_count="$(cd "${lab_dir}/examples/messy" && "${pytest_bin}" -q -p no:cacheprovider 2>/dev/null | grep -cE '^[.]+ +\[100%\]$')"
if [ "${messy_count}" = "1" ]; then
  check "the messy suite reports a single all-passing line" "yes"
else
  check "the messy suite reports a single all-passing line" "no"
fi

# The bug the linter is going to find, demonstrated at runtime.
if (cd "${lab_dir}/examples/messy" && python3 -c "
import receipts
first = receipts.add_item('apple', 120)
second = receipts.add_item('pear', 95)
raise SystemExit(0 if first is second else 1)
" >/dev/null 2>&1); then
  check "the messy add_item really does share one basket between calls (the B006 bug)" "yes"
else
  check "the messy add_item really does share one basket between calls (the B006 bug)" "no"
fi

# --------------------------------------------------------------------------
echo
echo "The linter: what it finds, by rule code"
# --------------------------------------------------------------------------

lint_report="$(cd "${lab_dir}/examples/messy" && "${ruff_bin}" check --isolated --select "${SELECT}" --output-format concise receipts.py 2>&1)"
lint_status=$?

if [ "${lint_status}" -ne 0 ]; then
  check "ruff check exits non-zero on the messy module" "yes"
else
  check "ruff check exits non-zero on the messy module" "no"
fi

for code in I001 F401 B006 E711 F841 SIM108 UP031 E501; do
  if printf '%s\n' "${lint_report}" | grep -q " ${code} "; then
    check "ruff check reports ${code} on the messy module" "yes"
  else
    check "ruff check reports ${code} on the messy module" "no"
  fi
done

if printf '%s\n' "${lint_report}" | grep -q "^Found 10 errors\.$"; then
  check "ruff check reports exactly 10 findings under --select ${SELECT}" "yes"
else
  check "ruff check reports exactly 10 findings under --select ${SELECT}" "no"
fi

# The default selection is deliberately smaller than the one above.
default_report="$(cd "${lab_dir}/examples/messy" && "${ruff_bin}" check --isolated --output-format concise receipts.py 2>&1)"
if printf '%s\n' "${default_report}" | grep -q "^Found 5 errors\.$" \
  && ! printf '%s\n' "${default_report}" | grep -q " B006 "; then
  check "ruff's default rule set is smaller and misses B006 until you select it" "yes"
else
  check "ruff's default rule set is smaller and misses B006 until you select it" "no"
fi

# --------------------------------------------------------------------------
echo
echo "The formatter: appearance only, and idempotent"
# --------------------------------------------------------------------------

if (cd "${lab_dir}/examples/messy" && "${ruff_bin}" format --isolated --check receipts.py >/dev/null 2>&1); then
  check "ruff format --check FAILS on the messy module (the CI form)" "no"
else
  check "ruff format --check FAILS on the messy module (the CI form)" "yes"
fi

scratch="$(scratch_copy "${lab_dir}/examples/messy")"
"${ruff_bin}" format --isolated "${scratch}/receipts.py" >/dev/null 2>&1
if run_pytest "${scratch}"; then
  check "the behaviour suite is STILL green after ruff format rewrote the module" "yes"
else
  check "the behaviour suite is STILL green after ruff format rewrote the module" "no"
fi

second_pass="$("${ruff_bin}" format --isolated "${scratch}/receipts.py" 2>&1)"
if printf '%s\n' "${second_pass}" | grep -q "1 file left unchanged"; then
  check "formatting is idempotent — the second run changes nothing" "yes"
else
  check "formatting is idempotent — the second run changes nothing" "no"
fi

if "${ruff_bin}" format --isolated --check "${scratch}/receipts.py" >/dev/null 2>&1; then
  check "ruff format --check now PASSES on the formatted copy" "yes"
else
  check "ruff format --check now PASSES on the formatted copy" "no"
fi
rm -rf "${scratch}"

# A formatter is not a linter: formatting alone leaves every real finding.
scratch="$(scratch_copy "${lab_dir}/examples/messy")"
"${ruff_bin}" format --isolated "${scratch}/receipts.py" >/dev/null 2>&1
after_format="$("${ruff_bin}" check --isolated --select "${SELECT}" --output-format concise "${scratch}/receipts.py" 2>&1)"
if printf '%s\n' "${after_format}" | grep -q " B006 " \
  && printf '%s\n' "${after_format}" | grep -q " F401 "; then
  check "formatting fixes no lint findings — B006 and F401 both survive it" "yes"
else
  check "formatting fixes no lint findings — B006 and F401 both survive it" "no"
fi
rm -rf "${scratch}"

# --------------------------------------------------------------------------
echo
echo "Autofix: safe, unsafe, and the line between them"
# --------------------------------------------------------------------------

scratch="$(scratch_copy "${lab_dir}/examples/messy")"
"${ruff_bin}" check --isolated --select "${SELECT}" --fix "${scratch}/receipts.py" >/dev/null 2>&1
safe_left="$("${ruff_bin}" check --isolated --select "${SELECT}" --output-format concise "${scratch}/receipts.py" 2>&1)"

if ! printf '%s\n' "${safe_left}" | grep -q " F401 "; then
  check "the SAFE autofix removes the unused imports (F401)" "yes"
else
  check "the SAFE autofix removes the unused imports (F401)" "no"
fi

if printf '%s\n' "${safe_left}" | grep -q " B006 "; then
  check "the SAFE autofix refuses to touch B006 — behaviour is a human decision" "yes"
else
  check "the SAFE autofix refuses to touch B006 — behaviour is a human decision" "no"
fi

if run_pytest "${scratch}"; then
  check "the behaviour suite is still green after the safe autofix" "yes"
else
  check "the behaviour suite is still green after the safe autofix" "no"
fi

"${ruff_bin}" check --isolated --select "${SELECT}" --fix --unsafe-fixes "${scratch}/receipts.py" >/dev/null 2>&1
unsafe_left="$("${ruff_bin}" check --isolated --select "${SELECT}" --output-format concise "${scratch}/receipts.py" 2>&1)"
if ! printf '%s\n' "${unsafe_left}" | grep -q " B006 "; then
  check "the UNSAFE autofix does rewrite the mutable default" "yes"
else
  check "the UNSAFE autofix does rewrite the mutable default" "no"
fi

# ...and that rewrite genuinely CHANGES BEHAVIOUR, which is why it is
# opt-in: the test that recorded the bug now fails.
if run_pytest "${scratch}"; then
  check "the unsafe fix changes behaviour, so the test that recorded the bug now fails" "no"
else
  check "the unsafe fix changes behaviour, so the test that recorded the bug now fails" "yes"
fi
rm -rf "${scratch}"

# --------------------------------------------------------------------------
echo
echo "Suppression: noqa with a code, not a bare noqa"
# --------------------------------------------------------------------------

scratch="$(mktemp -d "${TMPDIR:-/tmp}/ruff-lab.XXXXXX")"
{
  printf 'import json  # noqa: F401\n'
  printf 'import re\n\n\n'
  printf 'def first_digit(value):\n'
  printf '    if value == None:\n'
  printf '        return None\n'
  printf '    return re.search("[0-9]", value)\n'
} >"${scratch}/suppressed.py"
noqa_report="$("${ruff_bin}" check --isolated --select F,E --output-format concise "${scratch}/suppressed.py" 2>&1)"
if ! printf '%s\n' "${noqa_report}" | grep -q " F401 "; then
  check "# noqa: F401 suppresses exactly that rule on that line" "yes"
else
  check "# noqa: F401 suppresses exactly that rule on that line" "no"
fi
if printf '%s\n' "${noqa_report}" | grep -q " E711 "; then
  check "# noqa: F401 suppresses nothing else — E711 elsewhere still fires" "yes"
else
  check "# noqa: F401 suppresses nothing else — E711 elsewhere still fires" "no"
fi
rm -rf "${scratch}"

# --------------------------------------------------------------------------
echo
echo "The cleaned module and its configuration"
# --------------------------------------------------------------------------

if (cd "${lab_dir}/examples/clean" && "${ruff_bin}" check . >/dev/null 2>&1); then
  check "ruff check exits 0 on examples/clean using its own pyproject.toml" "yes"
else
  check "ruff check exits 0 on examples/clean using its own pyproject.toml" "no"
fi

if (cd "${lab_dir}/examples/clean" && "${ruff_bin}" format --check . >/dev/null 2>&1); then
  check "ruff format --check exits 0 on examples/clean" "yes"
else
  check "ruff format --check exits 0 on examples/clean" "no"
fi

if run_pytest "${lab_dir}/examples/clean"; then
  check "the cleaned module passes the same behaviour suite" "yes"
else
  check "the cleaned module passes the same behaviour suite" "no"
fi

if (cd "${lab_dir}/examples/clean" && python3 -c "
import receipts
first = receipts.add_item('apple', 120)
second = receipts.add_item('pear', 95)
assert first is not second
assert first == [{'name': 'apple', 'price_cents': 120}]
assert second == [{'name': 'pear', 'price_cents': 95}]
" >/dev/null 2>&1); then
  check "the cleaned add_item gives every caller a fresh basket — the bug is gone" "yes"
else
  check "the cleaned add_item gives every caller a fresh basket — the bug is gone" "no"
fi

# The two modules must still agree on everything that is not the bug.
if (cd "${lab_dir}" && python3 -c "
import importlib.util, sys

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

messy = load('messy_receipts', 'examples/messy/receipts.py')
clean = load('clean_receipts', 'examples/clean/receipts.py')
lines = ['apple 120', 'nonsense', 'brown bread 240', 'pear 95']
for mod in (messy, clean):
    basket = mod.load_basket(lines)
    assert mod.subtotal_cents(basket) == 455, mod
    assert mod.tax_cents(basket) == 91, mod
    assert mod.total_cents(basket) == 546, mod
    assert mod.describe(basket, 'apple') == 'apple: found x1', mod
    assert mod.format_receipt(basket) == messy.format_receipt(basket), mod
" >/dev/null 2>&1); then
  check "messy and clean agree on every price, description and receipt line" "yes"
else
  check "messy and clean agree on every price, description and receipt line" "no"
fi

# The per-file ignore is doing real work: S101 fires on the tests without
# the configuration and is silent with it.
s101_isolated="$(cd "${lab_dir}/examples/clean" && "${ruff_bin}" check --isolated --select S --output-format concise test_receipts.py 2>&1)"
if printf '%s\n' "${s101_isolated}" | grep -q " S101 "; then
  check "S101 fires on the test file when the configuration is ignored" "yes"
else
  check "S101 fires on the test file when the configuration is ignored" "no"
fi

s101_configured="$(cd "${lab_dir}/examples/clean" && "${ruff_bin}" check --output-format concise test_receipts.py 2>&1)"
if ! printf '%s\n' "${s101_configured}" | grep -q " S101 "; then
  check "the per-file ignore silences S101 for test_*.py and nowhere else" "yes"
else
  check "the per-file ignore silences S101 for test_*.py and nowhere else" "no"
fi

if python3 -c "
import tomllib, pathlib
config = tomllib.loads(pathlib.Path('${lab_dir}/examples/clean/pyproject.toml').read_text())
lint = config['tool']['ruff']['lint']
assert config['tool']['ruff']['line-length'] == 88
assert {'E', 'F', 'I', 'B', 'SIM', 'UP'} <= set(lint['select'])
assert lint['ignore'] == ['E501']
assert lint['per-file-ignores']['test_*.py'] == ['S101']
" >/dev/null 2>&1; then
  check "the reference pyproject.toml parses and declares select, ignore and a per-file ignore" "yes"
else
  check "the reference pyproject.toml parses and declares select, ignore and a per-file ignore" "no"
fi

# --------------------------------------------------------------------------
echo
echo "Your starter files"
# --------------------------------------------------------------------------

if python3 -c "import ast, pathlib; ast.parse(pathlib.Path('${lab_dir}/starter/receipts.py').read_text())" >/dev/null 2>&1; then
  check "starter/receipts.py is valid Python" "yes"
else
  check "starter/receipts.py is valid Python" "no"
fi

if run_pytest "${lab_dir}/starter"; then
  check "starter/ still passes its own behaviour suite (whatever stage you are at)" "yes"
else
  check "starter/ still passes its own behaviour suite — if this fails, finish exercise 6" "no"
fi

if (cd "${lab_dir}/starter" && python3 -c "
import receipts
for name in ('add_item', 'parse_line', 'load_basket', 'subtotal_cents',
             'tax_cents', 'total_cents', 'describe', 'format_receipt'):
    assert hasattr(receipts, name), name
" >/dev/null 2>&1); then
  check "starter/receipts.py still defines all eight public functions" "yes"
else
  check "starter/receipts.py still defines all eight public functions" "no"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ] || exit 1
exit 0
