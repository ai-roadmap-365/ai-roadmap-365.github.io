#!/usr/bin/env python3
"""Reference answers to exercises 7-12. Read AFTER you have tried them.

Same public names as `starter/02_config.py`, so `starter/03_check.sh` can be
pointed at either one. The resolver itself lives in `examples/appconfig.py`;
this file supplies the names the checker looks for and the SPEC the starter
uses.
"""

from __future__ import annotations

import argparse  # noqa: F401  (kept to mirror the starter)
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from appconfig import (  # noqa: E402,F401
    FALSE_WORDS,
    TRUE_WORDS,
    Config,
    ConfigError,
    Resolved,
    Setting,
    build_parser,
    load_toml,
    resolve,
    to_bool,
    validate,
)

# The same five settings the starter file specifies.
SPEC: tuple[Setting, ...] = (
    Setting("log_level", "str", "INFO", env="APP_LOG_LEVEL", flag="--log-level",
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    Setting("batch_size", "int", 32, env="APP_BATCH_SIZE", flag="--batch-size",
            minimum=1, maximum=1024),
    Setting("model_name", "str", "tiny-baseline", env="APP_MODEL_NAME",
            flag="--model-name"),
    Setting("dry_run", "bool", False, env="APP_DRY_RUN", flag="--dry-run"),
    Setting("api_key", "str", "", env="APP_API_KEY", flag=None, secret=True),
)


def safe_dict(config: Config) -> dict[str, Any]:
    """The configuration with every secret replaced. The only loggable version."""
    return config.safe_dict()


def main() -> None:
    config = resolve(SPEC, argv=sys.argv[1:], environ=dict(os.environ))
    print(config.provenance_table())
    for problem in validate(config, SPEC):
        print(f"PROBLEM: {problem}")


if __name__ == "__main__":
    main()
