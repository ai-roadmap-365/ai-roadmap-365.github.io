#!/usr/bin/env python3
"""The two halves joined: a run that can be reconstructed from its own record.

    python3 examples/06_run_manifest.py
    python3 examples/06_run_manifest.py --seed 11 --batch-size 128 --run-id run-4712

A training run you cannot reconstruct is an anecdote, not a result. This
script is the smallest honest version of the thing that makes a run
reproducible:

    * the CONFIGURATION is resolved through the four layers, and every value
      knows which layer it came from
    * the MANIFEST — model, data version, seed, batch size, and the
      provenance of each — is written into the log as the first event, so
      the log answers "what was this run actually configured with?" without
      anybody having to remember
    * the RUN LOG is JSON with a run_id on every line, so two runs of the
      same program are separable
    * the API KEY is present in the configuration, used by the program, and
      appears in neither the manifest nor any log line

Nothing here trains anything. The arithmetic is a deterministic stand-in, so
that the same seed produces the same numbers and you can see for yourself
that the log is enough to reproduce the run.
"""

from __future__ import annotations

import json
import logging
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from appconfig import APP_SPEC, ConfigError, resolve, validate_or_die  # noqa: E402
from applog import JsonFormatter, RedactingFilter  # noqa: E402

CONFIG_FILE = Path(__file__).resolve().parent / "config.toml"


def configure_logging(run_id: str, level: str, secrets: list[str]) -> logging.Logger:
    """One JSON handler on stdout, with the run id stamped on every line.

    stdout, not a file. Whatever supervises this process — a scheduler, a
    container runtime, a CI job — already collects stdout and already has a
    retention policy. Writing a file here would mean owning rotation, disk
    space and cleanup for no benefit. Day 81 and Day 84 both landed on this.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(static_fields={"run_id": run_id}))
    # On the HANDLER. A filter on a logger is skipped by every record that
    # propagates up from a child logger, which is every module in the program.
    handler.addFilter(RedactingFilter(secrets))

    logger = logging.getLogger("run")
    logger.handlers.clear()
    logger.filters.clear()
    logger.setLevel(getattr(logging, level))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def fake_step(rng: random.Random, step: int) -> float:
    """A deterministic stand-in for a training step. Same seed, same numbers."""
    return round(2.0 / (step + 1) + rng.random() * 0.01, 6)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    # The run id is configuration too, and it defaults to something fixed here
    # so the captured output is reproducible. In a real job it would be the
    # scheduler's job id, the CI run number, or a uuid4 — anything that is
    # unique and that you can paste into a search box.
    run_id = "run-4711"
    if "--run-id" in argv:
        index = argv.index("--run-id")
        run_id = argv[index + 1]
        argv = argv[:index] + argv[index + 2:]

    try:
        config = resolve(APP_SPEC, argv=argv, config_path=CONFIG_FILE)
        validate_or_die(config, APP_SPEC)
    except ConfigError as error:
        # Configuration failures are reported before logging is configured,
        # on stderr, and the process stops. There is nothing useful to do
        # with a program that does not know what it is meant to do.
        print(f"configuration error:\n{error}", file=sys.stderr)
        return 2

    secrets = [config["api_key"]] if config["api_key"] else []
    log = configure_logging(run_id, config["log_level"], secrets)

    # THE MANIFEST. First line of the run, and the reason the run is
    # reconstructable. Note safe_dict(): api_key is in the configuration and
    # is not in this event.
    log.info(
        "run started",
        extra={
            "config": config.safe_dict(),
            "provenance": {name: r.source for name, r in config.settings.items()},
        },
    )

    rng = random.Random(config["seed"])
    losses = []
    for step in range(1, 4):
        loss = fake_step(rng, step)
        losses.append(loss)
        log.info("step complete", extra={"step": step, "loss": loss})

    if config["dry_run"]:
        log.warning("dry run: nothing was written", extra={"artifact": None})
    else:
        log.info("artifact written", extra={"artifact": f"{config['model_name']}.bin"})

    log.info("run finished", extra={"steps": len(losses), "final_loss": losses[-1]})

    # The plain-language summary goes to stderr so that stdout stays a clean
    # stream of JSON objects. Two streams, two audiences, no interleaving.
    print("", file=sys.stderr)
    print("--- the same run, as a person would read it (stderr) ---", file=sys.stderr)
    print(f"run {run_id}: model={config['model_name']} "
          f"data={config['data_version']} seed={config['seed']} "
          f"batch={config['batch_size']}", file=sys.stderr)
    print(f"  final loss {losses[-1]}", file=sys.stderr)
    print(f"  api_key configured: {bool(config['api_key'])} "
          f"(value never printed, never logged)", file=sys.stderr)
    print("", file=sys.stderr)
    print("To repeat this run exactly, read the manifest out of its own log:",
          file=sys.stderr)
    print("  python3 examples/06_run_manifest.py \\", file=sys.stderr)
    print(f"      --seed {config['seed']} --batch-size {config['batch_size']} \\",
          file=sys.stderr)
    print(f"      --model-name {config['model_name']} "
          f"--data-version {config['data_version']}", file=sys.stderr)
    print("", file=sys.stderr)
    print("That command is derivable from the log because the log recorded the",
          file=sys.stderr)
    print("configuration. If it had not, the honest answer to 'what produced",
          file=sys.stderr)
    print("this number?' would be 'nobody knows', and the number would be an",
          file=sys.stderr)
    print("anecdote rather than a result.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
