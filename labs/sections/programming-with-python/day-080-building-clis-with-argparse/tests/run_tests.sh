#!/usr/bin/env bash
# Tests for the Day 080 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# A command-line interface is a contract with a SHELL, so most of this suite
# launches the real program as a subprocess and inspects what the shell can
# see: the exit code, standard output, and standard error — separately.
#
# Three checks are the ones worth reading, because they are the ones that
# cannot be faked:
#
#   * "a bad date writes to stderr, writes NOTHING to stdout, and exits 2"
#     captures the two streams into two different files. A program that
#     printed its error with print() would pass a combined-output check and
#     fail this one, which is exactly the point;
#   * "--dry-run leaves the store byte-identical" hashes the file before and
#     after. It is paired with a control that runs the same command WITHOUT
#     --dry-run and demands the hash changes, so the check cannot pass by the
#     program simply never writing anything;
#   * "parse_args works in-process with an explicit argv list" runs the pytest
#     suite in tests/, which never starts a process at all.
#
# No network, no clock beyond an explicit --on, deterministic. Exits 0 only if
# every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

# Resolve tools: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with install instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

python_bin="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

work="$(mktemp -d "${TMPDIR:-/tmp}/notes-cli.XXXXXX")"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

hash_of() { "${python_bin}" -c "
import hashlib, sys, pathlib
print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())
" "$1"; }

echo "Day 080 — A Tool You Would Actually Install"
echo

# ==========================================================================
# The behavioural battery. Everything below runs against whichever copy of
# notes.py it is handed, so the reference and your finished starter are held
# to exactly the same standard.
# ==========================================================================

run_battery() {
  local label="$1" program="$2"
  local dir="${work}/${label}"
  local store="${dir}/store.json"
  local out="${dir}/out.txt" err="${dir}/err.txt"
  mkdir -p "${dir}"

  local notes="${python_bin} ${program}"

  # ------------------------------------------------------------------------
  # 1. Help output — the documentation most users will ever read
  # ------------------------------------------------------------------------

  ${notes} --help >"${out}" 2>"${err}"
  local rc=$?
  [ "${rc}" -eq 0 ] &&
    check "${label}: --help exits 0" "yes" ||
    check "${label}: --help exits 0 (got ${rc})" "no"

  [ -s "${out}" ] &&
    check "${label}: --help writes to standard output" "yes" ||
    check "${label}: --help writes to standard output" "no"

  [ ! -s "${err}" ] &&
    check "${label}: --help writes nothing to standard error" "yes" ||
    check "${label}: --help writes nothing to standard error" "no"

  local subcommand
  for subcommand in add list search export remove; do
    grep -q "^ *${subcommand} " "${out}" &&
      check "${label}: --help names the '${subcommand}' subcommand" "yes" ||
      check "${label}: --help names the '${subcommand}' subcommand" "no"
  done

  grep -q "usage: notes" "${out}" &&
    check "${label}: usage line says 'notes', not the file name (prog=)" "yes" ||
    check "${label}: usage line says 'notes', not the file name (prog=)" "no"

  grep -q "Exit codes" "${out}" &&
    check "${label}: the epilog survives with its line breaks intact" "yes" ||
    check "${label}: the epilog survives with its line breaks intact" "no"

  ${notes} add --help >"${out}" 2>&1
  grep -q "YYYY-MM-DD" "${out}" &&
    check "${label}: 'add --help' shows the --on metavar" "yes" ||
    check "${label}: 'add --help' shows the --on metavar" "no"
  grep -q "storage options" "${out}" &&
    check "${label}: 'add --help' groups the storage options" "yes" ||
    check "${label}: 'add --help' groups the storage options" "no"

  ${notes} --version >"${out}" 2>&1
  rc=$?
  { [ "${rc}" -eq 0 ] && grep -q "^notes 1\.0\.0$" "${out}"; } &&
    check "${label}: --version prints 'notes 1.0.0' and exits 0" "yes" ||
    check "${label}: --version prints 'notes 1.0.0' and exits 0 (got ${rc})" "no"

  # ------------------------------------------------------------------------
  # 2. Usage errors — argparse's exit code 2, and nothing on stdout
  # ------------------------------------------------------------------------

  ${notes} >"${out}" 2>"${err}"
  rc=$?
  [ "${rc}" -eq 2 ] &&
    check "${label}: no subcommand at all exits 2" "yes" ||
    check "${label}: no subcommand at all exits 2 (got ${rc})" "no"

  ${notes} frobnicate >"${out}" 2>"${err}"
  rc=$?
  [ "${rc}" -ne 0 ] &&
    check "${label}: an unknown subcommand exits non-zero (${rc})" "yes" ||
    check "${label}: an unknown subcommand exits non-zero" "no"
  grep -q "invalid choice" "${err}" &&
    check "${label}: an unknown subcommand is explained on standard error" "yes" ||
    check "${label}: an unknown subcommand is explained on standard error" "no"

  ${notes} add "x" --tagg typo --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 2 ] && [ ! -s "${out}" ]; } &&
    check "${label}: a mistyped option is refused, not ignored" "yes" ||
    check "${label}: a mistyped option is refused, not ignored (got ${rc})" "no"

  ${notes} list -v -q --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 2 ] && grep -q "not allowed with argument" "${err}"; } &&
    check "${label}: -v and -q together exit 2, naming both options" "yes" ||
    check "${label}: -v and -q together exit 2, naming both options" "no"

  ${notes} list --format yaml --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 2 ] && grep -q "invalid choice" "${err}"; } &&
    check "${label}: a value outside choices= exits 2" "yes" ||
    check "${label}: a value outside choices= exits 2" "no"

  ${notes} list -n 0 --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 2 ] && grep -q "at least 1" "${err}"; } &&
    check "${label}: the custom positive_int type rejects 0" "yes" ||
    check "${label}: the custom positive_int type rejects 0" "no"

  # ---- THE STREAM-SEPARATION CHECK ---------------------------------------
  # Two separate files, two separate assertions. A program that printed its
  # error message on standard output would pass a 2>&1 check and fail here.
  ${notes} add "x" --on 2026-13-01 --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  [ "${rc}" -ne 0 ] &&
    check "${label}: a bad date exits non-zero (${rc})" "yes" ||
    check "${label}: a bad date exits non-zero" "no"
  [ "${rc}" -eq 2 ] &&
    check "${label}: a bad date exits exactly 2 — argparse's usage code" "yes" ||
    check "${label}: a bad date exits exactly 2 (got ${rc})" "no"
  [ ! -s "${out}" ] &&
    check "${label}: a bad date writes NOTHING to standard output" "yes" ||
    check "${label}: a bad date writes NOTHING to standard output" "no"
  [ -s "${err}" ] &&
    check "${label}: a bad date writes a message to standard error" "yes" ||
    check "${label}: a bad date writes a message to standard error" "no"
  grep -q "2026-13-01" "${err}" &&
    check "${label}: the message quotes the value that was rejected" "yes" ||
    check "${label}: the message quotes the value that was rejected" "no"
  grep -q "YYYY-MM-DD" "${err}" &&
    check "${label}: the message says what a date should look like" "yes" ||
    check "${label}: the message says what a date should look like" "no"
  [ ! -e "${store}" ] &&
    check "${label}: a refused command created no store file" "yes" ||
    check "${label}: a refused command created no store file" "no"

  ${notes} add "x" --tag "two words" --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 2 ] && grep -q "no spaces or commas" "${err}"; } &&
    check "${label}: the custom tag type rejects a tag with a space" "yes" ||
    check "${label}: the custom tag type rejects a tag with a space" "no"

  # ------------------------------------------------------------------------
  # 3. The happy path
  # ------------------------------------------------------------------------

  ${notes} add "ring the dentist" --tag health --on 2026-03-01 --store "${store}" \
    >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 0 ] && grep -q "^added note 1$" "${out}" && [ ! -s "${err}" ]; } &&
    check "${label}: a successful add exits 0, reports on stdout, is silent on stderr" "yes" ||
    check "${label}: a successful add exits 0, reports on stdout, is silent on stderr (got ${rc})" "no"

  ${notes} add "argparse turns a script into a tool" -t python -t writing \
    --on 2026-03-02 --store "${store}" >/dev/null 2>&1
  check "${label}: --tag repeats (action='append')" \
    "$(${notes} list --format json --store "${store}" 2>/dev/null |
       grep -q '"python"' && echo yes || echo no)"

  # ---- stdin, so the tool composes in a pipeline --------------------------
  echo "from a pipe" | ${notes} add - --tag inbox --on 2026-03-03 --store "${store}" \
    >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 0 ] && grep -q "^added note 3$" "${out}"; } &&
    check "${label}: 'add -' reads the note from a pipe" "yes" ||
    check "${label}: 'add -' reads the note from a pipe (got ${rc})" "no"
  ${notes} search "from a pipe" --store "${store}" >"${out}" 2>&1
  grep -q "from a pipe" "${out}" &&
    check "${label}: the piped text was really stored" "yes" ||
    check "${label}: the piped text was really stored" "no"

  # ---- a double dash ends option parsing ---------------------------------
  ${notes} add --on 2026-03-04 --store "${store}" -- "--not-a-flag" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 0 ] && grep -q "^added note 4$" "${out}"; } &&
    check "${label}: '--' lets a note start with two dashes" "yes" ||
    check "${label}: '--' lets a note start with two dashes (got ${rc})" "no"

  # ---- output formats -----------------------------------------------------
  ${notes} list --format json --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 0 ] && "${python_bin}" -c "
import json, sys
notes = json.load(open(sys.argv[1]))
assert isinstance(notes, list) and len(notes) == 4, notes
assert notes[0]['text'] == 'ring the dentist', notes[0]
" "${out}"; } &&
    check "${label}: 'list --format json' emits parseable JSON on stdout" "yes" ||
    check "${label}: 'list --format json' emits parseable JSON on stdout" "no"

  ${notes} list --store "${store}" >"${out}" 2>&1
  grep -q "^ID  DATE" "${out}" &&
    check "${label}: 'list' defaults to the table format" "yes" ||
    check "${label}: 'list' defaults to the table format" "no"

  ${notes} list -n 1 --store "${store}" >"${out}" 2>&1
  [ "$(grep -c '2026-03' "${out}")" -eq 1 ] &&
    check "${label}: '-n 1' limits the listing to one note" "yes" ||
    check "${label}: '-n 1' limits the listing to one note" "no"

  ${notes} export --format csv --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 0 ] && head -1 "${out}" | grep -q "^id,date,tags,text$" &&
    [ "$(wc -l <"${out}")" -eq 5 ]; } &&
    check "${label}: 'export --format csv' writes a header and four rows" "yes" ||
    check "${label}: 'export --format csv' writes a header and four rows" "no"

  # ---- diagnostics on stderr keep the RESULT on stdout clean --------------
  ${notes} list --format json -v --store "${store}" >"${out}" 2>"${err}"
  { "${python_bin}" -c "import json,sys; json.load(open(sys.argv[1]))" "${out}" &&
    grep -q "4 note(s) from" "${err}"; } &&
    check "${label}: -v chatter goes to stderr, leaving stdout valid JSON" "yes" ||
    check "${label}: -v chatter goes to stderr, leaving stdout valid JSON" "no"

  ${notes} add "quiet one" --on 2026-03-05 -q --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 0 ] && [ ! -s "${out}" ] && [ ! -s "${err}" ]; } &&
    check "${label}: -q succeeds in silence on both streams" "yes" ||
    check "${label}: -q succeeds in silence on both streams" "no"

  # ---- search follows grep's exit-code convention -------------------------
  ${notes} search dentist --store "${store}" >/dev/null 2>&1
  rc=$?
  [ "${rc}" -eq 0 ] &&
    check "${label}: search exits 0 when something matched" "yes" ||
    check "${label}: search exits 0 when something matched (got ${rc})" "no"
  ${notes} search kangaroo --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 1 ] && [ ! -s "${out}" ]; } &&
    check "${label}: search exits 1 when nothing matched, printing nothing" "yes" ||
    check "${label}: search exits 1 when nothing matched (got ${rc})" "no"
  ${notes} search DENTIST -i --store "${store}" >/dev/null 2>&1
  [ $? -eq 0 ] &&
    check "${label}: '-i' matches regardless of case" "yes" ||
    check "${label}: '-i' matches regardless of case" "no"

  # ------------------------------------------------------------------------
  # 4. --dry-run — the promise, and the control that proves it means anything
  # ------------------------------------------------------------------------

  local before after
  before="$(hash_of "${store}")"
  ${notes} remove 2 --dry-run --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  after="$(hash_of "${store}")"

  [ "${rc}" -eq 0 ] &&
    check "${label}: 'remove --dry-run' exits 0" "yes" ||
    check "${label}: 'remove --dry-run' exits 0 (got ${rc})" "no"
  [ "${before}" = "${after}" ] &&
    check "${label}: 'remove --dry-run' leaves the store BYTE-IDENTICAL" "yes" ||
    check "${label}: 'remove --dry-run' leaves the store BYTE-IDENTICAL" "no"
  grep -q "^would remove note 2$" "${out}" &&
    check "${label}: the dry run puts the ids on stdout, where they can be piped" "yes" ||
    check "${label}: the dry run puts the ids on stdout, where they can be piped" "no"
  grep -q "was not touched" "${err}" &&
    check "${label}: the dry run puts its summary on stderr, where it is a diagnostic" "yes" ||
    check "${label}: the dry run puts its summary on stderr, where it is a diagnostic" "no"

  # A dry run still VALIDATES: an impossible deletion is refused, not promised.
  ${notes} remove 999 --dry-run --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 1 ] && [ ! -s "${out}" ] && grep -q "no note with id 999" "${err}"; } &&
    check "${label}: a dry run still refuses a note that does not exist" "yes" ||
    check "${label}: a dry run still refuses a note that does not exist (got ${rc})" "no"

  # THE CONTROL: without --dry-run the same command must change the file.
  # Without this, "the bytes did not change" could be satisfied by a program
  # that never writes at all.
  before="$(hash_of "${store}")"
  ${notes} remove 2 --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  after="$(hash_of "${store}")"
  { [ "${rc}" -eq 0 ] && [ "${before}" != "${after}" ] &&
    grep -q "^removed note 2$" "${out}"; } &&
    check "${label}: control — a real remove DOES change the store" "yes" ||
    check "${label}: control — a real remove DOES change the store" "no"

  ${notes} remove 2 --store "${store}" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 1 ] && [ ! -s "${out}" ] && grep -q "no note with id 2" "${err}"; } &&
    check "${label}: removing it twice is a refusal on stderr with exit 1" "yes" ||
    check "${label}: removing it twice is a refusal on stderr with exit 1 (got ${rc})" "no"

  ${notes} remove 1 3 --store "${store}" >"${out}" 2>&1
  [ "$(grep -c '^removed note' "${out}")" -eq 2 ] &&
    check "${label}: nargs='+' removes several notes in one command" "yes" ||
    check "${label}: nargs='+' removes several notes in one command" "no"

  # ------------------------------------------------------------------------
  # 5. Configuration precedence, and composing in a pipeline
  # ------------------------------------------------------------------------

  local env_store="${dir}/from-env.json"
  ( cd "${dir}" && NOTES_STORE="${env_store}" ${notes} add "via the environment" \
      --on 2026-03-06 >/dev/null 2>&1 )
  [ -f "${env_store}" ] &&
    check "${label}: \$NOTES_STORE is used when --store is absent" "yes" ||
    check "${label}: \$NOTES_STORE is used when --store is absent" "no"

  local flag_store="${dir}/from-flag.json"
  ( cd "${dir}" && NOTES_STORE="${env_store}" ${notes} add "via the flag" \
      --on 2026-03-06 --store "${flag_store}" >/dev/null 2>&1 )
  { [ -f "${flag_store}" ] &&
    [ "$(${notes} list --format json --store "${env_store}" 2>/dev/null |
         grep -c 'via the flag')" -eq 0 ]; } &&
    check "${label}: --store beats \$NOTES_STORE (flag wins)" "yes" ||
    check "${label}: --store beats \$NOTES_STORE (flag wins)" "no"

  # Note the store for this battery is store.json, so ./notes.json appearing
  # here can only have come from the built-in default.
  ( cd "${dir}" && ${notes} add "the built-in default" --on 2026-03-06 >/dev/null 2>&1 )
  [ -f "${dir}/notes.json" ] &&
    check "${label}: with neither, the built-in ./notes.json default applies" "yes" ||
    check "${label}: with neither, the built-in ./notes.json default applies" "no"

  # A tool that writes its result to stdout can be piped into another tool.
  local piped
  piped="$(${notes} export --format json --store "${store}" 2>/dev/null |
           "${python_bin}" -c "import json,sys; print(len(json.load(sys.stdin)))")"
  [ "${piped}" = "2" ] &&
    check "${label}: 'export | python3' composes — stdout is machine-readable" "yes" ||
    check "${label}: 'export | python3' composes (got '${piped}')" "no"

  # Closing the pipe early must not produce a BrokenPipeError traceback.
  ${notes} export --format csv --store "${store}" 2>"${err}" | head -1 >/dev/null
  [ ! -s "${err}" ] &&
    check "${label}: closing the pipe early is not an error" "yes" ||
    check "${label}: closing the pipe early is not an error" "no"

  # ------------------------------------------------------------------------
  # 6. Refusals that are not usage errors exit 1, not 2
  # ------------------------------------------------------------------------

  echo "{ this is not json" >"${dir}/broken.json"
  ${notes} list --store "${dir}/broken.json" >"${out}" 2>"${err}"
  rc=$?
  { [ "${rc}" -eq 1 ] && [ ! -s "${out}" ] && grep -q "not valid JSON" "${err}"; } &&
    check "${label}: a corrupt store is exit 1 on stderr, not a traceback" "yes" ||
    check "${label}: a corrupt store is exit 1 on stderr, not a traceback (got ${rc})" "no"
  grep -q "Traceback" "${err}" &&
    check "${label}: no Python traceback ever reaches the user" "no" ||
    check "${label}: no Python traceback ever reaches the user" "yes"
}

# --------------------------------------------------------------------------
echo "1. The reference tool (examples/notes.py)"
# --------------------------------------------------------------------------
run_battery "reference" "${lab_dir}/examples/notes.py"

# --------------------------------------------------------------------------
echo
echo "2. The hand-rolled parser, and why it is not enough"
# --------------------------------------------------------------------------

by_hand_out="${work}/by_hand.txt"
"${python_bin}" "${lab_dir}/examples/by_hand.py" >"${by_hand_out}" 2>&1
by_hand_rc=$?
[ "${by_hand_rc}" -eq 0 ] &&
  check "examples/by_hand.py runs and exits 0" "yes" ||
  check "examples/by_hand.py runs and exits 0 (got ${by_hand_rc})" "no"
grep -q "8 ordinary command lines, 4 of them handled wrongly." "${by_hand_out}" &&
  check "the hand-rolled parser gets 4 of 8 ordinary command lines wrong" "yes" ||
  check "the hand-rolled parser gets 4 of 8 ordinary command lines wrong" "no"
grep -q "the tag is silently lost" "${by_hand_out}" &&
  check "it loses the value of --tag=shopping without saying so" "yes" ||
  check "it loses the value of --tag=shopping without saying so" "no"
grep -q "IndexError" "${by_hand_out}" &&
  check "a missing option value gives an IndexError, not a usage message" "yes" ||
  check "a missing option value gives an IndexError, not a usage message" "no"

# argparse handles every one of those correctly. Two spot-checks:
ref="${lab_dir}/examples/notes.py"
spot_store="${work}/spot.json"
"${python_bin}" "${ref}" add "buy milk" --tag=shopping --on 2026-03-01 \
  --store "${spot_store}" >/dev/null 2>&1
"${python_bin}" "${ref}" list --format json --store "${spot_store}" 2>/dev/null |
  grep -q '"shopping"' &&
  check "argparse handles --tag=shopping, which the hand-rolled parser dropped" "yes" ||
  check "argparse handles --tag=shopping, which the hand-rolled parser dropped" "no"
"${python_bin}" "${ref}" add "x" --tag --store "${spot_store}" >/dev/null 2>"${work}/e.txt"
spot_rc=$?
{ [ "${spot_rc}" -eq 2 ] && grep -q "expected one argument" "${work}/e.txt"; } &&
  check "argparse turns a missing option value into a usage message and exit 2" "yes" ||
  check "argparse turns a missing option value into a usage message and exit 2" "no"

# --------------------------------------------------------------------------
echo
echo "3. In-process: parse_args with an explicit argv list"
# --------------------------------------------------------------------------

pytest_out="$(cd "${lab_dir}" && NOTES_DIR=examples "${pytest_bin}" tests -q 2>&1)"
pytest_rc=$?
[ "${pytest_rc}" -eq 0 ] &&
  check "the in-process pytest suite passes against examples/" "yes" ||
  check "the in-process pytest suite passes against examples/ (exit ${pytest_rc})" "no"
if [ "${pytest_rc}" -ne 0 ]; then printf '%s\n' "${pytest_out}" | tail -25; fi
printf '%s' "${pytest_out}" | grep -qE '[0-9]+ passed' &&
  check "it reports passing tests ( $(printf '%s' "${pytest_out}" | tail -1) )" "yes" ||
  check "it reports passing tests" "no"

# The in-process suite must be testing something. Break the parser's prog name
# in a COPY and demand that the subprocess battery would notice.
sandbox="${work}/sandbox"
mkdir -p "${sandbox}"
cp "${ref}" "${sandbox}/notes.py"
sed -i.bak 's/prog="notes"/prog="notez"/' "${sandbox}/notes.py"
rm -f "${sandbox}/notes.py.bak"
"${python_bin}" "${sandbox}/notes.py" --help 2>&1 | grep -q "usage: notes " &&
  check "a broken prog= would be caught (it was not — the check is vacuous)" "no" ||
  check "a one-line break to prog= changes the help output, so the check bites" "yes"

# --------------------------------------------------------------------------
echo
echo "4. The starter"
# --------------------------------------------------------------------------

starter="${lab_dir}/starter/notes.py"

"${python_bin}" -c "
import ast, sys
source = open(sys.argv[1], encoding='utf-8').read()
tree = ast.parse(source)
names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
required = {
    'iso_date', 'positive_int', 'tag_name', 'common_options', 'build_parser',
    'parse_args', 'main', 'cmd_add', 'cmd_list', 'cmd_search', 'cmd_export',
    'cmd_remove',
}
missing = required - names
assert not missing, f'starter is missing: {sorted(missing)}'
" "${starter}"
[ $? -eq 0 ] &&
  check "starter/notes.py is valid Python and defines every required function" "yes" ||
  check "starter/notes.py is valid Python and defines every required function" "no"

for n in 1 2 3 4 5 6 7 8; do
  grep -q "EXERCISE ${n}" "${starter}" &&
    check "starter/notes.py carries EXERCISE ${n}" "yes" ||
    check "starter/notes.py carries EXERCISE ${n}" "no"
done

grep -q "argparse" "${starter}" &&
  check "starter/notes.py imports argparse" "yes" ||
  check "starter/notes.py imports argparse" "no"

remaining="$(grep -c 'raise NotImplementedError' "${starter}" || true)"
if [ "${remaining}" -gt 0 ]; then
  echo "  ..  ${remaining} exercise(s) still unfinished — the behavioural battery"
  echo "      will run against starter/notes.py once they are done."
else
  echo
  echo "5. Your finished starter, held to the same standard"
  run_battery "starter" "${starter}"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
