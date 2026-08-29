#!/usr/bin/env python3
"""EXERCISES 7-12 — the configuration half. Your work goes here.

Check your progress at any time:

    bash starter/03_check.sh

The `Setting`, `Resolved` and `Config` types are written for you and are
complete. What is missing is the resolution itself, and it is the part worth
writing by hand once.

Standard library only: os, tomllib, argparse, pathlib, dataclasses.
"""

from __future__ import annotations

import argparse
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

TRUE_WORDS = frozenset({"1", "true", "yes", "on"})
FALSE_WORDS = frozenset({"0", "false", "no", "off"})


class ConfigError(Exception):
    """Raised at startup when configuration is unusable."""


# ---------------------------------------------------------------------------
# WRITTEN FOR YOU — the three types. Read them; they define the shape of the
# answer. The important one is Resolved: a value AND its provenance, together,
# because they are useless apart.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Setting:
    name: str
    kind: str                       # "str" | "int" | "bool"
    default: Any
    env: str | None = None
    flag: str | None = None
    choices: tuple[Any, ...] | None = None
    minimum: int | None = None
    maximum: int | None = None
    secret: bool = False


@dataclass(frozen=True)
class Resolved:
    name: str
    value: Any
    source: str                     # "default" | "file:..." | "env:..." | "flag:..."
    raw: str | None = None
    secret: bool = False


@dataclass
class Config:
    settings: dict[str, Resolved] = field(default_factory=dict)

    def __getitem__(self, name: str) -> Any:
        return self.settings[name].value

    def source_of(self, name: str) -> str:
        return self.settings[name].source


# The specification the checker uses. Do not change it.
SPEC: tuple[Setting, ...] = (
    Setting("log_level", "str", "INFO", env="APP_LOG_LEVEL", flag="--log-level",
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    Setting("batch_size", "int", 32, env="APP_BATCH_SIZE", flag="--batch-size",
            minimum=1, maximum=1024),
    Setting("model_name", "str", "tiny-baseline", env="APP_MODEL_NAME",
            flag="--model-name"),
    Setting("dry_run", "bool", False, env="APP_DRY_RUN", flag="--dry-run"),
    # No flag, deliberately: a secret on the command line is visible in `ps`
    # to every other user on the machine and lands in the shell history file.
    Setting("api_key", "str", "", env="APP_API_KEY", flag=None, secret=True),
)


# ---------------------------------------------------------------------------
# WRITTEN FOR YOU — the argument parser. Note what it does NOT do: it sets no
# argparse defaults, so a flag that was not typed comes back as None and is
# distinguishable from one that was. The layering is your job, not argparse's.
# ---------------------------------------------------------------------------

def build_parser(spec: Sequence[Setting]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app", add_help=True)
    for setting in spec:
        if setting.flag is None:
            continue
        if setting.kind == "bool":
            parser.add_argument(setting.flag, dest=setting.name,
                                action="store_const", const="true", default=None)
            parser.add_argument(setting.flag.replace("--", "--no-", 1),
                                dest=setting.name, action="store_const",
                                const="false", default=None)
        else:
            parser.add_argument(setting.flag, dest=setting.name, default=None)
    return parser


# ---------------------------------------------------------------------------
# EXERCISE 7 — to_bool
#
# `bool("false")` is True. Every non-empty string is truthy in Python, so the
# naive conversion turns the word "false" into on, silently, and the feature
# you switched off stays switched on.
#
# Return True for anything in TRUE_WORDS, False for anything in FALSE_WORDS,
# case-insensitively and ignoring surrounding whitespace. Raise ValueError for
# anything else — including "", "maybe" and "2". Guessing is what got us here.
# ---------------------------------------------------------------------------

def to_bool(text: str) -> bool:
    raise NotImplementedError("EXERCISE 7: an explicit table, and a refusal for the rest")


# ---------------------------------------------------------------------------
# EXERCISE 8 — read the TOML file
#
# Return (table, filename) for a file that exists, and ({}, None) for a path
# that is None or missing. `tomllib.load` needs a BINARY file object; passing
# a text one raises TypeError, and that catches everybody exactly once.
#
# tomllib has been in the standard library since Python 3.11 and is read-only:
# there is no tomllib.dump. That is a deliberate scope decision, and it is
# fine, because a program almost always reads its configuration and almost
# never writes it.
# ---------------------------------------------------------------------------

def load_toml(path: Path | None) -> tuple[dict[str, Any], str | None]:
    raise NotImplementedError("EXERCISE 8: open it in binary mode, and handle 'missing'")


# ---------------------------------------------------------------------------
# EXERCISES 9, 10, 11 — the resolver
#
# Fill in `resolve` so that every setting is resolved through four layers,
# lowest precedence first:
#
#   1. default          source "default"
#   2. config file      source "file:<filename>"
#   3. environment      source "env:<VARIABLE>"
#   4. command line     source "flag:<--flag>"
#
# Each layer that has a value overwrites the one before it, and records its
# own name as the provenance. That is EXERCISE 9 (the layering) and EXERCISE
# 11 (the provenance) together, and they are one loop.
#
# EXERCISE 10 is the awkward one, and it is awkward in real life too. A
# missing environment variable and an empty one are DIFFERENT:
#
#   * not set at all              -> fall through to the layer below
#   * set to ""                   -> the operator said something. For a str
#                                    setting the value is "" and the source is
#                                    "env:NAME (set but empty)". For an int or
#                                    a bool setting, raise ConfigError naming
#                                    the variable, because "" is not a number.
#
# Ask `name in environ`, not `environ.get(name)`. `.get` returns None for
# never-set and "" for set-to-empty, and the usual `or default` idiom then
# collapses both into the default and loses the distinction forever.
#
# Types: a value from the file is already an int or a bool, because TOML has
# real types. A value from the environment or a flag is always text and must
# be converted. Conversion failures raise ConfigError naming the setting AND
# where the bad value came from.
# ---------------------------------------------------------------------------

def resolve(
    spec: Sequence[Setting],
    argv: Sequence[str] | None = None,
    environ: dict[str, str] | None = None,
    config_path: Path | None = None,
) -> Config:
    raise NotImplementedError(
        "EXERCISES 9-11: four layers, in order, each recording its own provenance"
    )


# ---------------------------------------------------------------------------
# EXERCISE 12 — validate at startup, and safe_dict
#
# `validate` returns a list of problem strings — ALL of them, not just the
# first, because fixing configuration one error per run is miserable.
#
# Check `choices`, `minimum` and `maximum` where the Setting defines them.
# Every message must contain:
#
#   * the setting's NAME
#   * what is wrong
#   * the PROVENANCE, so the reader knows which of the four places to go and
#     edit. The checker requires the source string to appear in the message.
#
# Never put a secret's VALUE in a message. Use "***redacted***" instead.
#
# `safe_dict` returns {name: value} with every secret replaced by
# "***redacted***". It is the only version of the configuration that may be
# logged, and exercise 5's JSON formatter is where it ends up.
# ---------------------------------------------------------------------------

def validate(config: Config, spec: Sequence[Setting]) -> list[str]:
    raise NotImplementedError(
        "EXERCISE 12: every problem at once, each naming the setting and its source"
    )


def safe_dict(config: Config) -> dict[str, Any]:
    raise NotImplementedError("EXERCISE 12: the configuration, minus the secrets")


# ---------------------------------------------------------------------------
# A place to try things out. `python3 starter/02_config.py --batch-size 256`
# ---------------------------------------------------------------------------

def main() -> None:
    import sys

    config = resolve(SPEC, argv=sys.argv[1:], environ=dict(os.environ))
    problems = validate(config, SPEC)
    for name, resolved in config.settings.items():
        shown = "***redacted***" if resolved.secret and resolved.value else repr(resolved.value)
        print(f"{name:<12} {shown:<18} {resolved.source}")
    for problem in problems:
        print(f"PROBLEM: {problem}")


if __name__ == "__main__":
    main()
