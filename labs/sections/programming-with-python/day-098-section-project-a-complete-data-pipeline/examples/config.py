"""Stage 5, part one: configuration resolved by precedence, with provenance.

Day 97's rule, and the Twelve-Factor App's third factor before it: configuration
lives outside the code, and the process reads it from the environment. This
module implements that with four layers, lowest first:

    1. defaults        the values baked into this file
    2. file            a TOML file named by --config-file
    3. environment     PIPELINE_<KEY>, uppercased
    4. command line    an explicit flag

The part people skip is the fourth column. Knowing that ``timeout_seconds`` is
5.0 is half an answer at 3 a.m.; knowing it is 5.0 *because nobody set it* is
the whole answer. So every resolved setting carries where it came from, and
``provenance_table`` prints it.

Secrets are marked, and a marked secret is never printed and never logged.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

REDACTED = "***redacted***"

#: key -> (default value, parser, is_secret)
SPEC: dict[str, tuple[object, str, bool]] = {
    "base_url": ("http://127.0.0.1:8080", "str", False),
    "sources": ("alpha,bravo,charlie", "str", False),
    "database_url": ("sqlite:///pipeline.db", "str", False),
    "api_token": ("", "str", True),
    "timeout_seconds": (5.0, "float", False),
    "retry_attempts": (3, "int", False),
    "retry_backoff_seconds": (0.05, "float", False),
    "window_hours": (12, "int", False),
    "report_at": ("", "str", False),
    "log_level": ("info", "str", False),
}


@dataclass(frozen=True)
class Setting:
    """One resolved setting and the layer that won it."""

    key: str
    value: object
    source: str
    secret: bool

    @property
    def display(self) -> str:
        if self.secret and self.value:
            return REDACTED
        if self.value == "":
            # An empty string is a real answer ("nobody set it"), and printing
            # nothing at all is how a provenance table stops being useful.
            return "<unset>"
        return str(self.value)


def _coerce(raw: object, kind: str) -> object:
    if kind == "int":
        return int(raw)
    if kind == "float":
        return float(raw)
    return str(raw)


@dataclass(frozen=True)
class Config:
    settings: dict[str, Setting]

    def __getitem__(self, key: str) -> object:
        return self.settings[key].value

    def source_of(self, key: str) -> str:
        return self.settings[key].source

    @property
    def source_names(self) -> list[str]:
        raw = str(self["sources"])
        return [name.strip() for name in raw.split(",") if name.strip()]

    @property
    def secrets(self) -> tuple[str, ...]:
        return tuple(
            str(setting.value)
            for setting in self.settings.values()
            if setting.secret and setting.value
        )

    def provenance_table(self) -> str:
        """The printable answer to 'why is it set to that?'."""
        width_key = max(len(k) for k in self.settings)
        width_value = max(len(s.display) for s in self.settings.values())
        width_value = max(width_value, len("value"))
        lines = [
            f"{'setting'.ljust(width_key)}  {'value'.ljust(width_value)}  source",
            f"{'-' * width_key}  {'-' * width_value}  {'-' * 12}",
        ]
        for key in sorted(self.settings):
            setting = self.settings[key]
            lines.append(
                f"{key.ljust(width_key)}  {setting.display.ljust(width_value)}  {setting.source}"
            )
        return "\n".join(lines)


def load_config(
    *,
    config_file: str | Path | None = None,
    environ: dict[str, str] | None = None,
    overrides: dict[str, object] | None = None,
) -> Config:
    """Resolve every setting through the four layers and record which one won.

    ``overrides`` is the command-line layer: pass only the flags the user
    actually gave, because a flag left at its argparse default is not a
    decision and must not outrank the environment.
    """
    environ = os.environ if environ is None else environ
    overrides = overrides or {}

    from_file: dict[str, object] = {}
    if config_file:
        path = Path(config_file)
        if not path.is_file():
            raise FileNotFoundError(f"config file not found: {path}")
        from_file = tomllib.loads(path.read_text(encoding="utf-8"))

    resolved: dict[str, Setting] = {}
    for key, (default, kind, secret) in SPEC.items():
        value: object = default
        source = "default"
        if key in from_file:
            value, source = _coerce(from_file[key], kind), "file"
        env_key = f"PIPELINE_{key.upper()}"
        if environ.get(env_key):
            value, source = _coerce(environ[env_key], kind), "environment"
        if key in overrides and overrides[key] is not None:
            value, source = _coerce(overrides[key], kind), "command line"
        resolved[key] = Setting(key=key, value=value, source=source, secret=secret)

    return Config(settings=resolved)
