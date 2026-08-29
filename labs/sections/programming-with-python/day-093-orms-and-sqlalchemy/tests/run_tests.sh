#!/usr/bin/env bash
# Tests for the Day 093 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# This harness proves the claims the lesson makes, and it proves nearly all of
# them by COUNTING THE STATEMENTS the ORM emitted rather than by checking that
# the answer looked right. That distinction is the lab:
#
#   * the toy ORM generates its own DDL and DML, maps rows back into objects,
#     and answers a repeat lookup from its identity map with NO SQL at all;
#   * SQLAlchemy 2.0's declarative models describe the same domain, and the
#     versions in requirements/requirements.txt are the ones actually loaded;
#   * an object moves transient -> pending -> persistent -> detached, and each
#     transition is observed rather than asserted from memory;
#   * flush is not commit — a genuinely separate connection cannot see the
#     flushed row until the transaction commits;
#   * the N+1 problem really is 1 + N, and selectinload really is exactly 2
#     statements while joinedload really is exactly 1;
#   * DetachedInstanceError is provoked twice, on a column and on a
#     relationship, and fixed two different ways;
#   * a flush inside a loop costs 500 cursor executions where one batched
#     flush costs 1 — and, honestly, a batched ORM insert costs the SAME
#     number of executions as Core, which is not what folklore says;
#   * the lab leaves no database, no __pycache__ and no temporary directory
#     behind, opens no socket, and contains no URL and no sudo.
#
# Everything runs offline against in-memory and temporary SQLite databases.
# Deterministic, non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that would
# then fail the cleanliness check at the end of this script -- failing the
# reader for following the instructions. Clearing them here makes that final
# check measure what it claims to: what THIS run left behind. `.venv` is
# untouched, because the packages' own bytecode is theirs, not ours.
find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

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

check_eq() {
  local label="$1" want="$2" got="$3"
  checks=$((checks + 1))
  if [ "${want}" = "${got}" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        expected: ${want}"
    echo "        actual  : ${got}"
    failures=$((failures + 1))
  fi
}

# Assert a line matching the pattern exists in the captured file.
check_grep() {
  local label="$1" file="$2" pattern="$3"
  checks=$((checks + 1))
  if grep -qE "${pattern}" "${file}"; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    echo "        no line in $(basename "${file}") matched: ${pattern}"
    failures=$((failures + 1))
  fi
}

# Resolve a tool: an explicit override, then this lab's .venv, then whatever is
# on PATH. Fails loudly with install instructions rather than skipping quietly.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

install_hint() {
  echo "  Install the pinned dependency with:" >&2
  echo "    cd ${lab_dir}" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing interpreter:" >&2
  echo "    PYTHON=/path/to/python3 PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
}

python_bin="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found." >&2
  install_hint
  exit 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  install_hint
  exit 1
}

if ! "${python_bin}" -c "import sqlalchemy" >/dev/null 2>&1; then
  echo "FAIL: SQLAlchemy is not importable from ${python_bin}." >&2
  echo "  This lab is about SQLAlchemy, so there is nothing to fall back to." >&2
  install_hint
  exit 1
fi

work="$(mktemp -d)"
cleanup() { rm -rf "${work}"; }
trap cleanup EXIT

export PYTHONPATH="${lab_dir}/examples"

echo "Day 093 — ORMs and SQLAlchemy"
echo

# ---------------------------------------------------------------------------
echo "1. Environment — the versions actually in use"
# ---------------------------------------------------------------------------
"${python_bin}" - > "${work}/versions.txt" <<'PY'
import platform
import sqlalchemy
import sqlite3
print(f"python {platform.python_version()}")
print(f"sqlalchemy {sqlalchemy.__version__}")
print(f"sqlite {sqlite3.sqlite_version}")
PY
sed 's/^/    /' "${work}/versions.txt"

pinned="$(grep -iE '^SQLAlchemy==' "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
installed="$(awk '/^sqlalchemy /{print $2}' "${work}/versions.txt")"
check_eq "the installed SQLAlchemy is the version requirements.txt pins" \
  "${pinned}" "${installed}"
# Written as a plain if rather than a `case` inside `$( )`: bash 3.2, which is
# still what macOS ships, mis-parses the `)` of a case pattern as the end of
# the command substitution and silently yields the wrong answer.
if [ "${installed%%.*}" = "2" ]; then major_is_two=yes; else major_is_two=no; fi
check "SQLAlchemy is 2.x, so the modern declarative API is available" \
  "${major_is_two}"

# The lesson claims Alembic is not exercised here. Prove the claim is honest
# rather than merely stated: if it were installed, the claim would need
# rewriting, so the harness would rather fail than let the text go stale.
check "the lesson's claim that Alembic is not installed here is still true" \
  "$("${python_bin}" -c "import alembic" >/dev/null 2>&1 && echo no || echo yes)"

# ---------------------------------------------------------------------------
echo
echo "2. The toy ORM — DDL, DML, mapping back, and an identity map"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/demo_toy.py" > "${work}/toy.txt" 2>&1
check_eq "demo_toy.py exits 0" "0" "$?"

check_grep "the class declaration generates its own CREATE TABLE" \
  "${work}/toy.txt" '^CREATE TABLE members \(id INTEGER PRIMARY KEY, name TEXT, email TEXT\)$'
check_grep "add() emits no SQL — only the two CREATE TABLEs so far" \
  "${work}/toy.txt" 'statements emitted so far: 2'
check_grep "a pending object has no primary key yet" \
  "${work}/toy.txt" 'ada\.id before flush: None'
check_grep "flush() assigns the key the database chose" \
  "${work}/toy.txt" 'ada\.id after flush: 1'
check_grep "the identity map returns the SAME object" \
  "${work}/toy.txt" 'first is second      : True'
check_grep "and it is the very object that was added" \
  "${work}/toy.txt" 'first is ada         : True'
check_grep "a repeat lookup emits zero statements" \
  "${work}/toy.txt" 'statements emitted   : 0'
check_grep "one object means one edit — no lost update" \
  "${work}/toy.txt" 'changed via .first., read via .second.: Ada O\.'

toy_statements="$(grep -cE '^     ?[0-9]+\. ' "${work}/toy.txt")"
check_eq "the toy session sent exactly 8 statements in total" "8" "${toy_statements}"

# The toy's identity map must survive a SELECT as well as a get(), which is the
# property that makes it a unit of work rather than a cache with a nice name.
"${python_bin}" - > "${work}/toy_identity.txt" <<'PY'
import sqlite3
from tiny_orm import Column, Model, Session


class Member(Model):
    __table__ = "members"
    id = Column("INTEGER", primary_key=True)
    name = Column("TEXT")


session = Session(sqlite3.connect(":memory:"))
session.create_all(Member)
ada = Member(name="Ada")
session.add(ada)
session.commit()
first = session.select(Member)[0]
second = session.get(Member, 1)
print("SAME", first is second and second is ada)
try:
    Member(nickname="oops")
    print("UNKNOWN_COLUMN rejected=False")
except TypeError:
    print("UNKNOWN_COLUMN rejected=True")
PY
check_grep "a SELECT and a get() return one object, not two copies" \
  "${work}/toy_identity.txt" '^SAME True$'
check_grep "the toy rejects a column it never declared" \
  "${work}/toy_identity.txt" '^UNKNOWN_COLUMN rejected=True$'

# ---------------------------------------------------------------------------
echo
echo "3. SQLAlchemy 2.0 — the same four operations, and the SQL it emitted"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/demo_sqlalchemy.py" > "${work}/sqla.txt" 2>&1
check_eq "demo_sqlalchemy.py exits 0" "0" "$?"

check_grep "add() emits zero statements" \
  "${work}/sqla.txt" 'statements emitted by add\(\): 0'
check_grep "an added object is pending, not persistent" \
  "${work}/sqla.txt" 'state -> transient=False pending=True persistent=False detached=False'
check_grep "flush() emits exactly one INSERT" \
  "${work}/sqla.txt" '1\. INSERT INTO members \(name, email\) VALUES \(\?, \?\)'
check_grep "and the database assigned the key" \
  "${work}/sqla.txt" 'member\.id                  : 7'
check_grep "after the flush the object is persistent" \
  "${work}/sqla.txt" 'state -> transient=False pending=False persistent=True detached=False'
check_grep "the identity map answers a repeat get() with no SQL" \
  "${work}/sqla.txt" 'statements emitted : 0'
check_grep "select() compiles to the SQL the lesson prints" \
  "${work}/sqla.txt" 'SELECT books\.title, books\.author FROM books WHERE books\.copies >= \? ORDER BY books\.title'
check_grep "a join and an aggregate produce the expected top row" \
  "${work}/sqla.txt" 'Ada Okonkwo      3'
check_grep "the many-to-many secondary table resolves five craft books" \
  "${work}/sqla.txt" "Book\(id=8, title='Effective Java'\)"

# The declarative models must round-trip through Core metadata, because the
# claim "the ORM is built on Core" is only worth making if it is checkable.
"${python_bin}" - > "${work}/metadata.txt" <<'PY'
from models import Base
names = sorted(Base.metadata.tables)
print("TABLES", " ".join(names))
loans = Base.metadata.tables["loans"]
print("FKS", len(loans.foreign_keys))
print("SECONDARY", "book_tags" in Base.metadata.tables)
PY
check_grep "all five tables register in one MetaData" \
  "${work}/metadata.txt" '^TABLES book_tags books loans members tags$'
check_grep "the loans table carries both foreign keys" \
  "${work}/metadata.txt" '^FKS 2$'
check_grep "the many-to-many secondary is a Core Table, not a mapped class" \
  "${work}/metadata.txt" '^SECONDARY True$'

# ---------------------------------------------------------------------------
echo
echo "4. The Session as a unit of work"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/demo_unit_of_work.py" > "${work}/uow.txt" 2>&1
check_eq "demo_unit_of_work.py exits 0" "0" "$?"

check_grep "a constructed object is transient" \
  "${work}/uow.txt" 'just constructed          -> transient'
check_grep "add() makes it pending" \
  "${work}/uow.txt" 'after session\.add\(\)       -> pending'
check_grep "flush() makes it persistent and gives it a key" \
  "${work}/uow.txt" 'after session\.flush\(\)     -> persistent   id=7'
check_grep "close() makes it detached" \
  "${work}/uow.txt" 'after session\.close\(\)     -> detached'

check_grep "the flush really did send the INSERT" \
  "${work}/uow.txt" '1\. INSERT INTO members \(name, email\) VALUES \(\?, \?\)'
check_grep "yet an outside connection still sees only 7 members" \
  "${work}/uow.txt" 'after flush, other connection sees : 7 members'
check_grep "and sees 8, with the new name, only after the commit" \
  "${work}/uow.txt" "after commit, other connection sees: 8 members, last 'Hana Ito'"

check_grep "autoflush emits the pending INSERT before an unrelated SELECT" \
  "${work}/uow.txt" '1\. INSERT INTO members \(name, email\) VALUES \(\?, \?\)'
check_grep "and the SELECT follows it in the same counted window" \
  "${work}/uow.txt" '2\. SELECT members\.id, members\.name, members\.email FROM members WHERE members\.name LIKE \?'

check_grep "reading a column after close raises DetachedInstanceError" \
  "${work}/uow.txt" 'Instance <Member at 0xADDR> is not bound to a Session; attribute refresh operation cannot proceed'
check_grep "expire_on_commit=False keeps the loaded column readable" \
  "${work}/uow.txt" "ada\.name after close: 'Ada Okonkwo'"
check_grep "touching a lazy relationship after close raises too" \
  "${work}/uow.txt" "lazy load operation of attribute 'loans' cannot proceed"
check_grep "eager loading is the fix for the relationship case" \
  "${work}/uow.txt" 'len\(ada\.loans\) after close: 4'
check_grep "the temporary database is removed on the way out" \
  "${work}/uow.txt" 'temporary database removed: True'

# ---------------------------------------------------------------------------
echo
echo "5. The N+1 problem, counted and then fixed"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/demo_n_plus_one.py" > "${work}/nplus1.txt" 2>&1
check_eq "demo_n_plus_one.py exits 0" "0" "$?"

check_grep "the naive loop reaches all 24 loans" \
  "${work}/nplus1.txt" 'members: 6   loans reached: 24'
check_grep "lazy loading costs 1 + N = 7 statements" \
  "${work}/nplus1.txt" 'lazy \(default\)    7 statements   <- 1 \+ N'
check_grep "selectinload costs exactly 2, whatever N is" \
  "${work}/nplus1.txt" 'selectinload      2 statements   <- 1 \+ 1, whatever N is'
check_grep "joinedload costs exactly 1, at the price of wider rows" \
  "${work}/nplus1.txt" 'joinedload        1 statement    <- 1, but wider rows'
check_grep "a joinedload of a collection without unique() raises, and says why" \
  "${work}/nplus1.txt" 'The unique\(\) method must be invoked on this Result'
check_grep "the JOIN really returns 24 rows for 6 members" \
  "${work}/nplus1.txt" 'rows the JOIN actually returned : 24'
check_grep "which collapse to 6 distinct Member objects" \
  "${work}/nplus1.txt" 'distinct Member objects built   : 6'
check_grep "the identity map caps a many-to-one N+1 at the DISTINCT count" \
  "${work}/nplus1.txt" 'loans: 24   distinct titles: 8'
check_grep "joinedload flattens that many-to-one case to one statement" \
  "${work}/nplus1.txt" 'with joinedload\(Loan\.book\): 1 statement, 8 titles'
check_grep "the many-to-many is 9 statements lazily" \
  "${work}/nplus1.txt" 'lazy         9 statements'
check_grep "and 2 with selectinload" \
  "${work}/nplus1.txt" 'selectinload 2 statements'

# The counts above are the specific numbers for this seed. The property that
# matters is more general than any of them, so assert the property directly:
# eager loading must be constant in N while lazy loading grows with it.
"${python_bin}" - > "${work}/scaling.txt" <<'PY'
from sqlalchemy import insert, select
from sqlalchemy.orm import Session, selectinload

from counting import QueryCounter
from library import build_engine
from models import Member

for extra in (0, 30):
    engine = build_engine()
    if extra:
        with engine.begin() as connection:
            connection.execute(
                insert(Member),
                [
                    {"name": f"Extra {n}", "email": f"extra{n}@library.test"}
                    for n in range(extra)
                ],
            )
    with Session(engine) as session:
        with QueryCounter(engine) as lazy:
            for member in session.scalars(select(Member)).all():
                len(member.loans)
    with Session(engine) as session:
        with QueryCounter(engine) as eager:
            for member in session.scalars(
                select(Member).options(selectinload(Member.loans))
            ).all():
                len(member.loans)
    print(f"MEMBERS {6 + extra} LAZY {len(lazy)} EAGER {len(eager)}")
    engine.dispose()
PY
check_grep "with 6 members: lazy 7, eager 2" \
  "${work}/scaling.txt" '^MEMBERS 6 LAZY 7 EAGER 2$'
check_grep "with 36 members: lazy 37, eager still 2 — N+1 against a constant" \
  "${work}/scaling.txt" '^MEMBERS 36 LAZY 37 EAGER 2$'

# ---------------------------------------------------------------------------
echo
echo "6. Bulk work — and an honest reading of the numbers"
# ---------------------------------------------------------------------------
"${python_bin}" "${lab_dir}/examples/demo_bulk.py" > "${work}/bulk.txt" 2>&1
check_eq "demo_bulk.py exits 0" "0" "$?"

check_grep "a flush inside the loop costs one execution per row" \
  "${work}/bulk.txt" '500 cursor execution\(s\), 500 parameter set\(s\), 0 of them batched'
check_grep "add_all() with one flush batches 500 rows into 1 execution" \
  "${work}/bulk.txt" 'add_all\(\) \+ one flush        1 execution\(s\)    500 row\(s\)'
check_grep "Core insert() costs the SAME 1 execution - not fewer" \
  "${work}/bulk.txt" 'Core insert\(\), one call      1 execution\(s\)    500 row\(s\)'
check_grep "the ORM update loop must SELECT before it can UPDATE" \
  "${work}/bulk.txt" 'ORM, object by object : 2 cursor execution\(s\), 14 parameter set\(s\)'
check_grep "and it builds one object per matching row" \
  "${work}/bulk.txt" '13 Loan objects built in memory'
check_grep "a Core UPDATE is 1 execution and builds no objects" \
  "${work}/bulk.txt" 'Core UPDATE           : 1 cursor execution\(s\), 1 parameter set\(s\)'
check_grep "the object count is what scales — 1013 of them at 1000 more rows" \
  "${work}/bulk.txt" '1013 Loan objects built in memory'
check_grep "while Core stays at zero objects for the same 1013 rows" \
  "${work}/bulk.txt" '0 Loan objects built, 1013 rows changed'

# ---------------------------------------------------------------------------
echo
echo "7. The starter exercises"
# ---------------------------------------------------------------------------
(cd "${lab_dir}" && "${pytest_bin}" starter -q > "${work}/starter.txt" 2>&1)
starter_status=$?
check_eq "pytest starter exits 0 on the unmodified skeleton" "0" "${starter_status}"
check_grep "one baseline test passes and nine exercises wait" \
  "${work}/starter.txt" '1 passed, 9 skipped'

# Every skipped test must name the exercise that unblocks it, or the starter is
# a wall rather than a ladder.
skip_reasons="$(grep -c 'reason="Exercise' "${lab_dir}/starter/test_queries.py")"
check_eq "all nine skipped tests name their exercise" "9" "${skip_reasons}"
exercise_markers="$(grep -c '^    EXERCISE [0-9]' "${lab_dir}/starter/queries.py")"
check_eq "and queries.py carries a matching numbered exercise for each" \
  "10" "${exercise_markers}"

# The skeleton must actually RUN — a starter that raises before the learner has
# touched it teaches nothing except that the lab is broken.
"${python_bin}" - > "${work}/skeleton.txt" 2>&1 <<'PY'
import sys
sys.path.insert(0, "starter")
from sqlalchemy.orm import Session

from library import build_engine
from queries import books_with_at_least, loan_titles, member_loan_totals, open_loan_counts

engine = build_engine()
with Session(engine) as session:
    print("BOOKS", books_with_at_least(session, 3))
    print("COUNTS", open_loan_counts(session)[0])
    print("TOTALS", member_loan_totals(session)[0])
    print("TITLES", len(loan_titles(session)))
engine.dispose()
PY
check_grep "the unmodified skeleton returns the RIGHT answers, slowly" \
  "${work}/skeleton.txt" "^BOOKS \['Clean Code', 'Introduction to Algorithms', 'The C Programming Language'\]$"
check_grep "including the busiest borrower" \
  "${work}/skeleton.txt" "^COUNTS \('Ada Okonkwo', 3\)$"
check_grep "and every loan title" \
  "${work}/skeleton.txt" '^TITLES 24$'

# ---------------------------------------------------------------------------
echo
echo "8. Captured output still matches a live run"
# ---------------------------------------------------------------------------
for capture in toy sqlalchemy unit-of-work n-plus-one bulk; do
  case "${capture}" in
    toy)          live="${work}/toy.txt" ;;
    sqlalchemy)   live="${work}/sqla.txt" ;;
    unit-of-work) live="${work}/uow.txt" ;;
    n-plus-one)   live="${work}/nplus1.txt" ;;
    bulk)         live="${work}/bulk.txt" ;;
  esac
  stored="${lab_dir}/expected-output/${capture}.txt"
  checks=$((checks + 1))
  if [ ! -f "${stored}" ]; then
    echo "  FAIL: expected-output/${capture}.txt is missing"
    failures=$((failures + 1))
  elif diff -q "${stored}" "${live}" >/dev/null 2>&1; then
    echo "  ok: expected-output/${capture}.txt matches this run exactly"
  else
    echo "  FAIL: expected-output/${capture}.txt differs from this run"
    diff "${stored}" "${live}" | head -12 | sed 's/^/        /'
    failures=$((failures + 1))
  fi
done

# ---------------------------------------------------------------------------
echo
echo "9. Hygiene — offline, self-contained, and leaving nothing behind"
# ---------------------------------------------------------------------------
"${python_bin}" - "${lab_dir}" > "${work}/hygiene.txt" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
skip = {".venv", "__pycache__", ".pytest_cache"}
urls, sudo_lines, net = set(), [], []
comment = re.compile(r"^\s*(#|--)")
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.suffix not in {".py", ".sh", ".ini"}:
        continue
    if skip & set(path.parts):
        continue
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
    ):
        urls.update(re.findall(r"https?://[^\s\"')]+", line))
        if re.search(r"(^|[;|&(]\s*)sudo\s", line) and not comment.match(line):
            sudo_lines.append(f"{path.name}:{number}")
        if re.match(r"\s*(import|from)\s+(urllib|http|requests)\b", line):
            net.append(f"{path.name}:{number}")
print("URLS " + " ".join(sorted(urls)))
print("SUDO " + " ".join(sudo_lines))
print("NET " + " ".join(net))
PY
check_eq "no URL appears anywhere in the lab's scripts" "URLS" \
  "$(grep '^URLS ' "${work}/hygiene.txt" | sed 's/ *$//')"
check_eq "no line in this lab would actually invoke sudo" "SUDO" \
  "$(grep '^SUDO ' "${work}/hygiene.txt" | sed 's/ *$//')"
check_eq "nothing here imports an HTTP client" "NET" \
  "$(grep '^NET ' "${work}/hygiene.txt" | sed 's/ *$//')"

check "the starter test suite arms a guard against opening a socket" \
  "$(grep -q 'NetworkAccessAttempted' "${lab_dir}/starter/conftest.py" && echo yes || echo no)"

# And prove that guard is not decorative, by tripping it on purpose.
(cd "${lab_dir}/starter" && "${python_bin}" - > "${work}/guard.txt" 2>&1 <<'PY'
import conftest  # noqa: F401  — importing it arms the guard
import socket

try:
    socket.create_connection(("127.0.0.1", 9))
    print("GUARD armed=False")
except conftest.NetworkAccessAttempted:
    print("GUARD armed=True")
PY
)
check_grep "and the guard really refuses a connection when one is attempted" \
  "${work}/guard.txt" '^GUARD armed=True$'

check "no captured output leaks an absolute home path" \
  "$(grep -rl '/Users/\|/home/' "${lab_dir}/expected-output" >/dev/null 2>&1 && echo no || echo yes)"
check "every invented email address uses the library.test domain" \
  "$(grep -ohE '[A-Za-z0-9._-]+@[A-Za-z0-9._-]+' "${lab_dir}/examples/library.py" | grep -v '@library\.test$' >/dev/null 2>&1 && echo no || echo yes)"
check "this suite created no database file inside the lab directory" \
  "$(find "${lab_dir}" -name '*.db' -not -path '*/.venv/*' | grep -q . && echo no || echo yes)"
check "and left no __pycache__ behind" \
  "$(find "${lab_dir}" -type d -name '__pycache__' -not -path '*/.venv/*' | grep -q . && echo no || echo yes)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
