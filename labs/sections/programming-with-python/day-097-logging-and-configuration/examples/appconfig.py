"""A four-layer configuration resolver that remembers where every value came from.

The four layers, lowest precedence first:

    1. defaults       written in the code, so the program runs with none of
                      the other three present
    2. config file    TOML, read with `tomllib` from the standard library
    3. environment    os.environ, which is where secrets and per-deployment
                      values belong
    4. command line   argparse flags, which are the most specific and
                      therefore win

Every setting carries a `Resolved` record — the value AND the layer that
supplied it AND the raw text before conversion. That is the whole reason
this module exists. "Why is it doing that?" should be answered by printing
the configuration, in five seconds, not by reading four files and guessing.

Everything here is the standard library: `os`, `tomllib`, `argparse`,
`pathlib`, `dataclasses`.
"""

from __future__ import annotations

import argparse
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

# --------------------------------------------------------------------------
# Type conversion. Everything from a file, an environment variable or a flag
# arrives as text, and text is not a type.
# --------------------------------------------------------------------------

TRUE_WORDS = frozenset({"1", "true", "yes", "on"})
FALSE_WORDS = frozenset({"0", "false", "no", "off"})


class ConfigError(Exception):
    """Raised at startup when configuration is unusable. Never at 3 a.m."""


def to_bool(text: str) -> bool:
    """Convert text to a bool, refusing anything ambiguous.

    This function exists because `bool("false")` is `True`. Every non-empty
    string is truthy in Python, so the naive version of this conversion
    turns "false" into on, silently, and the feature you switched off stays
    switched on. There is no warning; there is no error; there is only the
    wrong behaviour.
    """
    lowered = text.strip().lower()
    if lowered in TRUE_WORDS:
        return True
    if lowered in FALSE_WORDS:
        return False
    raise ValueError(
        f"expected one of {sorted(TRUE_WORDS | FALSE_WORDS)}, got {text!r}"
    )


def to_int(text: str) -> int:
    return int(text.strip())


def to_str(text: str) -> str:
    return text


CONVERTERS: dict[str, Callable[[str], Any]] = {
    "str": to_str,
    "int": to_int,
    "bool": to_bool,
}


# --------------------------------------------------------------------------
# The specification of one setting, and the record of one resolved value.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Setting:
    """What a setting is called in each of the four layers, and its rules."""

    name: str
    kind: str                       # "str" | "int" | "bool"
    default: Any
    env: str | None = None          # environment variable name
    flag: str | None = None         # command-line flag, e.g. "--batch-size"
    choices: tuple[Any, ...] | None = None
    minimum: int | None = None
    maximum: int | None = None
    secret: bool = False            # never printed, never logged
    help: str = ""


@dataclass(frozen=True)
class Resolved:
    """One setting's value, and the provenance of that value."""

    name: str
    value: Any
    source: str                     # "default" | "file:..." | "env:..." | "flag:..."
    raw: str | None = None          # the text before conversion, when there was any
    secret: bool = False

    def display(self) -> str:
        return "***redacted***" if self.secret and self.value is not None else repr(self.value)


@dataclass
class Config:
    """The resolved configuration: values by name, each with its provenance."""

    settings: dict[str, Resolved] = field(default_factory=dict)

    def __getitem__(self, name: str) -> Any:
        return self.settings[name].value

    def source_of(self, name: str) -> str:
        return self.settings[name].source

    def as_dict(self) -> dict[str, Any]:
        return {name: r.value for name, r in self.settings.items()}

    def safe_dict(self) -> dict[str, Any]:
        """Every value except the secrets, which become the placeholder.

        This is the dictionary you are allowed to log.
        """
        return {
            name: ("***redacted***" if r.secret and r.value is not None else r.value)
            for name, r in self.settings.items()
        }

    def provenance_table(self) -> str:
        """The five-second answer to "why is it doing that?"."""
        width_n = max(len(n) for n in self.settings)
        width_v = max(len(r.display()) for r in self.settings.values())
        width_n = max(width_n, len("setting"))
        width_v = max(width_v, len("value"))
        lines = [
            f"{'setting'.ljust(width_n)}  {'value'.ljust(width_v)}  came from",
            f"{'-' * width_n}  {'-' * width_v}  {'-' * 24}",
        ]
        for name in self.settings:
            r = self.settings[name]
            lines.append(f"{name.ljust(width_n)}  {r.display().ljust(width_v)}  {r.source}")
        return "\n".join(lines)


# --------------------------------------------------------------------------
# The resolver.
# --------------------------------------------------------------------------


def load_toml(path: Path | None) -> tuple[dict[str, Any], str | None]:
    """Read a TOML file if it exists. Returns the table and the path used.

    `tomllib` has been in the standard library since Python 3.11, and it is
    READ-ONLY on purpose — there is no `tomllib.dump`. If your program needs
    to write TOML you need a third-party library; if it only needs to read
    its own configuration, which is the overwhelmingly common case, the
    standard library is enough.

    Note the mode: `tomllib.load` requires a binary file object. Passing a
    text file raises `TypeError`, and that catches everybody once.
    """
    if path is None or not path.exists():
        return {}, None
    with path.open("rb") as handle:
        return tomllib.load(handle), str(path.name)


def build_parser(spec: Sequence[Setting]) -> argparse.ArgumentParser:
    """One flag per setting that has one. Defaults are deliberately absent.

    argparse's own `default=` is not used, because then a value that came
    from a default would be indistinguishable from one the user typed. The
    parser's job here is only to report what was actually passed; the
    layering is done by this module.
    """
    parser = argparse.ArgumentParser(
        prog="app",
        description="Demonstration application with four-layer configuration.",
        add_help=True,
    )
    parser.add_argument("--config", default=None, help="path to a TOML config file")
    for setting in spec:
        if setting.flag is None:
            continue
        if setting.kind == "bool":
            # Two flags rather than one, so --no-x can override a file or an
            # environment variable that said true. A lone --x can only ever
            # turn something on, which makes the highest-precedence layer
            # unable to express half of the values.
            parser.add_argument(
                setting.flag, dest=setting.name, action="store_const",
                const="true", default=None, help=setting.help,
            )
            parser.add_argument(
                setting.flag.replace("--", "--no-", 1), dest=setting.name,
                action="store_const", const="false", default=None,
                help=f"disable {setting.name}",
            )
        else:
            parser.add_argument(
                setting.flag, dest=setting.name, default=None, help=setting.help
            )
    return parser


def resolve(
    spec: Sequence[Setting],
    argv: Sequence[str] | None = None,
    environ: dict[str, str] | None = None,
    config_path: Path | None = None,
) -> Config:
    """Resolve every setting through the four layers, recording provenance.

    `argv` and `environ` are parameters with defaults rather than reads of
    `sys.argv` and `os.environ`, for exactly the reason Day 91's report took
    its instant as a parameter: a function that reaches out to global state
    cannot be tested, and configuration resolution is the one piece of code
    you most want to be able to test.
    """
    environ = os.environ if environ is None else environ
    parser = build_parser(spec)
    args = parser.parse_args([] if argv is None else list(argv))

    if args.config is not None:
        config_path = Path(args.config)
    file_table, file_name = load_toml(config_path)

    config = Config()
    for setting in spec:
        # ---- layer 1: the default in the code -----------------------------
        value, source, raw = setting.default, "default", None

        # ---- layer 2: the config file -------------------------------------
        if setting.name in file_table:
            file_value = file_table[setting.name]
            # TOML has real types, so a value read from it is already an int
            # or a bool. Only convert when it arrived as text.
            if isinstance(file_value, str) and setting.kind != "str":
                raw = file_value
                value = _convert(setting, file_value, f"file:{file_name}")
            else:
                raw = None
                value = _typecheck(setting, file_value, f"file:{file_name}")
            source = f"file:{file_name}"

        # ---- layer 3: the environment -------------------------------------
        if setting.env is not None and setting.env in environ:
            text = environ[setting.env]
            # A missing variable and an empty one are DIFFERENT. `in environ`
            # asks whether it was set at all; the empty string is a value
            # somebody chose. `os.environ.get(name)` collapses the two into
            # None-or-text and loses the distinction, which is why this uses
            # containment rather than .get().
            if text == "":
                value = "" if setting.kind == "str" else setting.default
                source = f"env:{setting.env} (set but empty)"
                raw = ""
                if setting.kind != "str":
                    raise ConfigError(
                        f"{setting.name}: environment variable {setting.env} is set "
                        f"but empty, and an empty string is not a valid "
                        f"{setting.kind}. Unset it to use the default, or give it a value."
                    )
            else:
                raw = text
                value = _convert(setting, text, f"env:{setting.env}")
                source = f"env:{setting.env}"

        # ---- layer 4: the command line ------------------------------------
        typed = getattr(args, setting.name, None)
        if typed is not None:
            raw = typed
            value = _convert(setting, typed, f"flag:{setting.flag}")
            source = f"flag:{setting.flag}"

        config.settings[setting.name] = Resolved(
            name=setting.name, value=value, source=source, raw=raw, secret=setting.secret
        )
    return config


def _convert(setting: Setting, text: str, where: str) -> Any:
    try:
        return CONVERTERS[setting.kind](text)
    except ValueError as error:
        raise ConfigError(
            f"{setting.name}: cannot read {text!r} from {where} as {setting.kind} ({error})"
        ) from error


def _typecheck(setting: Setting, value: Any, where: str) -> Any:
    expected = {"str": str, "int": int, "bool": bool}[setting.kind]
    # bool is a subclass of int in Python, so an int setting must reject True
    # explicitly or `batch_size = true` in the TOML file becomes 1.
    if setting.kind == "int" and isinstance(value, bool):
        raise ConfigError(f"{setting.name}: {where} gave a boolean where an int was expected")
    if not isinstance(value, expected):
        raise ConfigError(
            f"{setting.name}: {where} gave {type(value).__name__} "
            f"where {setting.kind} was expected"
        )
    return value


# --------------------------------------------------------------------------
# Validation, run once at startup.
# --------------------------------------------------------------------------


def validate(config: Config, spec: Sequence[Setting]) -> list[str]:
    """Return every problem, each naming the setting AND where the value came from.

    Two deliberate choices.

    It returns ALL the problems rather than raising on the first one, because
    fixing configuration one error per run is miserable and encourages people
    to guess.

    Every message names the provenance. "batch_size must be at least 1" tells
    you what is wrong. "batch_size: 0 is below the minimum of 1 (from
    flag:--batch-size)" tells you where to go and fix it.
    """
    problems: list[str] = []
    for setting in spec:
        resolved = config.settings[setting.name]
        value, where = resolved.value, resolved.source
        shown = "***redacted***" if setting.secret else repr(value)

        if setting.choices is not None and value not in setting.choices:
            problems.append(
                f"{setting.name}: {shown} is not one of "
                f"{list(setting.choices)} (from {where})"
            )
        if setting.minimum is not None and isinstance(value, int) and value < setting.minimum:
            problems.append(
                f"{setting.name}: {shown} is below the minimum of "
                f"{setting.minimum} (from {where})"
            )
        if setting.maximum is not None and isinstance(value, int) and value > setting.maximum:
            problems.append(
                f"{setting.name}: {shown} is above the maximum of "
                f"{setting.maximum} (from {where})"
            )
    return problems


def validate_or_die(config: Config, spec: Sequence[Setting]) -> None:
    """Fail at startup, loudly, with every problem listed at once."""
    problems = validate(config, spec)
    if problems:
        raise ConfigError(
            "configuration is not usable:\n  - " + "\n  - ".join(problems)
        )


# --------------------------------------------------------------------------
# The specification this lab's demonstration application uses.
# --------------------------------------------------------------------------

APP_SPEC: tuple[Setting, ...] = (
    Setting(
        name="log_level", kind="str", default="INFO",
        env="APP_LOG_LEVEL", flag="--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="lowest severity that reaches the handlers",
    ),
    Setting(
        name="batch_size", kind="int", default=32,
        env="APP_BATCH_SIZE", flag="--batch-size",
        minimum=1, maximum=1024,
        help="records processed per batch",
    ),
    Setting(
        name="model_name", kind="str", default="tiny-baseline",
        env="APP_MODEL_NAME", flag="--model-name",
        help="which model this run uses",
    ),
    Setting(
        name="seed", kind="int", default=0,
        env="APP_SEED", flag="--seed", minimum=0,
        help="random seed, so the run can be repeated",
    ),
    Setting(
        name="dry_run", kind="bool", default=False,
        env="APP_DRY_RUN", flag="--dry-run",
        help="do everything except write anything",
    ),
    Setting(
        name="data_version", kind="str", default="v1",
        env="APP_DATA_VERSION", flag="--data-version",
        help="which snapshot of the dataset this run read",
    ),
    # No flag. A secret passed on the command line is visible in the process
    # table to every other user on the machine, and lands in the shell
    # history file. Environment or a secret manager, and nowhere else.
    Setting(
        name="api_key", kind="str", default="",
        env="APP_API_KEY", flag=None, secret=True,
        help="credential for the upstream service (environment only)",
    ),
)
