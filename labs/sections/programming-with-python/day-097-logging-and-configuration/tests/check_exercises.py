#!/usr/bin/env python3
"""Check the twelve exercises by RUNNING them and looking at the values.

Usage (normally through starter/03_check.sh):

    python3 tests/check_exercises.py LOGGING_FILE CONFIG_FILE

It never reads how you wrote something. It imports your two files, calls your
functions, captures log output into a buffer, and compares real values — so
any correct implementation passes and a plausible-looking wrong one does not.

Prints one line per exercise and a final "N of 12 exercises complete.".
Exit status is 0 only when N is 12.
"""

from __future__ import annotations

import importlib.util
import io
import json
import logging
import sys
import tempfile
from pathlib import Path

SECRET = "sk-live-9f2c4a7b1e63"  # invented for this lab; not a real credential

# When a handler or formatter raises, the logging module prints the traceback
# to stderr and carries on — deliberately, because a logging failure must not
# take the program down with it. While the exercises are unfinished that
# happens on every call, so the checker's own output would be buried. Turning
# raiseExceptions off silences it; the checker reports the failure itself.
logging.raiseExceptions = False

results: list[tuple[int, str, bool, str]] = []


def record(number: int, title: str, ok: bool, detail: str = "") -> None:
    results.append((number, title, ok, detail))


def load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def capture(logger_name: str, formatter: logging.Formatter, filters=()):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    for f in filters:
        handler.addFilter(f)
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)
    return logger, stream


class Collector(logging.Handler):
    """Keeps the LogRecord objects themselves, not their rendered text."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


# ---------------------------------------------------------------------------
# Exercises 1-6
# ---------------------------------------------------------------------------


def check_logging(path: Path) -> None:
    try:
        mod = load(path, "starter_logging")
    except Exception as error:  # noqa: BLE001
        for number in range(1, 7):
            record(number, "(module did not import)", False, f"{type(error).__name__}: {error}")
        return

    # 1 --------------------------------------------------------------------
    try:
        ok = (
            isinstance(mod.log, logging.Logger)
            and mod.log.name == mod.__name__
            and mod.log is logging.getLogger(mod.__name__)
        )
        detail = f"log = {mod.log!r}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(1, "a module logger from logging.getLogger(__name__)", ok, detail)

    # 2 --------------------------------------------------------------------
    try:
        collector = Collector()
        logger = logging.getLogger("check.prepare")
        logger.handlers.clear()
        logger.filters.clear()
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(collector)

        kept = mod.prepare(mod.RECORDS, logger)
        levels = [r.levelname for r in collector.records]
        messages = [r.getMessage() for r in collector.records]
        done = [r for r in collector.records if "preparation done" in r.getMessage()]

        ok = (
            len(kept) == 4
            and levels.count("INFO") == 2
            and levels.count("WARNING") == 2
            and levels.count("DEBUG") == 6
            and any("kept 4 of 6" in m for m in messages)
            and SECRET not in " ".join(messages)
            and bool(done)
            and "%" in str(done[0].msg)       # lazy formatting, not an f-string
            and bool(done[0].args)
        )
        detail = f"returned {len(kept)} records; levels {levels}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(2, "prepare() logs at the right levels and returns its result", ok, detail)

    # 3 --------------------------------------------------------------------
    try:
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.WARNING)          # deliberately too high
        handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger = mod.make_debug_logger("check.two_level", handler)
        logger.debug("a debug line")
        text = stream.getvalue()
        ok = (
            logger.level == logging.DEBUG
            and logger.propagate is False
            and len(logger.handlers) == 1
            and "a debug line" in text
        )
        detail = f"logger={logging.getLevelName(logger.level)} " \
                 f"handler={logging.getLevelName(logger.handlers[0].level)} " \
                 f"output={text.strip()!r}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(3, "the two-level trap: a DEBUG call actually comes out", ok, detail)

    # 4 --------------------------------------------------------------------
    try:
        collector = Collector()
        logger = logging.getLogger("check.exception")
        logger.handlers.clear()
        logger.filters.clear()
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(collector)

        bad = mod.log_parse_failure("sixty-four", logger)
        good = mod.log_parse_failure("64", logger)
        failure = collector.records[0]
        rendered = logging.Formatter("%(message)s").format(failure)
        ok = (
            bad is False
            and good is True
            and len(collector.records) == 1
            and failure.levelname == "ERROR"
            and failure.exc_info is not None
            and "Traceback" in rendered
            and "ValueError" in rendered
        )
        detail = f"exc_info={'present' if failure.exc_info else 'MISSING'}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(4, "a failure logged with exception(), traceback attached", ok, detail)

    # 5 --------------------------------------------------------------------
    try:
        formatter = mod.JsonFormatter({"run_id": "run-1"})
        logger, stream = capture("check.json", formatter)
        logger.info("batch complete", extra={"batch": 2, "kept": 61})
        payload = json.loads(stream.getvalue().strip())
        ok = (
            payload["level"] == "INFO"
            and payload["logger"] == "check.json"
            and payload["event"] == "batch complete"
            and payload["run_id"] == "run-1"
            and payload["batch"] == 2
            and payload["kept"] == 61
            and payload["ts"].endswith("Z")
            and payload["ts"][4] == "-"
            and "args" not in payload
        )
        detail = f"parsed keys {sorted(payload)}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(5, "a JSON formatter with ts, level, logger, event and extras", ok, detail)

    # 6 --------------------------------------------------------------------
    try:
        formatter = mod.JsonFormatter({"run_id": "run-1"})
        logger, stream = capture(
            "check.redact", formatter, filters=[mod.RedactingFilter([SECRET])]
        )
        logger.info("calling upstream with key %s", SECRET)
        logger.info(f"in the message: {SECRET}")
        logger.info("config", extra={"headers": {"Authorization": f"Bearer {SECRET}"}})
        text = stream.getvalue()
        ok = SECRET not in text and text.count(mod.RedactingFilter.PLACEHOLDER) >= 3
        detail = ("the secret appears in the captured log" if SECRET in text
                  else "the secret appears nowhere in the captured log")
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(6, "a redacting filter: the secret reaches no handler", ok, detail)


# ---------------------------------------------------------------------------
# Exercises 7-12
# ---------------------------------------------------------------------------

TOML_TEXT = 'batch_size = 64\nmodel_name = "small-encoder"\ndry_run = false\n'


def check_config(path: Path) -> None:
    try:
        mod = load(path, "starter_config")
    except Exception as error:  # noqa: BLE001
        for number in range(7, 13):
            record(number, "(module did not import)", False, f"{type(error).__name__}: {error}")
        return

    work = Path(tempfile.mkdtemp(prefix="day097-check-"))
    toml_path = work / "config.toml"
    toml_path.write_text(TOML_TEXT, encoding="utf-8")

    # 7 --------------------------------------------------------------------
    try:
        truthy = all(mod.to_bool(t) is True for t in ["true", "TRUE", " yes ", "1", "on"])
        falsey = all(mod.to_bool(t) is False for t in ["false", "FALSE", "no", "0", "off"])
        refused = 0
        for text in ["maybe", "", "2", "y"]:
            try:
                mod.to_bool(text)
            except ValueError:
                refused += 1
        ok = truthy and falsey and refused == 4
        detail = f"truthy={truthy} falsey={falsey} refused {refused} of 4"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(7, "to_bool refuses to believe that 'false' is true", ok, detail)

    # 8 --------------------------------------------------------------------
    try:
        table, name = mod.load_toml(toml_path)
        empty, none_name = mod.load_toml(work / "does-not-exist.toml")
        missing, _ = mod.load_toml(None)
        ok = (
            table["batch_size"] == 64
            and isinstance(table["batch_size"], int)
            and table["dry_run"] is False
            and name == "config.toml"
            and empty == {} and none_name is None
            and missing == {}
        )
        detail = f"read {sorted(table)} from {name!r}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(8, "load_toml reads a TOML file and tolerates a missing one", ok, detail)

    # 9 --------------------------------------------------------------------
    try:
        steps = [
            ([], {}, None, 32),
            ([], {}, toml_path, 64),
            ([], {"APP_BATCH_SIZE": "128"}, toml_path, 128),
            (["--batch-size", "256"], {"APP_BATCH_SIZE": "128"}, toml_path, 256),
        ]
        seen = []
        for argv, environ, cfg, expected in steps:
            config = mod.resolve(mod.SPEC, argv=argv, environ=environ, config_path=cfg)
            seen.append((config["batch_size"], expected))
        ok = all(actual == expected for actual, expected in seen)
        detail = " -> ".join(str(actual) for actual, _ in seen)
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(9, "four layers: default, file, environment, flag — the flag wins", ok, detail)

    # 10 -------------------------------------------------------------------
    try:
        unset = mod.resolve(mod.SPEC, argv=[], environ={}, config_path=toml_path)
        empty = mod.resolve(
            mod.SPEC, argv=[], environ={"APP_MODEL_NAME": ""}, config_path=toml_path
        )
        given = mod.resolve(
            mod.SPEC, argv=[], environ={"APP_MODEL_NAME": "large"}, config_path=toml_path
        )
        int_empty_refused = False
        try:
            mod.resolve(mod.SPEC, argv=[], environ={"APP_BATCH_SIZE": ""})
        except mod.ConfigError as error:
            int_empty_refused = "APP_BATCH_SIZE" in str(error)

        ok = (
            unset["model_name"] == "small-encoder"
            and unset.source_of("model_name").startswith("file:")
            and empty["model_name"] == ""
            and "empty" in empty.source_of("model_name")
            and given["model_name"] == "large"
            and given.source_of("model_name") == "env:APP_MODEL_NAME"
            and int_empty_refused
        )
        detail = (f"unset -> {unset.source_of('model_name')}; "
                  f"empty -> {empty.source_of('model_name')}")
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(10, "a missing environment variable and an empty one differ", ok, detail)

    # 11 -------------------------------------------------------------------
    try:
        config = mod.resolve(
            mod.SPEC,
            argv=["--batch-size", "256"],
            environ={"APP_API_KEY": SECRET, "APP_LOG_LEVEL": "DEBUG"},
            config_path=toml_path,
        )
        sources = {name: config.source_of(name) for name in
                   ("log_level", "batch_size", "model_name", "dry_run", "api_key")}
        ok = (
            sources["log_level"] == "env:APP_LOG_LEVEL"
            and sources["batch_size"] == "flag:--batch-size"
            and sources["model_name"] == "file:config.toml"
            and sources["dry_run"] == "file:config.toml"
            and sources["api_key"] == "env:APP_API_KEY"
        )
        detail = str(sources)
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(11, "every value reports the layer it came from", ok, detail)

    # 12 -------------------------------------------------------------------
    try:
        bad = mod.resolve(
            mod.SPEC,
            argv=["--batch-size", "0", "--log-level", "VERBOSE"],
            environ={"APP_API_KEY": SECRET},
            config_path=toml_path,
        )
        problems = mod.validate(bad, mod.SPEC)
        joined = " | ".join(problems)
        good = mod.resolve(mod.SPEC, argv=["--batch-size", "128"], environ={},
                           config_path=toml_path)
        safe = mod.safe_dict(bad)

        ok = (
            len(problems) == 2
            and any("batch_size" in p and "flag:--batch-size" in p for p in problems)
            and any("log_level" in p and "flag:--log-level" in p for p in problems)
            and SECRET not in joined
            and mod.validate(good, mod.SPEC) == []
            and safe["api_key"] == "***redacted***"
            and safe["batch_size"] == 0
            and SECRET not in json.dumps(safe)
        )
        detail = f"{len(problems)} problems: {joined}"
    except Exception as error:  # noqa: BLE001
        ok, detail = False, f"{type(error).__name__}: {error}"
    record(12, "startup validation names the setting and its provenance", ok, detail)

    for leftover in sorted(work.iterdir()):
        leftover.unlink()
    work.rmdir()


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_exercises.py LOGGING_FILE CONFIG_FILE", file=sys.stderr)
        return 2
    logging_file, config_file = Path(sys.argv[1]), Path(sys.argv[2])
    sys.path.insert(0, str(logging_file.resolve().parent))

    check_logging(logging_file)
    check_config(config_file)

    passed = 0
    for number, title, ok, detail in sorted(results):
        if ok:
            passed += 1
            print(f"  {number:>2}. ok       {title}")
        else:
            print(f"  {number:>2}. not yet  {title}")
            if detail:
                print(f"          {detail}")
    print()
    print(f"{passed} of 12 exercises complete.")
    return 0 if passed == 12 else 1


if __name__ == "__main__":
    raise SystemExit(main())
