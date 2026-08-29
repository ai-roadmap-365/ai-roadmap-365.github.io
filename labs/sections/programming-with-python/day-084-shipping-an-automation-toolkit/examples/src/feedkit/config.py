"""Configuration, resolved by a precedence that is written down and testable.

The order, weakest first:

    1. defaults baked into the code   — so the tool runs with no setup at all
    2. a configuration file           — the machine's long-lived preferences
    3. environment variables          — deployment-specific values and secrets
    4. command-line flags             — this one run, right now

Every automation has this order. Most of them have it by accident, spread over
a dozen `or` expressions, and nobody can say what wins. Here it is one pure
function over four dictionaries, so a test can assert all four levels — which
is exactly what `tests/run_tests.sh` does.

`resolve` also records WHERE each value came from. `feedkit status
--explain-config` prints that table, which turns "why is it doing that?" into a
five-second question instead of an afternoon.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

#: Layer 1. Everything the toolkit needs to run at all, with no file, no
#: environment and no flags. A tool that cannot start without configuration is
#: a tool nobody tries.
DEFAULTS: dict[str, Any] = {
    "sources": ["notes", "links"],
    "max_items": 5,
    "report_limit": 10,
    "timeout_seconds": 5.0,
    "retries": 3,
    "backoff_seconds": 0.5,
    "log_level": "info",
    "state_file": "feedkit-state.json",
    "max_age_minutes": 1440,
}

#: Layer 3. Environment variable name -> (config key, type).
ENV_KEYS: dict[str, tuple[str, str]] = {
    "FEEDKIT_BASE_URL": ("base_url", "str"),
    "FEEDKIT_MAX_ITEMS": ("max_items", "int"),
    "FEEDKIT_REPORT_LIMIT": ("report_limit", "int"),
    "FEEDKIT_TIMEOUT_SECONDS": ("timeout_seconds", "float"),
    "FEEDKIT_RETRIES": ("retries", "int"),
    "FEEDKIT_BACKOFF_SECONDS": ("backoff_seconds", "float"),
    "FEEDKIT_LOG_LEVEL": ("log_level", "str"),
    "FEEDKIT_STATE_FILE": ("state_file", "str"),
    "FEEDKIT_MAX_AGE_MINUTES": ("max_age_minutes", "int"),
    "FEEDKIT_SOURCES": ("sources", "list"),
}

#: The one value that must NEVER come from a file in the repository.
SECRET_ENV = "FEEDKIT_TOKEN"


class ConfigError(ValueError):
    """The configuration is unusable. Stop the run; do not guess."""


@dataclass(frozen=True)
class Config:
    """The resolved settings for one run."""

    base_url: str
    sources: tuple[str, ...]
    max_items: int
    report_limit: int
    timeout_seconds: float
    retries: int
    backoff_seconds: float
    log_level: str
    state_file: str
    max_age_minutes: int
    token: str = ""
    provenance: Mapping[str, str] = field(default_factory=dict)

    @property
    def max_age_seconds(self) -> int:
        return self.max_age_minutes * 60


def coerce(value: Any, kind: str, key: str) -> Any:
    """Turn a string from a file, an environment variable or a flag into the
    type the rest of the program expects, and fail loudly when it cannot."""
    if kind == "list":
        if isinstance(value, (list, tuple)):
            return [str(item) for item in value]
        return [part.strip() for part in str(value).split(",") if part.strip()]
    try:
        if kind == "int":
            return int(value)
        if kind == "float":
            return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{key}: {value!r} is not a valid {kind}") from exc
    return str(value)


def kind_of(key: str) -> str:
    """The declared type of a configuration key, from the defaults table."""
    for _, (config_key, kind) in ENV_KEYS.items():
        if config_key == key:
            return kind
    default = DEFAULTS.get(key)
    if isinstance(default, bool):
        return "str"
    if isinstance(default, int):
        return "int"
    if isinstance(default, float):
        return "float"
    if isinstance(default, list):
        return "list"
    return "str"


def read_config_file(path: Path) -> dict[str, Any]:
    """Read a TOML configuration file. Missing file is not an error; an
    unparseable one is."""
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path}: not valid TOML: {exc}") from exc
    settings = data.get("feedkit", data)
    if not isinstance(settings, dict):
        raise ConfigError(f"{path}: expected a table of settings")
    return dict(settings)


def find_config_file(explicit: str | None, environ: Mapping[str, str], cwd: Path) -> Path | None:
    """Where the configuration file lives, in the order a user expects.

    A flag beats the environment, which beats the current directory, which
    beats the user's XDG configuration directory. Returning None means "no file
    anywhere", which is a perfectly normal state, not an error.
    """
    if explicit:
        return Path(explicit).expanduser()
    from_env = environ.get("FEEDKIT_CONFIG")
    if from_env:
        return Path(from_env).expanduser()
    local = cwd / "feedkit.toml"
    if local.is_file():
        return local
    base = environ.get("XDG_CONFIG_HOME")
    home = Path(base).expanduser() if base else Path(environ.get("HOME", "~")).expanduser() / ".config"
    candidate = home / "feedkit" / "feedkit.toml"
    return candidate if candidate.is_file() else None


def env_values(environ: Mapping[str, str]) -> dict[str, Any]:
    """Layer 3, extracted from an environment mapping passed in as an argument
    (never read from os.environ in here — that is a boundary, and tests need to
    supply their own)."""
    values: dict[str, Any] = {}
    for name, (key, kind) in ENV_KEYS.items():
        if name in environ and environ[name] != "":
            values[key] = coerce(environ[name], kind, key)
    return values


def resolve(
    file_values: Mapping[str, Any],
    environment: Mapping[str, Any],
    flags: Mapping[str, Any],
    token: str = "",
) -> Config:
    """Apply the four layers in order and record where each value came from.

    Pure. Four dictionaries in, one Config out. This is the function the lab's
    precedence test drives directly, and it is why "which layer wins?" is a
    question with a checked answer rather than a folk belief.
    """
    merged: dict[str, Any] = {}
    provenance: dict[str, str] = {}

    for layer_name, layer in (
        ("default", DEFAULTS),
        ("file", file_values),
        ("environment", environment),
        ("flag", {key: value for key, value in flags.items() if value is not None}),
    ):
        for key, value in layer.items():
            if key not in DEFAULTS and key != "base_url":
                # An unknown key in a config file is almost always a typo, and
                # silently ignoring it is how people lose an afternoon.
                if layer_name == "file":
                    raise ConfigError(f"unknown setting in configuration file: {key!r}")
                continue
            merged[key] = coerce(value, kind_of(key), key) if layer_name != "default" else value
            provenance[key] = layer_name

    base_url = str(merged.get("base_url", "")).rstrip("/")
    if not base_url:
        raise ConfigError(
            "no base URL configured. Set FEEDKIT_BASE_URL in the environment, "
            "or pass --base-url. Deployment-specific addresses do not belong in "
            "a file that is committed."
        )
    if merged["retries"] < 1:
        raise ConfigError("retries must be at least 1")
    if merged["max_items"] < 0:
        raise ConfigError("max-items must not be negative")

    provenance.setdefault("base_url", "environment")
    provenance["token"] = "environment" if token else "unset"

    return Config(
        base_url=base_url,
        sources=tuple(merged["sources"]),
        max_items=int(merged["max_items"]),
        report_limit=int(merged["report_limit"]),
        timeout_seconds=float(merged["timeout_seconds"]),
        retries=int(merged["retries"]),
        backoff_seconds=float(merged["backoff_seconds"]),
        log_level=str(merged["log_level"]),
        state_file=str(merged["state_file"]),
        max_age_minutes=int(merged["max_age_minutes"]),
        token=token,
        provenance=provenance,
    )


def load(
    flags: Mapping[str, Any],
    environ: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> tuple[Config, Path | None]:
    """The impure wrapper: find the file, read the environment, then call the
    pure `resolve`. All the I/O is in these six lines."""
    environ = os.environ if environ is None else environ
    cwd = Path.cwd() if cwd is None else cwd
    config_path = find_config_file(flags.get("config"), environ, cwd)
    file_values = read_config_file(config_path) if config_path else {}
    token = environ.get(SECRET_ENV, "")
    config = resolve(file_values, env_values(environ), flags, token=token)
    return config, config_path


def explain(config: Config, config_path: Path | None) -> str:
    """The provenance table. Answers 'why is it doing that?' in one command."""
    lines = [f"configuration file: {config_path or 'none found'}", ""]
    lines.append(f"  {'setting':<20} {'value':<28} {'came from'}")
    for key in sorted(config.provenance):
        if key == "token":
            shown = "set (never printed)" if config.token else "unset"
        else:
            shown = str(getattr(config, key, ""))
        lines.append(f"  {key:<20} {shown:<28} {config.provenance[key]}")
    return "\n".join(lines)
