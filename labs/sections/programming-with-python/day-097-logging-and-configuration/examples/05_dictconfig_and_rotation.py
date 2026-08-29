#!/usr/bin/env python3
"""dictConfig, two handlers with two formatters, and file rotation.

    python3 examples/05_dictconfig_and_rotation.py [WORKDIR]

Three things:

    1. `logging.config.dictConfig` — the configuration form worth knowing,
       because it puts the whole logging setup in ONE dictionary that can
       itself come from a config file, which is the point of the day
    2. `RotatingFileHandler` and `TimedRotatingFileHandler`, demonstrated
       until they actually rotate
    3. the honest note: for a service, stdout plus a supervisor is usually
       the better answer, and Day 81 and Day 84 both argued this already

If WORKDIR is not given the script makes a temporary directory and removes it
on the way out, so it leaves nothing behind.
"""

from __future__ import annotations

import json
import logging
import logging.config
import logging.handlers
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

RUN_ID = "run-4711"
API_KEY = "sk-live-9f2c4a7b1e63"  # invented for this lab; not a real credential


def banner(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def build_dict_config(log_dir: Path, level: str) -> dict:
    """The whole logging setup as one dictionary.

    Read it top to bottom: it is the four objects of the logging module,
    written out as four sections. Formatters render. Filters decide and edit.
    Handlers send somewhere, each with its own level and its own formatter.
    Loggers are named and say which handlers they use.

    `disable_existing_loggers` is the setting nobody reads and everybody is
    bitten by. It defaults to True, which silences every logger that already
    existed when this call is made — including the ones created at import
    time by libraries you depend on. Set it to False unless you specifically
    want that.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # For a person, on a terminal.
            "console": {
                "format": "%(asctime)s %(levelname)-8s %(name)-14s %(message)s",
                "datefmt": "%H:%M:%S",
            },
            # For a machine, in a file. Same records, different rendering:
            # the formatter belongs to the handler, not to the record.
            "json": {
                "()": "applog.JsonFormatter",
                "static_fields": {"run_id": RUN_ID},
            },
        },
        "filters": {
            "redact": {
                "()": "applog.RedactingFilter",
                "secrets": [API_KEY],
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",           # people want the summary
                "formatter": "console",
                "filters": ["redact"],
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",          # the file keeps everything
                "formatter": "json",
                "filters": ["redact"],
                "filename": str(log_dir / "app.log"),
                "maxBytes": 900,           # absurdly small, to force rotation
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "app": {
                "level": level,            # the LOGGER's level: the first gate
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {"level": "WARNING", "handlers": ["console"]},
    }


def demo_dictconfig(log_dir: Path) -> logging.Logger:
    banner("1. dictConfig: the whole setup in one dictionary")

    config = build_dict_config(log_dir, level="DEBUG")
    logging.config.dictConfig(config)
    log = logging.getLogger("app.prepare")

    print("Configured. One logger, two handlers, two formatters, one filter.")
    print("Watch the SAME five calls produce two different renderings.")
    print()
    print("--- what the console handler prints (level INFO, human format) ---")
    log.debug("cache hit for shard 3")
    log.info("run started")
    log.info("batch complete", extra={"batch": 1, "kept": 61})
    log.warning("upstream slow", extra={"status": 429})
    log.info("using key %s", API_KEY)
    print()

    lines = (log_dir / "app.log").read_text(encoding="utf-8").splitlines()
    print("--- what the file handler wrote (level DEBUG, JSON) ---")
    for line in lines:
        print(f"  {line}")
    print()
    print(f"console saw 4 of the 5 calls; the file has {len(lines)} of them.")
    print("The DEBUG line was accepted by the logger, rejected by the console")
    print("handler and kept by the file handler — the two-level rule, with two")
    print("handlers disagreeing on purpose, which is what it is FOR.")
    print()
    key_in_file = API_KEY in (log_dir / "app.log").read_text(encoding="utf-8")
    print(f"the secret appears in the file: {key_in_file}")
    print("The redacting filter is listed on BOTH handlers, which is the only")
    print("arrangement that actually works: a filter on the `app` logger would")
    print("be skipped by every record propagating up from `app.prepare`, and")
    print("both destinations would be leaking. Demonstration 03 measures that.")

    print()
    print("Why a dictionary rather than calls: this is DATA. It can be loaded")
    print("from the TOML file the rest of the configuration comes from, kept in")
    print("version control, diffed in review, and swapped per environment")
    print("without touching a line of Python. `logging.basicConfig` is the")
    print("convenience version of the same thing — one handler on the ROOT")
    print("logger, and nothing at all if the root already has one, which is")
    print("why calling it twice appears to do nothing the second time.")
    return log


def demo_rotation(log_dir: Path) -> None:
    banner("2. Rotation: what happens when the file gets big")

    log = logging.getLogger("app.rotate")
    # DEBUG, so these 40 lines go to the file and not to your terminal. The
    # console handler is at INFO; the file handler is at DEBUG.
    for index in range(40):
        log.debug("processing record", extra={"record": index})

    handler = logging.getLogger("app").handlers[1]
    handler.flush()

    files = sorted(p.name for p in log_dir.glob("app.log*"))
    print(f"maxBytes=900, backupCount=3. After 40 more records:")
    for name in files:
        path = log_dir / name
        print(f"  {name:<12} {path.stat().st_size:>6} bytes, "
              f"{len(path.read_text(encoding='utf-8').splitlines())} lines")
    print()
    print("`app.log` is always the live one. When it exceeds maxBytes it is")
    print("renamed to `app.log.1`, the old `.1` becomes `.2`, and the file")
    print("that would have become `.4` is DELETED — backupCount is how many")
    print("you keep, and everything past it is gone for good.")
    print()
    print("`TimedRotatingFileHandler` is the same idea keyed on the clock")
    print("rather than the size. Waiting for midnight is impractical in a")
    print("demonstration, so here it is with the rollover called by hand —")
    print("which is exactly what the handler does when the interval elapses:")

    timed = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_dir / "daily.log"), when="midnight", backupCount=7,
        encoding="utf-8",
    )
    timed.setFormatter(logging.Formatter("%(message)s"))
    timed_log = logging.getLogger("timed.demo")
    timed_log.handlers.clear()
    timed_log.propagate = False
    timed_log.setLevel(logging.INFO)
    timed_log.addHandler(timed)

    timed_log.info("yesterday's work")
    timed.doRollover()
    timed_log.info("today's work")
    timed.close()

    daily = sorted(p.name for p in log_dir.glob("daily.log*"))
    print(f"  files after one rollover: {len(daily)}")
    for name in daily:
        suffix = "the live file" if name == "daily.log" else "rolled, named by date"
        print(f"    {name:<24} {suffix}")
    print()
    print("Size-based rotation bounds your DISK; time-based rotation bounds")
    print("your SEARCH, because 'the log for Tuesday' is one file. Pick by")
    print("which of those two questions you ask more often. `backupCount=7`")
    print("with when='midnight' is a week of history and no more.")

    print()
    print("Now the honest part, and it is the same conclusion Day 81 reached")
    print("about scheduling and Day 84 reached about packaging.")
    print()
    print("For a long-running service, writing your own log files is usually")
    print("the WRONG default. Log to stdout, unformatted by any rotation")
    print("logic, and let the thing that already supervises your process")
    print("collect it — systemd's journal, a container runtime, a process")
    print("manager. Four reasons, none of them theoretical:")
    print()
    print("  * Rotation in-process is racy across processes. Two workers with")
    print("    RotatingFileHandler on the same file will rename it out from")
    print("    under each other. There is a documented recipe involving a")
    print("    socket handler and a single writer, and it exists because the")
    print("    simple thing does not work.")
    print("  * The supervisor already does it, uniformly, for every service on")
    print("    the machine, with one retention policy you can audit.")
    print("  * A container has no persistent disk to rotate onto anyway.")
    print("  * stdout composes. `your-app | grep ERROR` works; a file handler")
    print("    inside the process does not compose with anything.")
    print()
    print("When file rotation IS right: a scheduled job that runs on a machine")
    print("with a disk and no supervisor, a desktop application, or a")
    print("deliberately separate audit trail with its own retention rules.")
    print("Those are real cases. They are not the default.")


def demo_level_change(log_dir: Path) -> None:
    banner("3. Turning it down without editing code")

    print("The whole argument for logging over print, in one demonstration.")
    print("Same program, same calls, one configuration value changed:")
    print()
    for level in ("DEBUG", "INFO", "WARNING"):
        for path in log_dir.glob("app.log*"):
            path.unlink()
        logging.config.dictConfig(build_dict_config(log_dir, level=level))
        log = logging.getLogger("app.levels")
        log.debug("cache hit for shard 3")
        log.info("batch complete", extra={"batch": 1})
        log.warning("upstream slow", extra={"status": 429})
        logging.getLogger("app").handlers[1].flush()
        lines = (log_dir / "app.log").read_text(encoding="utf-8").splitlines()
        events = [json.loads(line)["event"] for line in lines]
        print(f"  logger level {level:<8} -> file has {len(lines)} lines: {events}")
    print()
    print("Three deployments, three answers, one unchanged program. With")
    print("print() the only way to get the first row is to edit the source and")
    print("ship it, and the only way to get back to the third is to edit it")
    print("again — which is exactly the change nobody wants to make while")
    print("something is broken.")


def main() -> None:
    if len(sys.argv) > 1:
        log_dir, temporary = Path(sys.argv[1]), False
        log_dir.mkdir(parents=True, exist_ok=True)
    else:
        log_dir, temporary = Path(tempfile.mkdtemp(prefix="day097-")), True

    try:
        demo_dictconfig(log_dir)
        demo_rotation(log_dir)
        demo_level_change(log_dir)
        print()
        print("=" * 70)
        print("dictConfig and rotation demonstration complete.")
        if temporary:
            print("(the log directory was temporary and has been removed)")
        else:
            print(f"(log files left in {log_dir.name}/ because you named a directory)")
    finally:
        logging.shutdown()
        if temporary:
            shutil.rmtree(log_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
