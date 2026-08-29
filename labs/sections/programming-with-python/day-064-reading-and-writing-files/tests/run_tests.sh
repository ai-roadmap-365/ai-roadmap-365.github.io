#!/usr/bin/env bash
# Tests for the Day 064 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# These checks exercise real file behaviour, not file existence: text is
# written and read back byte for byte, a real large file is generated and
# read both ways with tracemalloc measuring both peaks, a genuinely
# undecodable byte is written and recovered from, the atomic writer is
# interrupted mid-operation and the directory inspected, and a real
# directory tree is walked with pathlib. Every check runs in a throwaway
# temporary directory that is removed afterwards. No network, no
# privileges, non-interactive. Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

scratch="$(mktemp -d -t day064-tests.XXXXXX)"
cleanup() { rm -rf "${scratch}"; }
trap cleanup EXIT

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

# check_toolkit <label> <toolkit_dir> <python-body>
# Runs an assertion body against fileio_toolkit imported from toolkit_dir.
# A clean exit (every assert passed) is a pass.
check_toolkit() {
  local label="$1" toolkit_dir="$2" body="$3"
  local out
  if out="$(PYTHONPATH="${toolkit_dir}" SCRATCH="${scratch}" python3 -c "
import os
from pathlib import Path
import fileio_toolkit as t
scratch = Path(os.environ['SCRATCH'])
${body}" 2>&1)"; then
    check "${label}" "yes"
  else
    check "${label}" "no"
    echo "    (${out##*$'\n'})"
  fi
}

run_toolkit_checks() {
  local dir="$1"
  echo "Testing the toolkit in ${dir} (real files in a temporary directory) ..."

  check_toolkit "1. text round-trips through an explicit utf-8 encoding" "${dir}" "
p = scratch / 'round.txt'
text = 'line one\ncafé\n'
size = t.write_text_file(p, text)
assert t.read_text_file(p) == text, 'round-trip changed the text'
assert size == len(text.encode('utf-8')), f'size {size} is not the utf-8 byte count'
assert size > len(text), 'café must take more bytes than characters in utf-8'
"

  check_toolkit "1b. mode 'w' replaces rather than appends" "${dir}" "
p = scratch / 'replace.txt'
t.write_text_file(p, 'first\n')
t.write_text_file(p, 'second\n')
assert t.read_text_file(p) == 'second\n', 'mode w must truncate first'
"

  check_toolkit "1c. write() adds no newline of its own" "${dir}" "
p = scratch / 'nonewline.txt'
size = t.write_text_file(p, 'abc')
assert size == 3, f'expected 3 bytes, got {size}'
assert t.read_text_file(p) == 'abc'
"

  check_toolkit "2. streaming and whole-file reads agree on the longest line" "${dir}" "
p = scratch / 'big.log'
t.make_big_file(p, 20000, long_line_at=10000)
whole_len, whole_peak = t.longest_line_whole_file(p)
stream_len, stream_peak = t.longest_line_streaming(p)
assert whole_len == stream_len == 60, f'{whole_len} != {stream_len} != 60'
assert stream_peak > 0, 'tracemalloc peak should be measured, not zero'
"

  check_toolkit "2b. streaming peak memory is far below the whole-file peak" "${dir}" "
p = scratch / 'big.log'
t.make_big_file(p, 20000, long_line_at=10000)
_, whole_peak = t.longest_line_whole_file(p)
_, stream_peak = t.longest_line_streaming(p)
assert stream_peak * 4 < whole_peak, f'streaming {stream_peak} vs whole {whole_peak}'
"

  check_toolkit "3. a strict utf-8 read of a latin-1 byte raises UnicodeDecodeError" "${dir}" "
p = scratch / 'broken.log'
p.write_bytes(b'caf\xe9 logged\n')
try:
    t.read_text_file(p)
    raise SystemExit('strict read should have raised')
except UnicodeDecodeError as err:
    assert '0xe9' in str(err), str(err)
"

  check_toolkit "3b. errors='replace' recovers the file with U+FFFD" "${dir}" "
p = scratch / 'broken.log'
p.write_bytes(b'caf\xe9 logged\n')
text, recovered = t.read_text_surviving_bad_bytes(p)
assert recovered is True, 'the fallback should have been needed'
assert text == 'caf� logged\n', repr(text)
"

  check_toolkit "3c. a clean utf-8 file needs no fallback" "${dir}" "
p = scratch / 'clean.txt'
t.write_text_file(p, 'café\n')
text, recovered = t.read_text_surviving_bad_bytes(p)
assert recovered is False and text == 'café\n', (recovered, text)
"

  check_toolkit "4. atomic write leaves the OLD file intact until os.replace" "${dir}" "
box = scratch / 'atomic'
box.mkdir(exist_ok=True)
target = box / 'config.txt'
t.write_text_file(target, 'version = 1\n')
seen = {}
def peek(temp):
    seen['names'] = sorted(p.name for p in box.iterdir())
    seen['content'] = t.read_text_file(target)
    seen['temp'] = t.read_text_file(temp)
t.atomic_write_text(target, 'version = 2\n', after_temp=peek)
assert seen['names'] == ['config.txt', 'config.txt.tmp'], seen['names']
assert seen['content'] == 'version = 1\n', seen['content']
assert seen['temp'] == 'version = 2\n', seen['temp']
"

  check_toolkit "4b. after os.replace the new content is there and no .tmp remains" "${dir}" "
box = scratch / 'atomic2'
box.mkdir(exist_ok=True)
target = box / 'config.txt'
t.write_text_file(target, 'version = 1\n')
t.atomic_write_text(target, 'version = 2\n')
assert t.read_text_file(target) == 'version = 2\n'
assert sorted(p.name for p in box.iterdir()) == ['config.txt'], 'a .tmp file was left behind'
"

  check_toolkit "4c. the temp file sits in the SAME directory as the target" "${dir}" "
box = scratch / 'atomic3'
box.mkdir(exist_ok=True)
target = box / 'config.txt'
t.write_text_file(target, 'old\n')
seen = {}
t.atomic_write_text(target, 'new\n', after_temp=lambda temp: seen.update(parent=temp.parent))
assert seen['parent'] == box, f\"temp was in {seen['parent']}, not {box}\"
"

  check_toolkit "4d. the naive write is caught holding a half-written file" "${dir}" "
p = scratch / 'unsafe.txt'
t.write_text_file(p, 'version = 1\n')
seen = {}
t.unsafe_write_text(p, 'version = 2 with more content\n',
                    after_open=lambda path: seen.update(mid=t.read_text_file(path)))
assert seen['mid'] != 'version = 1\n', 'the old content should already be gone'
assert seen['mid'] != 'version = 2 with more content\n', 'it should still be incomplete'
"

  check_toolkit "5. list_tree finds every file as a sorted relative path" "${dir}" "
tree = scratch / 'tree'
(tree / 'sub' / 'deeper').mkdir(parents=True, exist_ok=True)
t.write_text_file(tree / 'a.txt', 'a\n')
t.write_text_file(tree / 'sub' / 'b.txt', 'b\n')
t.write_text_file(tree / 'sub' / 'deeper' / 'c.txt', 'c\n')
found = t.list_tree(tree)
assert found == ['a.txt', os.path.join('sub', 'b.txt'), os.path.join('sub', 'deeper', 'c.txt')], found
"

  check_toolkit "5b. list_tree returns files only, never directories" "${dir}" "
tree = scratch / 'tree'
found = t.list_tree(tree)
assert all(not (tree / f).is_dir() for f in found), found
assert 'sub' not in found, 'directories must be filtered out'
"
}

run_demo_checks() {
  local script="$1" label_prefix="$2"
  echo "Testing ${script} end to end ..."
  local out code demo_ws
  demo_ws="${scratch}/demo-$(basename "$(dirname "${script}")")"
  out="$(python3 "${script}" "${demo_ws}" 2>&1)"
  code=$?
  if [ "${code}" -eq 0 ]; then
    check "${label_prefix}: driver exits 0" "yes"
  else
    check "${label_prefix}: driver exits 0" "no"
    echo "    (exit ${code}; last line: ${out##*$'\n'})"
  fi
  for needle in \
    'round-trip identical: True' \
    'same answer: True' \
    'UnicodeDecodeError' \
    'recovered: True' \
    "config.txt', 'config.txt.tmp'" \
    '3 file(s) found by Path.rglob'
  do
    if printf '%s' "${out}" | grep -qF "${needle}"; then
      check "${label_prefix}: driver output contains \"${needle}\"" "yes"
    else
      check "${label_prefix}: driver output contains \"${needle}\"" "no"
    fi
  done
  rm -rf "${demo_ws}"
}

# --- Reference: always tested strictly ---
run_toolkit_checks "${lab_dir}/examples"
run_demo_checks "${lab_dir}/examples/demo.py" "examples"

# --- Learner starter ---
echo "Testing starter/fileio_toolkit.py ..."
starter_toolkit="${lab_dir}/starter/fileio_toolkit.py"
if python3 -c "compile(open('${starter_toolkit}').read(), '${starter_toolkit}', 'exec')" 2>/dev/null; then
  check "starter toolkit is valid Python" "yes"
else
  check "starter toolkit is valid Python" "no"
fi

if grep -q 'NotImplementedError' "${starter_toolkit}"; then
  echo "Note: starter/fileio_toolkit.py still has unfinished exercises — testing structure only."
  for name in write_text_file read_text_file longest_line_streaming \
              read_text_surviving_bad_bytes atomic_write_text list_tree; do
    if grep -q "def ${name}" "${starter_toolkit}"; then
      check "starter defines ${name}" "yes"
    else
      check "starter defines ${name}" "no"
    fi
  done
else
  run_toolkit_checks "${lab_dir}/starter"
  run_demo_checks "${lab_dir}/starter/demo.py" "starter"
  # A streaming reader that secretly slurps the file is not streaming.
  if grep -A 20 'def longest_line_streaming' "${starter_toolkit}" | grep -qE '\.read\(\)|\.readlines\(\)'; then
    check "starter longest_line_streaming avoids read()/readlines()" "no"
  else
    check "starter longest_line_streaming avoids read()/readlines()" "yes"
  fi
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
