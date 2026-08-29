"""The command line: three subcommands over one shared core, plus the
scheduled entry point.

`feedkit fetch` does the work. `feedkit report` renders what has been
collected. `feedkit status` says when the last successful run was and whether
the toolkit has gone quiet. `feedkit-scheduled` is what the crontab, launchd
job or systemd timer invokes — the same fetch, with the settings a machine
wants rather than the settings a human wants.

Both entry points are declared in `pyproject.toml` under
`[project.scripts]`, which is what turns them into commands on PATH when the
package is installed. That is Day 83's mechanism doing the work Day 80's
argparse designed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from . import adapters, config as config_module, core, logging_setup, runner
from . import state as state_module

VERSION = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="feedkit",
        description=(
            "Collect entries from configured JSON sources, on a schedule, "
            "without processing anything twice."
        ),
        epilog=(
            "Settings resolve in this order, weakest first: defaults, "
            "configuration file, environment, flags. Run "
            "`feedkit status --explain-config` to see where each value came from. "
            "The access token is read from FEEDKIT_TOKEN and is never written to "
            "a file or a log."
        ),
    )
    # Global options are the CONFIGURATION SETTINGS — the fourth and strongest
    # layer of the precedence. Keeping them all on the main parser rather than
    # scattering them across subcommands means `--max-items` means the same
    # thing everywhere, and `status --explain-config` can show the effect of
    # any of them.
    parser.add_argument("--version", action="version", version=f"feedkit {VERSION}")
    parser.add_argument("--config", metavar="PATH", help="configuration file to read")
    parser.add_argument("--base-url", dest="base_url", help="root address of the source server")
    parser.add_argument("--log-level", dest="log_level", choices=sorted(logging_setup.LEVELS))
    parser.add_argument("--state-file", dest="state_file", metavar="PATH")
    parser.add_argument("--sources", help="comma-separated list, overriding the configuration")
    parser.add_argument(
        "--max-items",
        dest="max_items",
        type=int,
        metavar="N",
        help="most previously unseen entries to accept from one source in one run",
    )
    parser.add_argument("--retries", type=int, metavar="N", help="attempts per source")

    subcommands = parser.add_subparsers(dest="command", metavar="COMMAND")

    fetch = subcommands.add_parser("fetch", help="collect new entries from every source")
    fetch.add_argument(
        "--dry-run",
        action="store_true",
        help="do everything except write the state file, and say what would have changed",
    )

    report = subcommands.add_parser("report", help="show what has been collected")
    report.add_argument("--limit", dest="report_limit", type=int, metavar="N")

    status = subcommands.add_parser("status", help="show the last successful run")
    status.add_argument(
        "--max-age-minutes",
        dest="max_age_minutes",
        type=int,
        metavar="N",
        help="watchdog allowance; exit 3 when the last success is older than this",
    )
    status.add_argument(
        "--explain-config",
        action="store_true",
        help="print every setting, its value, and which layer it came from",
    )
    return parser


CONFIG_FLAGS = (
    "config",
    "base_url",
    "log_level",
    "state_file",
    "sources",
    "max_items",
    "retries",
    "report_limit",
    "max_age_minutes",
)


def flags_from(args: argparse.Namespace) -> dict[str, Any]:
    """Only the parsed arguments that are configuration settings, and only the
    ones actually supplied — argparse leaves the rest as None, and None is what
    tells the resolver 'this layer has no opinion'."""
    return {name: getattr(args, name, None) for name in CONFIG_FLAGS}


def main(argv: Sequence[str] | None = None, stdout: TextIO | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = stdout if stdout is not None else sys.stdout
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help(out)
        return core.EXIT_FATAL

    try:
        settings, config_path = config_module.load(flags_from(args))
    except config_module.ConfigError as exc:
        print(f"feedkit: configuration error: {exc}", file=sys.stderr)
        return core.EXIT_FATAL

    run_id = runner.new_run_id()
    logger = logging_setup.configure(
        settings.log_level,
        run_id=run_id,
        secrets=[settings.token] if settings.token else [],
        stream=out,
    )
    state_path = Path(settings.state_file).expanduser()
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")

    try:
        if args.command == "fetch":
            return _cmd_fetch(args, settings, state_path, lock_path, logger, out, run_id)
        if args.command == "report":
            return _cmd_report(settings, state_path, out)
        if args.command == "status":
            return _cmd_status(args, settings, config_path, state_path, out)
    except state_module.StateError as exc:
        print(f"feedkit: {exc}", file=sys.stderr)
        return core.EXIT_FATAL

    parser.print_help(out)
    return core.EXIT_FATAL


def _cmd_fetch(
    args: argparse.Namespace,
    settings: config_module.Config,
    state_path: Path,
    lock_path: Path,
    logger: Any,
    out: TextIO,
    run_id: str,
) -> int:
    session = adapters.build_session()
    try:
        fetcher = adapters.HttpFetcher(
            session=session,
            base_url=settings.base_url,
            token=settings.token,
            timeout=settings.timeout_seconds,
            retries=settings.retries,
            backoff_seconds=settings.backoff_seconds,
            logger=logger,
        )
        summary, code = runner.run_fetch(
            settings,
            fetcher,
            adapters.SystemClock(),
            state_path,
            lock_path,
            logger,
            dry_run=args.dry_run,
            run_id=run_id,
        )
    finally:
        session.close()

    print(core.format_summary(summary, run_id=run_id, dry_run=args.dry_run), file=out)
    return code


def _cmd_report(settings: config_module.Config, state_path: Path, out: TextIO) -> int:
    current = state_module.load(state_path)
    print(core.render_report(current, settings.report_limit), file=out)
    return core.EXIT_OK


def _cmd_status(
    args: argparse.Namespace,
    settings: config_module.Config,
    config_path: Path | None,
    state_path: Path,
    out: TextIO,
) -> int:
    if args.explain_config:
        print(config_module.explain(settings, config_path), file=out)
        return core.EXIT_OK

    current = state_module.load(state_path)
    text, stale = core.render_status(
        current, adapters.SystemClock().now_iso(), settings.max_age_seconds
    )
    print(text, file=out)
    # A watchdog is only useful if it can fail. Exiting non-zero on silence is
    # what lets a second, much simpler scheduled job page you when the first
    # one has stopped running at all.
    return core.EXIT_PARTIAL if stale else core.EXIT_OK


def scheduled_main(argv: Sequence[str] | None = None) -> int:
    """The entry point a scheduler invokes.

    It is a thin wrapper on purpose. The scheduled run wants a fetch, quieter
    logging by default, and no interactive help — everything else is identical,
    because a scheduled run that behaves differently from the one you tested by
    hand is a scheduled run you have not tested.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    return main(["--log-level", "info", "fetch", *argv])


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
