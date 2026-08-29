#!/usr/bin/env bash
# Tests for the Day 095 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Every check below asserts a REAL VALUE, and every instant it asserts about
# is pinned in this file. Nothing here reads the clock, because a suite that
# used "now" would pass 363 days a year and fail on the two that matter.
#
# What it asks:
#
#   * is the IANA zone database actually present, and how many zones?
#   * are the 23-hour and the 25-hour day really 23 and 25 hours?
#   * does the ambiguous wall reading give two offsets and two instants?
#   * does the nonexistent one fail to survive a round trip?
#   * does UTC ISO text sort chronologically, and does local text not?
#   * does the hand-written resolver agree with zoneinfo on all 26 cases?
#   * does the starter report 0 of 10, and the reference solution 10 of 10?
#
# Nothing touches the network. Nothing needs sudo. Temporary work happens in
# mktemp -d and is removed in a trap, so a finished run leaves this directory
# exactly as it found it.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work=""
checks=0
failures=0

cleanup() { [ -n "${work}" ] && [ -d "${work}" ] && rm -rf "${work}"; }
trap cleanup EXIT INT TERM

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

# check_eq LABEL EXPECTED ACTUAL — prints what it wanted when it does not match.
check_eq() {
  local label="$1" expected="$2" actual="$3"
  checks=$((checks + 1))
  if [ "${expected}" = "${actual}" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        expected: ${expected}"
    echo "        actual:   ${actual}"
    failures=$((failures + 1))
  fi
}

python_bin="${PYTHON:-$(command -v python3 || true)}"
if [ -z "${python_bin}" ] || [ ! -x "${python_bin}" ]; then
  echo "python3 was not found. Install Python 3.11+ or set PYTHON=/path/to/python3."
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
work="$(mktemp -d)"

# py 'SOURCE' — run a snippet and echo its single line of output.
py() { "${python_bin}" -c "$1"; }

PRELUDE='
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
UTC = timezone.utc
L = ZoneInfo("Europe/London")
NY = ZoneInfo("America/New_York")
def daylen(y, m, d, z):
    a = datetime.combine(date(y, m, d), time(0), tzinfo=z)
    b = datetime.combine(date(y, m, d) + timedelta(days=1), time(0), tzinfo=z)
    return (b.astimezone(UTC) - a.astimezone(UTC)).total_seconds() / 3600
'

echo "Day 095 — Dates, Times, and Time Zones"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "zones:   $("${python_bin}" -c 'import zoneinfo; print(len(zoneinfo.available_timezones()))')"
echo "tzpath:  $("${python_bin}" -c 'import zoneinfo; print(zoneinfo.TZPATH[0] if zoneinfo.TZPATH else "empty")')"
echo "work:    a temporary directory, removed when this script exits"
echo

# ---------------------------------------------------------------------------
echo "1. The zone database is present and usable"
# ---------------------------------------------------------------------------
check "zoneinfo imports" \
  "$(py 'import zoneinfo' >/dev/null 2>&1 && echo yes || echo no)"
check "Europe/London loads from the system database" \
  "$(py 'from zoneinfo import ZoneInfo; ZoneInfo("Europe/London")' >/dev/null 2>&1 && echo yes || echo no)"
check "America/New_York loads" \
  "$(py 'from zoneinfo import ZoneInfo; ZoneInfo("America/New_York")' >/dev/null 2>&1 && echo yes || echo no)"
zone_total="$(py 'import zoneinfo; print(len(zoneinfo.available_timezones()))')"
check "the database holds more than 100 zones (found ${zone_total})" \
  "$([ "${zone_total}" -gt 100 ] && echo yes || echo no)"
check "a name that is not a zone raises ZoneInfoNotFoundError" \
  "$(py 'from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
try:
    ZoneInfo("Europe/Atlantis")
except ZoneInfoNotFoundError:
    raise SystemExit(0)
raise SystemExit(1)' >/dev/null 2>&1 && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "2. The 23-hour day and the 25-hour day"
# ---------------------------------------------------------------------------
check_eq "Europe/London 2026-03-29 is 23 hours" "23.0" \
  "$(py "${PRELUDE}"'print(daylen(2026, 3, 29, L))')"
check_eq "Europe/London 2026-10-25 is 25 hours" "25.0" \
  "$(py "${PRELUDE}"'print(daylen(2026, 10, 25, L))')"
check_eq "Europe/London 2026-06-15 is an ordinary 24 hours" "24.0" \
  "$(py "${PRELUDE}"'print(daylen(2026, 6, 15, L))')"
check_eq "America/New_York 2026-03-08 is 23 hours" "23.0" \
  "$(py "${PRELUDE}"'print(daylen(2026, 3, 8, NY))')"
check_eq "America/New_York 2026-11-01 is 25 hours" "25.0" \
  "$(py "${PRELUDE}"'print(daylen(2026, 11, 1, NY))')"
check_eq "the short and long days sum to exactly 48 hours" "48.0" \
  "$(py "${PRELUDE}"'print(daylen(2026, 3, 29, L) + daylen(2026, 10, 25, L))')"
check_eq "Australia/Lord_Howe moves by half an hour, not one" "23.5" \
  "$(py "${PRELUDE}"'print(daylen(2026, 10, 4, ZoneInfo("Australia/Lord_Howe")))')"
check_eq "subtracting two LOCAL midnights always says 24, even on 25 Oct" "24.0" \
  "$(py "${PRELUDE}"'
a = datetime.combine(date(2026, 10, 25), time(0), tzinfo=L)
b = datetime.combine(date(2026, 10, 26), time(0), tzinfo=L)
print((b - a).total_seconds() / 3600)')"

# ---------------------------------------------------------------------------
echo
echo "3. The hour that happened twice"
# ---------------------------------------------------------------------------
check_eq "2026-10-25 01:30 London: offsets are +01:00 then +00:00" "1:00:00|0:00:00" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 10, 25, 1, 30)
print(w.replace(tzinfo=L, fold=0).utcoffset(), w.replace(tzinfo=L, fold=1).utcoffset(), sep="|")')"
check_eq "the two folds name two instants an hour apart" \
  "2026-10-25T00:30:00+00:00|2026-10-25T01:30:00+00:00|1:00:00" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 10, 25, 1, 30)
a = w.replace(tzinfo=L, fold=0).astimezone(UTC)
b = w.replace(tzinfo=L, fold=1).astimezone(UTC)
print(f"{a.isoformat()}|{b.isoformat()}|{b - a}")')"
check_eq "the two epoch seconds differ by 3600" "3600.0" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 10, 25, 1, 30)
print(w.replace(tzinfo=L, fold=1).timestamp() - w.replace(tzinfo=L, fold=0).timestamp())')"
check_eq "and yet == says they are equal: compare in UTC, always" "True" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 10, 25, 1, 30)
print(w.replace(tzinfo=L, fold=0) == w.replace(tzinfo=L, fold=1))')"
check_eq "the tz names are BST then GMT" "BST|GMT" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 10, 25, 1, 30)
print(w.replace(tzinfo=L, fold=0).tzname(), w.replace(tzinfo=L, fold=1).tzname(), sep="|")')"
check_eq "a job firing when the local clock reads 01:30 fires twice" "2" \
  "$(py "${PRELUDE}"'
start = datetime(2026, 10, 25, 0, 0, tzinfo=L).astimezone(UTC)
fires = sum(1 for m in range(300)
            if (lambda x: (x.hour, x.minute) == (1, 30))((start + timedelta(minutes=m)).astimezone(L)))
print(fires)')"

# ---------------------------------------------------------------------------
echo
echo "4. The hour that never happened"
# ---------------------------------------------------------------------------
check_eq "2026-03-29 01:30 London does not survive a round trip" \
  "2026-03-29T02:30:00+01:00" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 3, 29, 1, 30).replace(tzinfo=L)
print(w.astimezone(UTC).astimezone(L).isoformat())')"
check_eq "fold=0 uses the offset before the gap, fold=1 the offset after" \
  "0:00:00|1:00:00" \
  "$(py "${PRELUDE}"'
w = datetime(2026, 3, 29, 1, 30)
print(w.replace(tzinfo=L, fold=0).utcoffset(), w.replace(tzinfo=L, fold=1).utcoffset(), sep="|")')"
check_eq "a job firing at local 01:30 fires zero times on 2026-03-29" "0" \
  "$(py "${PRELUDE}"'
start = datetime(2026, 3, 29, 0, 0, tzinfo=L).astimezone(UTC)
fires = sum(1 for m in range(300)
            if (lambda x: (x.hour, x.minute) == (1, 30))((start + timedelta(minutes=m)).astimezone(L)))
print(fires)')"
check_eq "the fold order separates the two cases: ambiguous <, nonexistent >" \
  "True|True" \
  "$(py "${PRELUDE}"'
def pair(w):
    return (w.replace(tzinfo=L, fold=0).astimezone(UTC), w.replace(tzinfo=L, fold=1).astimezone(UTC))
amb = pair(datetime(2026, 10, 25, 1, 30))
non = pair(datetime(2026, 3, 29, 1, 30))
print(f"{amb[0] < amb[1]}|{non[0] > non[1]}")')"

# ---------------------------------------------------------------------------
echo
echo "5. Sorting: UTC text works, local text does not"
# ---------------------------------------------------------------------------
SORT_PRELUDE="${PRELUDE}"'
KOL = ZoneInfo("Asia/Kolkata")
EVENTS = [
    ("checkout", datetime(2026, 8, 16, 18, 0, tzinfo=UTC), NY),
    ("dispatch", datetime(2026, 8, 16, 16, 0, tzinfo=UTC), L),
    ("packed",   datetime(2026, 8, 16, 15, 0, tzinfo=UTC), KOL),
    ("ordered",  datetime(2026, 8, 16, 11, 30, tzinfo=UTC), KOL),
]
def utc_text(i):
    return i.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
'
check_eq "UTC ISO text sorted as TEXT equals sorted by instant" "True" \
  "$(py "${SORT_PRELUDE}"'
by_text = sorted(utc_text(i) for _, i, _ in EVENTS)
by_instant = [utc_text(i) for _, i, _ in sorted(EVENTS, key=lambda e: e[1])]
print(by_text == by_instant)')"
check_eq "the UTC text order is the true chronological order" \
  "ordered,packed,dispatch,checkout" \
  "$(py "${SORT_PRELUDE}"'
rows = sorted(((utc_text(i), n) for n, i, _ in EVENTS))
print(",".join(n for _, n in rows))')"
check_eq "local text sorts into a DIFFERENT order — here, the reverse" \
  "checkout,dispatch,ordered,packed" \
  "$(py "${SORT_PRELUDE}"'
rows = sorted((i.astimezone(z).strftime("%Y-%m-%dT%H:%M:%S"), n) for n, i, z in EVENTS)
print(",".join(n for _, n in rows))')"
check_eq "local text WITH its offset also sorts wrongly" "False" \
  "$(py "${SORT_PRELUDE}"'
by_text = [n for _, n in sorted((i.astimezone(z).isoformat(), n) for n, i, z in EVENTS)]
by_instant = [n for n, _, _ in sorted(EVENTS, key=lambda e: e[1])]
print(by_text == by_instant)')"
check_eq "two instants an hour apart collapse to one local string" "True" \
  "$(py "${SORT_PRELUDE}"'
a = datetime(2026, 10, 25, 0, 30, tzinfo=UTC).astimezone(L).strftime("%Y-%m-%dT%H:%M:%S")
b = datetime(2026, 10, 25, 1, 30, tzinfo=UTC).astimezone(L).strftime("%Y-%m-%dT%H:%M:%S")
print(a == b)')"

# ---------------------------------------------------------------------------
echo
echo "6. Parsing, formatting and durations"
# ---------------------------------------------------------------------------
check_eq "fromisoformat accepts a trailing Z" "2026-10-25T01:30:00+00:00" \
  "$(py 'from datetime import datetime; print(datetime.fromisoformat("2026-10-25T01:30:00Z").isoformat())')"
check_eq "%Z does not parse BST at all" "ValueError" \
  "$(py 'from datetime import datetime
try:
    datetime.strptime("2026-10-25 01:30:00 BST", "%Y-%m-%d %H:%M:%S %Z")
    print("parsed")
except ValueError:
    print("ValueError")')"
check_eq "%Z parses UTC and then throws the zone away" "None" \
  "$(py 'from datetime import datetime
print(datetime.strptime("2026-10-25 01:30:00 UTC", "%Y-%m-%d %H:%M:%S %Z").tzinfo)')"
check_eq "%z with a numeric offset keeps it" "1:00:00" \
  "$(py 'from datetime import datetime
print(datetime.strptime("2026-10-25 01:30:00 +0100", "%Y-%m-%d %H:%M:%S %z").utcoffset())')"
check_eq "one ambiguous date string, two valid parses, two months apart" \
  "2026-03-05|2026-05-03" \
  "$(py 'from datetime import datetime
a = datetime.strptime("05/03/2026", "%d/%m/%Y").date()
b = datetime.strptime("05/03/2026", "%m/%d/%Y").date()
print(f"{a}|{b}")')"
check_eq "31 January plus timedelta(days=30) is 2 March, not one month" "2026-03-02" \
  "$(py 'from datetime import datetime, timedelta
print((datetime(2026, 1, 31) + timedelta(days=30)).date())')"
check_eq "a leap second is not representable" "ValueError" \
  "$(py 'from datetime import datetime
try:
    datetime(2016, 12, 31, 23, 59, 60)
    print("accepted")
except ValueError:
    print("ValueError")')"
check_eq "the signed 32-bit epoch runs out in January 2038" \
  "2038-01-19T03:14:07+00:00" \
  "$(py 'from datetime import datetime, timezone
print(datetime.fromtimestamp(2**31 - 1, timezone.utc).isoformat())')"

# ---------------------------------------------------------------------------
echo
echo "7. Wall clock against monotonic clock"
# ---------------------------------------------------------------------------
check_eq "time.monotonic() is monotonic and not adjustable" "True|False" \
  "$(py 'import time
i = time.get_clock_info("monotonic")
print(f"{i.monotonic}|{i.adjustable}")')"
check_eq "time.time() is neither" "False|True" \
  "$(py 'import time
i = time.get_clock_info("time")
print(f"{i.monotonic}|{i.adjustable}")')"
check "monotonic never goes backwards across 20000 samples" \
  "$(py 'import time
last = time.monotonic()
for _ in range(20000):
    now = time.monotonic()
    if now < last:
        raise SystemExit(1)
    last = now
raise SystemExit(0)' >/dev/null 2>&1 && echo yes || echo no)"
check "a monotonic measurement of real work is positive" \
  "$(py 'import time
s = time.monotonic()
t = sum(range(200000))
raise SystemExit(0 if time.monotonic() - s > 0 else 1)' >/dev/null 2>&1 && echo yes || echo no)"
check_eq "a wall-clock stopwatch across the repeated hour under-reports by 3600s" \
  "-3600.0" \
  "$(py "${PRELUDE}"'
start = datetime(2026, 10, 25, 0, 0, tzinfo=UTC)
end = start + timedelta(minutes=75)
naive = end.astimezone(L).replace(tzinfo=None) - start.astimezone(L).replace(tzinfo=None)
print((naive - timedelta(minutes=75)).total_seconds())')"
check_eq "and it can report a NEGATIVE duration for real work" "-2400.0" \
  "$(py "${PRELUDE}"'
start = datetime(2026, 10, 25, 0, 50, tzinfo=UTC)
end = start + timedelta(minutes=20)
naive = end.astimezone(L).replace(tzinfo=None) - start.astimezone(L).replace(tzinfo=None)
print(naive.total_seconds())')"

# ---------------------------------------------------------------------------
echo
echo "8. The from-scratch resolver agrees with the real database"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/06_resolver.py" >"${work}/resolver.txt" 2>&1
resolver_status=$?
check "examples/06_resolver.py exits 0" \
  "$([ ${resolver_status} -eq 0 ] && echo yes || echo no)"
check_eq "26 comparisons were made" "yes" \
  "$(grep -q "13 wall readings x 2 folds = 26 comparisons" "${work}/resolver.txt" && echo yes || echo no)"
check_eq "zero disagreements with zoneinfo" "disagreements with zoneinfo: 0" \
  "$(grep "disagreements with zoneinfo" "${work}/resolver.txt")"
check_eq "zero cases classified wrongly" "cases classified wrongly:    0" \
  "$(grep "cases classified wrongly" "${work}/resolver.txt")"
check_eq "no line in the comparison table says NO" "0" \
  "$(grep -c " NO$" "${work}/resolver.txt" || true)"
check_eq "the resolver classifies the gap as nonexistent" "6" \
  "$(grep -c "nonexistent" "${work}/resolver.txt")"
check_eq "and the repeat as ambiguous" "6" \
  "$(grep -c "ambiguous " "${work}/resolver.txt")"

# The resolver is not vacuous: corrupt the rule table and it must disagree.
sed 's/datetime(2026, 10, 25, 1, 0, tzinfo=UTC)/datetime(2026, 10, 18, 1, 0, tzinfo=UTC)/' \
  "${lab_dir}/examples/06_resolver.py" >"${work}/broken_resolver.py"
"${python_bin}" "${work}/broken_resolver.py" >"${work}/broken.txt" 2>&1
broken_status=$?
check "a resolver with a wrong transition date FAILS (proving the check is real)" \
  "$([ ${broken_status} -ne 0 ] && echo yes || echo no)"
check "the broken run reports disagreements with zoneinfo" \
  "$(grep -q "disagreements with zoneinfo: 0" "${work}/broken.txt" && echo no || echo yes)"

# ---------------------------------------------------------------------------
echo
echo "9. Every example script runs and prints what the lesson quotes"
# ---------------------------------------------------------------------------
for script in 01_zone_database 02_odd_days 03_fold 04_sorting 05_clocks; do
  "${python_bin}" "${lab_dir}/examples/${script}.py" >"${work}/${script}.txt" 2>&1
  status=$?
  check "examples/${script}.py exits 0" \
    "$([ ${status} -eq 0 ] && echo yes || echo no)"
done
check "01 reports the search path and a zone count" \
  "$(grep -q "zones available here:" "${work}/01_zone_database.txt" && echo yes || echo no)"
check "02 shows the 23-hour and 25-hour London days" \
  "$(grep -q "23.0h" "${work}/02_odd_days.txt" && grep -q "25.0h" "${work}/02_odd_days.txt" && echo yes || echo no)"
check "03 shows the local clock reading 01:30 twice" \
  "$(grep -q "the local clock read 01:30 2 times" "${work}/03_fold.txt" && echo yes || echo no)"
check "03 shows zero firings on the spring-forward day" \
  "$(grep -q "firings on 2026-03-29: 0" "${work}/03_fold.txt" && echo yes || echo no)"
check "04 proves the UTC text sort matches the instant sort" \
  "$(grep -q "sorted as text     == sorted as instants : True" "${work}/04_sorting.txt" && echo yes || echo no)"
check "05 reports monotonic as not adjustable" \
  "$(grep -q "monotonic        True       False" "${work}/05_clocks.txt" && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
echo "10. The starter and its reference answers"
# ---------------------------------------------------------------------------
bash "${lab_dir}/starter/02_check.sh" "${lab_dir}/starter/01_timezones.py" \
  >"${work}/starter.txt" 2>&1
starter_status=$?
check_eq "an untouched starter reports 0 of 10" "0 of 10 exercises complete." \
  "$(grep "exercises complete" "${work}/starter.txt")"
check "an untouched starter exits non-zero" \
  "$([ ${starter_status} -ne 0 ] && echo yes || echo no)"
check_eq "every exercise is reported as not started, not as an error" "10" \
  "$(grep -c "not started" "${work}/starter.txt")"

bash "${lab_dir}/starter/02_check.sh" "${lab_dir}/examples/07_solution.py" \
  >"${work}/solution.txt" 2>&1
solution_status=$?
check_eq "the reference answers report 10 of 10" "10 of 10 exercises complete." \
  "$(grep "exercises complete" "${work}/solution.txt")"
check "the reference answers exit 0" \
  "$([ ${solution_status} -eq 0 ] && echo yes || echo no)"

# And the marker is not vacuous either: break one answer, expect it caught.
sed 's/return first < second/return first != second/' \
  "${lab_dir}/examples/07_solution.py" >"${work}/broken_solution.py"
bash "${lab_dir}/starter/02_check.sh" "${work}/broken_solution.py" \
  >"${work}/broken_solution.txt" 2>&1
broken_solution_status=$?
check "a solution that confuses ambiguous with nonexistent is caught" \
  "$([ ${broken_solution_status} -ne 0 ] && echo yes || echo no)"
check_eq "and it is reported as WRONG rather than as complete" "9 of 10 exercises complete." \
  "$(grep "exercises complete" "${work}/broken_solution.txt")"

# ---------------------------------------------------------------------------
echo
echo "11. The lab is offline, unprivileged and leaves nothing behind"
# ---------------------------------------------------------------------------
check "no example or starter file imports a network module" \
  "$(grep -rlE "^[[:space:]]*(import|from)[[:space:]]+(socket|urllib|http|requests|ftplib|smtplib)" \
      "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null | grep -q . && echo no || echo yes)"
check "nothing in the lab invokes sudo" \
  "$(grep -rn "^[^#]*sudo " "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" 2>/dev/null | grep -q . && echo no || echo yes)"
check "no URL appears in any script in this lab" \
  "$(grep -rnE "https?://" "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" 2>/dev/null | grep -q . && echo no || echo yes)"
check "no script this suite asserts on ever reads the clock for an instant" \
  "$(grep -rn "datetime.now" "${lab_dir}/examples/01_zone_database.py" \
       "${lab_dir}/examples/02_odd_days.py" "${lab_dir}/examples/03_fold.py" \
       "${lab_dir}/examples/04_sorting.py" "${lab_dir}/examples/06_resolver.py" \
       "${lab_dir}/examples/07_solution.py" \
       2>/dev/null | grep -q . && echo no || echo yes)"
check "no __pycache__ directory was left in the lab" \
  "$([ -z "$(find "${lab_dir}" -type d -name __pycache__ 2>/dev/null)" ] && echo yes || echo no)"
check "no stray files were created in the lab directory" \
  "$([ -z "$(find "${lab_dir}" -maxdepth 1 -type f ! -name 'README.md' ! -name 'metadata.yml' ! -name 'security.md' ! -name 'troubleshooting.md' 2>/dev/null)" ] && echo yes || echo no)"

# ---------------------------------------------------------------------------
echo
if [ "${failures}" -eq 0 ]; then
  echo "${checks} checks, ${failures} failure(s)."
  exit 0
fi
echo "${checks} checks, ${failures} failure(s)."
exit 1
