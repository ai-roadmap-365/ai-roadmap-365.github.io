#!/usr/bin/env bash
# Tests for the Day 065 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks exercise real behaviour, not file existence: the messy CSV
# really does carry a byte-order mark; naive comma-splitting really does
# mangle it; csv.DictReader really does recover the quoted newline, the
# doubled quotes, and the ragged row; the JSON / JSON Lines / CSV round
# trips really are lossless; and the from-scratch quoting state machine
# really does agree with the standard library on every row.
#
# The reference in examples/ is always tested strictly. The learner's
# starter/ is tested structurally while exercises are unfinished, and to
# the same strict standard once they are complete.
# No network, non-interactive. Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d -t day065-tests.XXXXXX)"
trap 'rm -rf "${tmp_dir}"' EXIT

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

# check_py <label> <module_dir> <python-body>
# Runs an assertion body with module_dir on the import path. A clean exit
# (every assert holds) is a pass.
check_py() {
  local label="$1" module_dir="$2" body="$3"
  if PYTHONPATH="${module_dir}" TMP_DIR="${tmp_dir}" LAB="${lab_dir}" python3 -c "${body}" 2>/dev/null; then
    check "${label}" "yes"
  else
    check "${label}" "no"
  fi
}

# --- the input data itself -------------------------------------------------

echo "Testing the messy input file ..."
check_py "messy_orders.csv really starts with a byte-order mark" "${lab_dir}" \
"import os
raw = open(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'rb').read()
assert raw[:3] == b'\xef\xbb\xbf', raw[:3]"

check_py "messy_orders.csv really contains a newline inside a quoted field" "${lab_dir}" \
"import os
text = open(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), encoding='utf-8-sig').read()
assert 'Leave at door.\nRing the bell twice.' in text
assert len(text.splitlines()) == 7  # 6 records spread over 7 physical lines"

check_py "config.json is valid JSON with the five expected columns" "${lab_dir}" \
"import json, os
cfg = json.load(open(os.path.join(os.environ['LAB'], 'data', 'config.json'), encoding='utf-8'))
assert cfg['columns'] == ['order_id', 'customer', 'items', 'notes', 'total']
assert cfg['encoding'] == 'utf-8-sig'"

# --- the pipeline ----------------------------------------------------------

run_wrangle_checks() {
  local module_dir="$1"
  echo "Testing the wrangling pipeline in ${module_dir} ..."

  check_py "naive splitting breaks three physical lines" "${module_dir}" \
"import os, wrangle
text = open(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), encoding='utf-8-sig').read()
broken = wrangle.naive_report(text, 5)
assert [n for n, _ in broken] == [2, 4, 7], broken
assert dict(broken)[2] == 6 and dict(broken)[4] == 2 and dict(broken)[7] == 3"

  check_py "naive splitting also corrupts a line whose field count looks right" "${module_dir}" \
"import os, wrangle
text = open(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), encoding='utf-8-sig').read()
row = wrangle.naive_split_rows(text)[4]
assert len(row) == 5
assert row[1] == '\"Alan \"\"Turing\"\" Jr.\"'  # quotes never removed, escape never resolved"

  check_py "DictReader returns five records and strips the byte-order mark" "${module_dir}" \
"import os, wrangle
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
assert len(rows) == 5, len(rows)
assert list(rows[0])[0] == 'order_id', list(rows[0])[0]"

  check_py "the quoted newline, the embedded comma and the doubled quotes survive" "${module_dir}" \
"import os, wrangle
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
assert rows[0]['items'] == 'widget, large'
assert rows[1]['notes'] == 'Leave at door.\nRing the bell twice.'
assert rows[2]['customer'] == 'Alan \"Turing\" Jr.'"

  check_py "the ragged row comes back with None for its missing fields" "${module_dir}" \
"import os, wrangle
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
assert rows[4]['order_id'] == '1005'
assert rows[4]['notes'] is None and rows[4]['total'] is None"

  check_py "cleaning fills defaults and turns total into a real float" "${module_dir}" \
"import json, os, wrangle
cfg = json.load(open(os.path.join(os.environ['LAB'], 'data', 'config.json'), encoding='utf-8'))
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
recs = wrangle.clean_rows(rows, cfg)
assert all(v is not None for r in recs for v in r.values())
assert recs[4]['notes'] == '' and recs[4]['total'] == 0.0
assert isinstance(recs[0]['total'], float) and recs[0]['total'] == 49.5"

  check_py "the JSON round trip is lossless" "${module_dir}" \
"import json, os, wrangle
from pathlib import Path
cfg = json.load(open(os.path.join(os.environ['LAB'], 'data', 'config.json'), encoding='utf-8'))
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
recs = wrangle.clean_rows(rows, cfg)
p = Path(os.environ['TMP_DIR']) / 'rt.json'
wrangle.write_json(recs, p)
assert wrangle.read_json(p) == recs"

  check_py "the JSON Lines round trip is lossless and is one line per record" "${module_dir}" \
"import json, os, wrangle
from pathlib import Path
cfg = json.load(open(os.path.join(os.environ['LAB'], 'data', 'config.json'), encoding='utf-8'))
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
recs = wrangle.clean_rows(rows, cfg)
p = Path(os.environ['TMP_DIR']) / 'rt.jsonl'
wrangle.write_jsonl(recs, p)
assert wrangle.read_jsonl(p) == recs
lines = [ln for ln in p.read_text(encoding='utf-8').splitlines() if ln.strip()]
assert len(lines) == len(recs) == 5, len(lines)
assert all(json.loads(ln) for ln in lines)"

  check_py "the CSV round trip is lossless once types are restored" "${module_dir}" \
"import json, os, wrangle
from pathlib import Path
cfg = json.load(open(os.path.join(os.environ['LAB'], 'data', 'config.json'), encoding='utf-8'))
rows = wrangle.read_rows(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), 'utf-8-sig', ',')
recs = wrangle.clean_rows(rows, cfg)
p = Path(os.environ['TMP_DIR']) / 'rt.csv'
wrangle.write_csv(recs, p, cfg['columns'], ',')
assert wrangle.read_csv_typed(p, cfg['columns'], ',', cfg['numeric_columns']) == recs
assert '\"widget, large\"' in p.read_text(encoding='utf-8')  # DictWriter re-quotes for us"
}

run_parser_checks() {
  local module_dir="$1"
  echo "Testing the from-scratch quoting state machine in ${module_dir} ..."

  check_py "the from-scratch parser agrees with the csv module on the messy file" "${module_dir}" \
"import os, csv_field_parser as p
text = open(os.path.join(os.environ['LAB'], 'data', 'messy_orders.csv'), encoding='utf-8-sig').read()
mine, theirs, agree = p.compare(text)
assert agree, list(zip(mine, theirs))
assert len(mine) == 6"

  check_py "the from-scratch parser handles embedded commas, newlines and doubled quotes" "${module_dir}" \
"import csv_field_parser as p
assert p.parse_csv('a,\"b,c\",d\n') == [['a', 'b,c', 'd']]
assert p.parse_csv('a,\"line1\nline2\",d\n') == [['a', 'line1\nline2', 'd']]
assert p.parse_csv('a,\"say \"\"hi\"\"\",d\n') == [['a', 'say \"hi\"', 'd']]"

  check_py "the from-scratch parser handles empty fields, no trailing newline and CRLF" "${module_dir}" \
"import csv_field_parser as p
assert p.parse_csv('a,,c\n') == [['a', '', 'c']]
assert p.parse_csv('a,b,c') == [['a', 'b', 'c']]
assert p.parse_csv('a,b\r\nc,d\r\n') == [['a', 'b'], ['c', 'd']]
assert p.parse_csv('a,b,') == [['a', 'b', '']]"

  check_py "the from-scratch parser agrees with the csv module on a semicolon dialect" "${module_dir}" \
"import csv_field_parser as p
text = 'name;amount\nWien;1.234,50\n\"Berlin; Mitte\";2.000,00\n'
mine, theirs, agree = p.compare(text, delimiter=';')
assert agree, list(zip(mine, theirs))
assert mine[2][0] == 'Berlin; Mitte'"
}

run_end_to_end() {
  local script="$1"
  echo "Running ${script} end to end ..."
  local out code
  out="$(cd "${lab_dir}" && python3 "${script}" 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ] && printf '%s' "${out}" | grep -qF "round trip lossless: JSON yes, JSONL yes, CSV yes"; then
    check "${script} runs end to end and reports a lossless round trip" "yes"
  else
    check "${script} runs end to end and reports a lossless round trip" "no"
    echo "    (exit ${code}; output: ${out})"
  fi
}

# --- reference: always strict ---
run_wrangle_checks "${lab_dir}/examples"
run_parser_checks "${lab_dir}/examples"
run_end_to_end "examples/wrangle.py"

check_py "the written out/orders.jsonl parses line by line as JSON" "${lab_dir}/examples" \
"import json, os
from pathlib import Path
p = Path(os.environ['LAB']) / 'out' / 'orders.jsonl'
recs = [json.loads(ln) for ln in p.read_text(encoding='utf-8').splitlines() if ln.strip()]
assert len(recs) == 5
assert recs[2]['customer'] == 'Alan \"Turing\" Jr.'"

# --- learner starter ---
echo "Testing starter/ ..."
starter_wrangle="${lab_dir}/starter/wrangle.py"
starter_parser="${lab_dir}/starter/csv_field_parser.py"

for f in "${starter_wrangle}" "${starter_parser}"; do
  if python3 -c "compile(open('${f}').read(), '${f}', 'exec')" 2>/dev/null; then
    check "$(basename "${f}") is valid Python" "yes"
  else
    check "$(basename "${f}") is valid Python" "no"
  fi
done

if grep -q 'NotImplementedError' "${starter_wrangle}" || grep -q 'NotImplementedError' "${starter_parser}"; then
  echo "Note: starter/ still has unfinished exercises — testing structure only."
  for name in naive_report read_rows clean_row write_jsonl read_jsonl; do
    if grep -q "def ${name}" "${starter_wrangle}"; then
      check "starter defines ${name}" "yes"
    else
      check "starter defines ${name}" "no"
    fi
  done
  if grep -q 'def parse_csv' "${starter_parser}"; then
    check "starter defines parse_csv" "yes"
  else
    check "starter defines parse_csv" "no"
  fi
else
  run_wrangle_checks "${lab_dir}/starter"
  run_parser_checks "${lab_dir}/starter"
  run_end_to_end "starter/wrangle.py"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
