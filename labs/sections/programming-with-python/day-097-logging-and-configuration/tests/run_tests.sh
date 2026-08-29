#!/usr/bin/env bash
# Tests for the Day 097 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# Every check compares a REAL VALUE. Log output is captured with a handler
# writing into a buffer — never by scraping stdout — so what is asserted on is
# exactly the records that reached that handler and nothing else.
#
# What this suite asks:
#
#   * does the logging module behave the way the lesson says it does — the
#     two-level trap, propagation and its duplicate, exception() against
#     error(str(e)), lazy formatting?
#   * does the JSON formatter produce parseable objects with the right
#     fields, and does the redacting filter keep the secret out of ALL of
#     them, including the traceback?
#   * does the four-layer resolver put the flag on top, report provenance
#     correctly, tell a missing environment variable from an empty one, and
#     refuse a bad value at startup with a message naming the setting?
#   * does the starter honestly report 0 of 12 before you start, and does the
#     checker say 12 of 12 for the reference answers?
#
# Nothing touches the network. Nothing needs sudo. Everything is built in a
# temporary directory removed by a trap, so a completed run leaves the lab
# directory exactly as it found it.
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

echo "Day 097 — Logging and Configuration"
echo "python3: $("${python_bin}" -c 'import sys; print(sys.version.split()[0])')"
echo "work:    a temporary directory, removed when this script exits"
echo

# tomllib arrived in Python 3.11. Fail with one clear line rather than a wall
# of import errors halfway through.
"${python_bin}" -c 'import tomllib' >/dev/null 2>&1
check "this python has tomllib (3.11 or newer)" \
  "$([ $? -eq 0 ] && echo yes || echo no)"

# ---------------------------------------------------------------------------
# The Python half of the suite. It writes one KEY=VALUE line per assertion
# into a file, which bash then compares. Log capture happens through buffer
# handlers inside this program.
# ---------------------------------------------------------------------------
"${python_bin}" - "${lab_dir}" > "${work}/facts.txt" 2>"${work}/facts.err" <<'PY'
import importlib.util, io, json, logging, os, subprocess, sys, tempfile
from pathlib import Path

lab = Path(sys.argv[1])
sys.path.insert(0, str(lab / "examples"))

from applog import JsonFormatter, RedactingFilter, buffer_handler, iso_utc
import appconfig
from appconfig import APP_SPEC, ConfigError, Setting, resolve, validate, validate_or_die

SECRET = "sk-live-9f2c4a7b1e63"
out = {}

def emit(key, value):
    out[key] = value

# --- the two-level trap ----------------------------------------------------
log = logging.getLogger("t.trap")
log.handlers.clear(); log.filters.clear(); log.propagate = False
log.setLevel(logging.DEBUG)
handler, stream = buffer_handler(logging.WARNING, logging.Formatter("%(message)s"))
log.addHandler(handler)
log.debug("dropped"); log.info("dropped"); log.warning("kept")
emit("TRAP_LINES", len(stream.getvalue().strip().splitlines()))
emit("TRAP_TEXT", stream.getvalue().strip())

log.handlers.clear()
handler, stream = buffer_handler(logging.DEBUG, logging.Formatter("%(message)s"))
log.addHandler(handler)
log.debug("now it comes out")
emit("TRAP_FIXED", stream.getvalue().strip())

# --- propagation and the duplicate ----------------------------------------
root = logging.getLogger()
saved = (root.handlers[:], root.level)
root.handlers.clear(); root.setLevel(logging.DEBUG)
rh, rstream = buffer_handler(logging.DEBUG, logging.Formatter("R:%(message)s"))
root.addHandler(rh)
app = logging.getLogger("t.app")
app.handlers.clear(); app.filters.clear(); app.setLevel(logging.DEBUG); app.propagate = True
ah, astream = buffer_handler(logging.DEBUG, logging.Formatter("A:%(message)s"))
app.addHandler(ah)
child = logging.getLogger("t.app.child")
child.handlers.clear(); child.filters.clear(); child.propagate = True
child.info("once")
emit("PROP_TOTAL", len(astream.getvalue().splitlines()) + len(rstream.getvalue().splitlines()))

app.propagate = False
astream.truncate(0); astream.seek(0); rstream.truncate(0); rstream.seek(0)
child.info("once")
emit("PROP_FIX1", len(astream.getvalue().splitlines()) + len(rstream.getvalue().splitlines()))

app.propagate = True; app.handlers.clear()
astream.truncate(0); astream.seek(0); rstream.truncate(0); rstream.seek(0)
child.info("once")
emit("PROP_FIX2", len(astream.getvalue().splitlines()) + len(rstream.getvalue().splitlines()))
root.handlers.clear(); root.handlers.extend(saved[0]); root.setLevel(saved[1])

# --- exception() against error(str(e)) -------------------------------------
log = logging.getLogger("t.exc")
log.handlers.clear(); log.filters.clear(); log.propagate = False; log.setLevel(logging.DEBUG)
h, s = buffer_handler(logging.DEBUG, logging.Formatter("%(message)s"))
log.addHandler(h)
try:
    int("sixty-four")
except ValueError as error:
    log.error("could not parse: %s", str(error))
emit("ERRSTR_HAS_TRACEBACK", "Traceback" in s.getvalue())
emit("ERRSTR_LINES", len(s.getvalue().strip().splitlines()))
s.truncate(0); s.seek(0)
try:
    int("sixty-four")
except ValueError:
    log.exception("could not parse")
emit("EXC_HAS_TRACEBACK", "Traceback" in s.getvalue())
emit("EXC_NAMES_TYPE", "ValueError" in s.getvalue())
emit("EXC_NAMES_FUNCTION", "int(" in s.getvalue())

# --- lazy formatting -------------------------------------------------------
class Counter:
    n = 0
    def __str__(self):
        Counter.n += 1
        return "rendered"

log = logging.getLogger("t.lazy")
log.handlers.clear(); log.filters.clear(); log.propagate = False
log.setLevel(logging.INFO)
h, s = buffer_handler(logging.INFO, logging.Formatter("%(message)s"))
log.addHandler(h)
Counter.n = 0
for _ in range(100):
    log.debug("x %s", Counter())
emit("LAZY_RENDERS", Counter.n)
Counter.n = 0
for _ in range(100):
    log.debug(f"x {Counter()}")
emit("EAGER_RENDERS", Counter.n)

# --- the JSON formatter ----------------------------------------------------
log = logging.getLogger("t.json")
log.handlers.clear(); log.filters.clear(); log.propagate = False; log.setLevel(logging.DEBUG)
h, s = buffer_handler(logging.DEBUG, JsonFormatter({"run_id": "run-4711"}))
log.addHandler(h)
log.info("batch complete", extra={"batch": 2, "kept": 61})
log.warning("upstream slow", extra={"status": 429})
try:
    int("nope")
except ValueError:
    log.exception("parse failed", extra={"batch": 3})
records = [json.loads(line) for line in s.getvalue().splitlines()]
emit("JSON_COUNT", len(records))
emit("JSON_FIRST_EVENT", records[0]["event"])
emit("JSON_FIRST_LEVEL", records[0]["level"])
emit("JSON_FIRST_RUNID", records[0]["run_id"])
emit("JSON_FIRST_KEPT", records[0]["kept"])
emit("JSON_LOGGER", records[0]["logger"])
emit("JSON_EXC_TYPE", records[2]["exc_type"])
emit("JSON_HAS_TRACEBACK_FIELD", "traceback" in records[2])
emit("JSON_TS_SHAPE", len(records[0]["ts"]) == 24 and records[0]["ts"].endswith("Z"))
emit("JSON_TS_SORTS", sorted(r["ts"] for r in records) == [r["ts"] for r in records])
emit("ISO_UTC_ZERO", iso_utc(0))

# --- the redacting filter --------------------------------------------------
def redacted_text(on_logger):
    logger = logging.getLogger("t.redact.logger" if on_logger else "t.redact.handler")
    logger.handlers.clear(); logger.filters.clear()
    logger.propagate = False; logger.setLevel(logging.DEBUG)
    h, s = buffer_handler(logging.DEBUG, JsonFormatter({"run_id": "run-4711"}))
    if on_logger:
        logger.addFilter(RedactingFilter([SECRET]))
    else:
        h.addFilter(RedactingFilter([SECRET]))
    logger.addHandler(h)
    logger.info("key %s", SECRET)
    logger.info(f"inline {SECRET}")
    logger.info("cfg", extra={"headers": {"Authorization": f"Bearer {SECRET}"}})
    logger.info("list", extra={"argv": ["--key", SECRET]})
    return logger, s

logger, s = redacted_text(on_logger=False)
emit("REDACT_SECRET_PRESENT", SECRET in s.getvalue())
emit("REDACT_PLACEHOLDERS", s.getvalue().count("***redacted***"))

# the same filter attached to the LOGGER, and a record arriving from a child
logger, s = redacted_text(on_logger=True)
child = logging.getLogger("t.redact.logger.child")
child.handlers.clear(); child.filters.clear(); child.propagate = True
child.info("key %s", SECRET)
lines = s.getvalue().splitlines()
emit("LOGGER_FILTER_DIRECT_LEAKS", SECRET in lines[0])
emit("LOGGER_FILTER_CHILD_LEAKS", SECRET in lines[-1])

# a secret inside an exception message survives a filter, and does not
# survive a formatter that scrubs the finished line
class ScrubbingJsonFormatter(JsonFormatter):
    def __init__(self, secrets, **kwargs):
        super().__init__(**kwargs)
        self.redactor = RedactingFilter(secrets)
    def format(self, record):
        return self.redactor.scrub(super().format(record))

for label, formatter in (("FILTERONLY", JsonFormatter()),
                         ("SCRUBBED", ScrubbingJsonFormatter([SECRET]))):
    logger = logging.getLogger(f"t.exc.{label}")
    logger.handlers.clear(); logger.filters.clear()
    logger.propagate = False; logger.setLevel(logging.DEBUG)
    h, s = buffer_handler(logging.DEBUG, formatter)
    h.addFilter(RedactingFilter([SECRET]))
    logger.addHandler(h)
    try:
        raise RuntimeError(f"upstream rejected key {SECRET}")
    except RuntimeError:
        logger.exception("request failed")
    emit(f"TRACEBACK_{label}_LEAKS", SECRET in s.getvalue())

# --- configuration: four layers -------------------------------------------
cfg = lab / "examples" / "config.toml"
steps = [
    ([], {}, None),
    ([], {}, cfg),
    ([], {"APP_BATCH_SIZE": "128"}, cfg),
    (["--batch-size", "256"], {"APP_BATCH_SIZE": "128"}, cfg),
]
values, sources = [], []
for argv, environ, path in steps:
    c = resolve(APP_SPEC, argv=argv, environ=environ, config_path=path)
    values.append(c["batch_size"])
    sources.append(c.source_of("batch_size"))
emit("LAYER_VALUES", ",".join(str(v) for v in values))
emit("LAYER_SOURCES", ",".join(sources))

c = resolve(APP_SPEC, argv=["--batch-size", "256", "--log-level", "DEBUG"],
            environ={"APP_SEED": "7", "APP_API_KEY": SECRET}, config_path=cfg)
emit("PROV_TABLE", ",".join(f"{n}={r.source}" for n, r in c.settings.items()))
emit("PROV_TABLE_LEAKS", SECRET in c.provenance_table())
emit("SAFE_DICT_LEAKS", SECRET in json.dumps(c.safe_dict()))
emit("SAFE_DICT_KEY", c.safe_dict()["api_key"])
emit("AS_DICT_HAS_SECRET", c.as_dict()["api_key"] == SECRET)

# TOML types survive
c = resolve(APP_SPEC, argv=[], environ={}, config_path=cfg)
emit("TOML_TYPES", f"{type(c['batch_size']).__name__},{type(c['dry_run']).__name__}")

# --- missing against empty -------------------------------------------------
unset = resolve(APP_SPEC, argv=[], environ={}, config_path=cfg)
empty = resolve(APP_SPEC, argv=[], environ={"APP_MODEL_NAME": ""}, config_path=cfg)
given = resolve(APP_SPEC, argv=[], environ={"APP_MODEL_NAME": "large"}, config_path=cfg)
emit("EMPTY_TRIPLE", "|".join([
    f"{unset['model_name']}:{unset.source_of('model_name')}",
    f"{empty['model_name']}:{empty.source_of('model_name')}",
    f"{given['model_name']}:{given.source_of('model_name')}",
]))
try:
    resolve(APP_SPEC, argv=[], environ={"APP_BATCH_SIZE": ""})
    emit("EMPTY_INT_REFUSED", False)
except ConfigError as error:
    emit("EMPTY_INT_REFUSED", "APP_BATCH_SIZE" in str(error))

# --- bool conversion -------------------------------------------------------
emit("BOOL_NAIVE", bool("false"))
emit("BOOL_TRUE_WORDS", ",".join(str(appconfig.to_bool(t)) for t in
                                 ["true", "TRUE", " yes ", "1", "on"]))
emit("BOOL_FALSE_WORDS", ",".join(str(appconfig.to_bool(t)) for t in
                                  ["false", "FALSE", "no", "0", "off"]))
refused = 0
for text in ["maybe", "", "2", "y"]:
    try:
        appconfig.to_bool(text)
    except ValueError:
        refused += 1
emit("BOOL_REFUSED", refused)
c = resolve(APP_SPEC, argv=[], environ={"APP_DRY_RUN": "false"}, config_path=cfg)
emit("BOOL_FROM_ENV", c["dry_run"])

# --- validation ------------------------------------------------------------
bad = resolve(APP_SPEC, argv=["--batch-size", "0", "--log-level", "VERBOSE"],
              environ={"APP_SEED": "-1", "APP_API_KEY": SECRET}, config_path=cfg)
problems = validate(bad, APP_SPEC)
emit("VALIDATE_COUNT", len(problems))
emit("VALIDATE_NAMES_SETTING", all(p.split(":")[0] in
     {"log_level", "batch_size", "seed"} for p in problems))
emit("VALIDATE_NAMES_SOURCE", all(("flag:" in p or "env:" in p or "file:" in p
     or "default" in p) for p in problems))
emit("VALIDATE_LEAKS", SECRET in " ".join(problems))
good = resolve(APP_SPEC, argv=["--batch-size", "128"], environ={"APP_SEED": "7"},
               config_path=cfg)
emit("VALIDATE_GOOD", len(validate(good, APP_SPEC)))
try:
    validate_or_die(bad, APP_SPEC)
    emit("VALIDATE_DIED", False)
except ConfigError:
    emit("VALIDATE_DIED", True)

# --- 06_run_manifest.py, end to end ---------------------------------------
env = dict(os.environ)
env.update({"APP_API_KEY": SECRET, "APP_SEED": "7", "PYTHONDONTWRITEBYTECODE": "1"})
proc = subprocess.run(
    [sys.executable, str(lab / "examples" / "06_run_manifest.py")],
    capture_output=True, text=True, env=env, cwd=str(lab),
)
emit("MANIFEST_EXIT", proc.returncode)
lines = [line for line in proc.stdout.splitlines() if line.startswith("{")]
manifest = json.loads(lines[0])
emit("MANIFEST_EVENT", manifest["event"])
emit("MANIFEST_RUNID", manifest["run_id"])
emit("MANIFEST_SEED_SOURCE", manifest["provenance"]["seed"])
emit("MANIFEST_BATCH_SOURCE", manifest["provenance"]["batch_size"])
emit("MANIFEST_KEY", manifest["config"]["api_key"])
emit("MANIFEST_LEAKS", SECRET in proc.stdout or SECRET in proc.stderr)
emit("MANIFEST_LINES", len(lines))
emit("MANIFEST_FINAL_LOSS", json.loads(lines[-1])["final_loss"])
emit("MANIFEST_RUNIDS_ALL", len({json.loads(l)["run_id"] for l in lines}))

proc2 = subprocess.run(
    [sys.executable, str(lab / "examples" / "06_run_manifest.py"),
     "--seed", "7", "--batch-size", "64", "--model-name", "small-encoder",
     "--data-version", "2026-08-01"],
    capture_output=True, text=True, env=env, cwd=str(lab),
)
lines2 = [line for line in proc2.stdout.splitlines() if line.startswith("{")]
emit("MANIFEST_REPRODUCED",
     json.loads(lines2[-1])["final_loss"] == json.loads(lines[-1])["final_loss"])

proc3 = subprocess.run(
    [sys.executable, str(lab / "examples" / "06_run_manifest.py"), "--batch-size", "0"],
    capture_output=True, text=True, env=env, cwd=str(lab),
)
emit("MANIFEST_BAD_EXIT", proc3.returncode)
emit("MANIFEST_BAD_NAMES_SETTING", "batch_size" in proc3.stderr)
emit("MANIFEST_BAD_NAMES_SOURCE", "flag:--batch-size" in proc3.stderr)

for key, value in out.items():
    print(f"{key}={value}")
PY

if [ -s "${work}/facts.err" ]; then
  echo "the python half of the suite failed:"
  cat "${work}/facts.err"
  exit 1
fi

fact() { grep "^$1=" "${work}/facts.txt" | head -1 | cut -d= -f2-; }

# ---------------------------------------------------------------------------
echo
echo "1. The logging module behaves as the lesson claims"
# ---------------------------------------------------------------------------
check_eq "the two-level trap: 3 calls, logger at DEBUG, handler at WARNING -> 1 line" \
  "1" "$(fact TRAP_LINES)"
check_eq "and the line that survived is the warning" "kept" "$(fact TRAP_TEXT)"
check_eq "lowering the HANDLER's level lets the debug line out" \
  "now it comes out" "$(fact TRAP_FIXED)"
check_eq "propagation: one call, two handlers up the tree -> 2 lines" \
  "2" "$(fact PROP_TOTAL)"
check_eq "fix 1, propagate = False -> 1 line" "1" "$(fact PROP_FIX1)"
check_eq "fix 2, handlers in one place only -> 1 line" "1" "$(fact PROP_FIX2)"

# ---------------------------------------------------------------------------
echo
echo "2. exception() keeps what error(str(e)) throws away"
# ---------------------------------------------------------------------------
check_eq "log.error(str(e)) produces no traceback" "False" "$(fact ERRSTR_HAS_TRACEBACK)"
check_eq "log.error(str(e)) is one line" "1" "$(fact ERRSTR_LINES)"
check_eq "log.exception() attaches the traceback" "True" "$(fact EXC_HAS_TRACEBACK)"
check_eq "the traceback names the exception type" "True" "$(fact EXC_NAMES_TYPE)"
check_eq "the traceback names the failing call" "True" "$(fact EXC_NAMES_FUNCTION)"

# ---------------------------------------------------------------------------
echo
echo "3. Lazy formatting renders nothing for a suppressed record"
# ---------------------------------------------------------------------------
check_eq "100 suppressed DEBUG calls, %s formatting -> 0 renders" \
  "0" "$(fact LAZY_RENDERS)"
check_eq "100 suppressed DEBUG calls, f-string -> 100 renders" \
  "100" "$(fact EAGER_RENDERS)"

# ---------------------------------------------------------------------------
echo
echo "4. The JSON formatter produces parseable objects with real fields"
# ---------------------------------------------------------------------------
check_eq "three calls produced three JSON objects" "3" "$(fact JSON_COUNT)"
check_eq "event is the formatted message" "batch complete" "$(fact JSON_FIRST_EVENT)"
check_eq "level is the NAME, not the number" "INFO" "$(fact JSON_FIRST_LEVEL)"
check_eq "the logger's name is carried" "t.json" "$(fact JSON_LOGGER)"
check_eq "run_id is stamped on every line by the formatter" \
  "run-4711" "$(fact JSON_FIRST_RUNID)"
check_eq "a field passed through extra= survives as a field" "61" "$(fact JSON_FIRST_KEPT)"
check_eq "the exception's type is its own field" "ValueError" "$(fact JSON_EXC_TYPE)"
check_eq "the traceback is its own field, not glued to the message" \
  "True" "$(fact JSON_HAS_TRACEBACK_FIELD)"
check_eq "ts is ISO 8601 UTC to milliseconds" "True" "$(fact JSON_TS_SHAPE)"
check_eq "ts sorts chronologically as plain text" "True" "$(fact JSON_TS_SORTS)"
check_eq "iso_utc(0) is the Unix epoch in UTC" \
  "1970-01-01T00:00:00.000Z" "$(fact ISO_UTC_ZERO)"

# ---------------------------------------------------------------------------
echo
echo "5. The secret does not reach the log"
# ---------------------------------------------------------------------------
check_eq "with the filter on the handler, the secret appears NOWHERE" \
  "False" "$(fact REDACT_SECRET_PRESENT)"
check_eq "and four routes were redacted: message, args, nested dict, list" \
  "4" "$(fact REDACT_PLACEHOLDERS)"
check_eq "a filter on the LOGGER protects a direct call" \
  "False" "$(fact LOGGER_FILTER_DIRECT_LEAKS)"
check_eq "and DOES NOT protect a record propagating from a child logger" \
  "True" "$(fact LOGGER_FILTER_CHILD_LEAKS)"
check_eq "a secret inside an exception message survives a filter" \
  "True" "$(fact TRACEBACK_FILTERONLY_LEAKS)"
check_eq "and does not survive a formatter that scrubs the finished line" \
  "False" "$(fact TRACEBACK_SCRUBBED_LEAKS)"

# ---------------------------------------------------------------------------
echo
echo "6. Configuration: four layers, in order, each one overriding the last"
# ---------------------------------------------------------------------------
check_eq "default 32, file 64, environment 128, flag 256" \
  "32,64,128,256" "$(fact LAYER_VALUES)"
check_eq "and each value reports the layer it came from" \
  "default,file:config.toml,env:APP_BATCH_SIZE,flag:--batch-size" \
  "$(fact LAYER_SOURCES)"
check_eq "seven settings, five different provenances" \
  "log_level=flag:--log-level,batch_size=flag:--batch-size,model_name=file:config.toml,seed=env:APP_SEED,dry_run=file:config.toml,data_version=file:config.toml,api_key=env:APP_API_KEY" \
  "$(fact PROV_TABLE)"
check_eq "TOML has real types: no conversion needed for int or bool" \
  "int,bool" "$(fact TOML_TYPES)"

# ---------------------------------------------------------------------------
echo
echo "7. Missing and empty are different, and strings are not types"
# ---------------------------------------------------------------------------
check_eq "unset falls through; empty is a value; set is a value" \
  "small-encoder:file:config.toml|:env:APP_MODEL_NAME (set but empty)|large:env:APP_MODEL_NAME" \
  "$(fact EMPTY_TRIPLE)"
check_eq "an empty environment variable for an int setting is refused by name" \
  "True" "$(fact EMPTY_INT_REFUSED)"
check_eq "the trap: bool('false') is True" "True" "$(fact BOOL_NAIVE)"
check_eq "to_bool reads the true words" "True,True,True,True,True" \
  "$(fact BOOL_TRUE_WORDS)"
check_eq "to_bool reads the false words" "False,False,False,False,False" \
  "$(fact BOOL_FALSE_WORDS)"
check_eq "to_bool refuses all four ambiguous inputs" "4" "$(fact BOOL_REFUSED)"
check_eq "APP_DRY_RUN=false resolves to False, not True" "False" "$(fact BOOL_FROM_ENV)"

# ---------------------------------------------------------------------------
echo
echo "8. Startup validation, and the secret it must not print"
# ---------------------------------------------------------------------------
check_eq "three bad values are reported all at once" "3" "$(fact VALIDATE_COUNT)"
check_eq "every message names its setting" "True" "$(fact VALIDATE_NAMES_SETTING)"
check_eq "every message names the layer the value came from" \
  "True" "$(fact VALIDATE_NAMES_SOURCE)"
check_eq "no message contains the secret" "False" "$(fact VALIDATE_LEAKS)"
check_eq "a good configuration reports no problems" "0" "$(fact VALIDATE_GOOD)"
check_eq "validate_or_die raises on a bad configuration" "True" "$(fact VALIDATE_DIED)"
check_eq "the provenance table never prints the secret" "False" "$(fact PROV_TABLE_LEAKS)"
check_eq "safe_dict never contains the secret" "False" "$(fact SAFE_DICT_LEAKS)"
check_eq "safe_dict shows the placeholder instead" "***redacted***" "$(fact SAFE_DICT_KEY)"
check_eq "as_dict DOES carry the real value, because the program needs it" \
  "True" "$(fact AS_DICT_HAS_SECRET)"

# ---------------------------------------------------------------------------
echo
echo "9. The run manifest: a run reconstructable from its own log"
# ---------------------------------------------------------------------------
check_eq "06_run_manifest.py exits 0" "0" "$(fact MANIFEST_EXIT)"
check_eq "its first event is the manifest" "run started" "$(fact MANIFEST_EVENT)"
check_eq "every line carries one run_id" "1" "$(fact MANIFEST_RUNIDS_ALL)"
check_eq "the run id is on the manifest line" "run-4711" "$(fact MANIFEST_RUNID)"
check_eq "the manifest records where the seed came from" \
  "env:APP_SEED" "$(fact MANIFEST_SEED_SOURCE)"
check_eq "and where the batch size came from" \
  "file:config.toml" "$(fact MANIFEST_BATCH_SOURCE)"
check_eq "the manifest carries the placeholder, not the key" \
  "***redacted***" "$(fact MANIFEST_KEY)"
check_eq "the key appears in neither stdout nor stderr" "False" "$(fact MANIFEST_LEAKS)"
check_eq "six JSON events were logged" "6" "$(fact MANIFEST_LINES)"
check_eq "the final loss is deterministic for seed 7" \
  "0.506509" "$(fact MANIFEST_FINAL_LOSS)"
check_eq "re-running from the manifest reproduces the same final loss" \
  "True" "$(fact MANIFEST_REPRODUCED)"
check_eq "a bad configuration stops the program before it starts" \
  "2" "$(fact MANIFEST_BAD_EXIT)"
check_eq "and the refusal names the setting" "True" "$(fact MANIFEST_BAD_NAMES_SETTING)"
check_eq "and names the layer it came from" "True" "$(fact MANIFEST_BAD_NAMES_SOURCE)"

# ---------------------------------------------------------------------------
echo
echo "10. The demonstration scripts and the starter checker"
# ---------------------------------------------------------------------------
for script in 01_prints.py 02_logging_architecture.py 03_structured_logging.py \
              04_config_resolver.py 05_dictconfig_and_rotation.py; do
  (cd "${lab_dir}" && "${python_bin}" "examples/${script}" >"${work}/${script}.out" 2>&1)
  check "examples/${script} runs and exits 0" \
    "$([ $? -eq 0 ] && echo yes || echo no)"
done
check "05_dictconfig_and_rotation.py rotated the file into 4 generations" \
  "$(grep -q 'app.log.3' "${work}/05_dictconfig_and_rotation.py.out" && echo yes || echo no)"
check "05 shows a TimedRotatingFileHandler rollover" \
  "$(grep -q 'files after one rollover: 2' "${work}/05_dictconfig_and_rotation.py.out" \
     && echo yes || echo no)"
check "01_prints.py really does print the API key, which is the point" \
  "$(grep -q 'sk-live-9f2c4a7b1e63' "${work}/01_prints.py.out" && echo yes || echo no)"
check "no demonstration script leaves an absolute home path in its output" \
  "$(grep -l '/Users/\|/home/' "${work}"/*.out >/dev/null 2>&1 && echo no || echo yes)"

(cd "${lab_dir}" && bash starter/03_check.sh >"${work}/starter-before.txt" 2>&1)
before_status=$?
check_eq "the untouched starter reports 0 of 12" "0 of 12 exercises complete." \
  "$(grep 'exercises complete' "${work}/starter-before.txt")"
check_eq "and exits non-zero" "1" "${before_status}"

(cd "${lab_dir}" && bash starter/03_check.sh examples/07_solution_logging.py \
   examples/08_solution_config.py >"${work}/starter-after.txt" 2>&1)
after_status=$?
check_eq "the reference answers report 12 of 12" "12 of 12 exercises complete." \
  "$(grep 'exercises complete' "${work}/starter-after.txt")"
check_eq "and exit 0" "0" "${after_status}"

# The checker must be able to FAIL. Break one reference answer on purpose and
# confirm the count drops — a checker that always says 12 is worth nothing.
cp "${lab_dir}/examples/applog.py" "${lab_dir}/examples/appconfig.py" "${work}/"
sed 's/logger.exception("could not parse batch size")/logger.error("could not parse batch size")/' \
  "${lab_dir}/examples/07_solution_logging.py" > "${work}/broken_logging.py"
(cd "${lab_dir}" && bash starter/03_check.sh "${work}/broken_logging.py" \
   examples/08_solution_config.py >"${work}/starter-broken.txt" 2>&1)
check_eq "with exception() replaced by error(), the checker catches it" \
  "11 of 12 exercises complete." \
  "$(grep 'exercises complete' "${work}/starter-broken.txt")"

# ---------------------------------------------------------------------------
echo
echo "11. Hygiene: offline, no sudo, no leaked paths, nothing left behind"
# ---------------------------------------------------------------------------
"${python_bin}" - "${lab_dir}" > "${work}/hygiene.txt" <<'PY'
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
urls, sudo_lines = set(), []
comment = re.compile(r"^\s*#")
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.suffix not in {".py", ".sh", ".toml"}:
        continue
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
    ):
        urls.update(re.findall(r"https?://[^\s\"')]+", line))
        if re.search(r"(^|[;|&(]\s*)sudo\s", line) and not comment.match(line):
            sudo_lines.append(f"{path.name}:{number}")
print("URLS " + " ".join(sorted(urls)))
print("SUDO " + " ".join(sudo_lines))
PY
check_eq "no URL appears anywhere in the lab's scripts" "URLS" \
  "$(grep '^URLS ' "${work}/hygiene.txt" | sed 's/ *$//')"
check_eq "no line in this lab would actually invoke sudo" "SUDO" \
  "$(grep '^SUDO ' "${work}/hygiene.txt" | sed 's/ *$//')"
check "nothing in this lab imports a networking module" \
  "$(grep -rlE '^\s*(import|from)\s+(socket|urllib|http|requests)' \
     "${lab_dir}/examples" "${lab_dir}/starter" >/dev/null 2>&1 && echo no || echo yes)"
check "no captured output leaks an absolute home path" \
  "$(grep -rl '/Users/\|/home/' "${lab_dir}/expected-output" >/dev/null 2>&1 \
     && echo no || echo yes)"
check "this suite left no log file in the lab directory" \
  "$([ ! -e "${lab_dir}/app.log" ] && [ ! -e "${lab_dir}/daily.log" ] \
     && [ ! -e "${lab_dir}/starter/app.log" ] && echo yes || echo no)"
check "this suite left no __pycache__ behind" \
  "$(find "${lab_dir}" -type d -name __pycache__ | grep -q . && echo no || echo yes)"

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
