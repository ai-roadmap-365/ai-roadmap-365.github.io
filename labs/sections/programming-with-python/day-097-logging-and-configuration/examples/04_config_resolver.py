#!/usr/bin/env python3
"""Four layers of configuration, resolved once, with the provenance of every value.

    python3 examples/04_config_resolver.py

The layers, lowest precedence first:

    default  <  config file  <  environment  <  command-line flag

Five demonstrations:

    1. one setting given a DIFFERENT value in all four layers at once, so you
       can watch each layer override the last and see which one wins
    2. the provenance table: every setting, its value, and where it came from
    3. the type problem — everything from the environment is text, and
       bool("false") is True
    4. missing and empty are different, and the difference is visible
    5. the startup validator, refusing bad values by name and by provenance

Everything is the standard library: os, tomllib, argparse, pathlib.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from appconfig import (  # noqa: E402
    APP_SPEC,
    ConfigError,
    Setting,
    resolve,
    to_bool,
    validate,
    validate_or_die,
)

CONFIG_FILE = Path(__file__).resolve().parent / "config.toml"


def banner(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def demo_precedence() -> None:
    banner("1. One setting, four different values, four layers")

    print("batch_size is:")
    print("    32   in the code, as the default")
    print("    64   in examples/config.toml")
    print("   128   in the environment, as APP_BATCH_SIZE")
    print("   256   on the command line, as --batch-size")
    print()
    print("Adding one layer at a time:")
    print()

    steps = [
        ("nothing but the code", [], {}, None),
        ("+ the config file", [], {}, CONFIG_FILE),
        ("+ the environment", [], {"APP_BATCH_SIZE": "128"}, CONFIG_FILE),
        ("+ the flag", ["--batch-size", "256"], {"APP_BATCH_SIZE": "128"}, CONFIG_FILE),
    ]
    for label, argv, environ, path in steps:
        config = resolve(APP_SPEC, argv=argv, environ=environ, config_path=path)
        resolved = config.settings["batch_size"]
        print(f"  {label:<24}  batch_size = {resolved.value:<5} from {resolved.source}")

    print()
    print("The flag wins. That ordering is not arbitrary and it is worth being")
    print("able to justify: each layer is more specific than the one below it.")
    print("A default is what everybody gets. A file is what this deployment")
    print("gets. An environment variable is what this process gets. A flag is")
    print("what THIS INVOCATION gets, typed by a person who is looking at the")
    print("problem right now. The more specific statement wins, which is the")
    print("same rule CSS uses and the same rule your shell uses.")


def demo_provenance() -> None:
    banner("2. The provenance table: why is it doing that?")

    config = resolve(
        APP_SPEC,
        argv=["--batch-size", "256", "--log-level", "DEBUG"],
        environ={"APP_SEED": "7", "APP_API_KEY": "sk-live-9f2c4a7b1e63"},
        config_path=CONFIG_FILE,
    )
    print(config.provenance_table())
    print()
    print("Every setting reports its value AND the layer that supplied it.")
    print("Seven settings, five different provenances, one screen. The value of")
    print("this is entirely in the third column: without it, 'why is batch_size")
    print("256?' means reading a TOML file, a deployment manifest, a shell")
    print("wrapper and an argparse definition, in the dark, at speed.")
    print()
    print("Note api_key. It is in the table so you can see WHERE it came from")
    print("and whether it is set at all, and its value is never printed. Those")
    print("are two different questions and only one of them is dangerous.")
    print()
    print("Note also that api_key has no flag. A secret passed on the command")
    print("line is visible in `ps` to every other user on the machine and lands")
    print("in the shell history file. Environment or a secret manager, and")
    print("nowhere else.")


def demo_types() -> None:
    banner("3. Everything from the environment is a string")

    print("The trap, in one line of Python:")
    print(f'    bool("false")  ->  {bool("false")}')
    print()
    print("Every non-empty string is truthy. So the naive conversion turns the")
    print("word 'false' into on, silently, and the feature you switched off")
    print("stays switched on. No error, no warning, just the wrong behaviour.")
    print()
    print("The fix is an explicit table of words, and a refusal for anything")
    print("else:")
    for text in ["true", "TRUE", "1", "yes", "on", "false", "0", "no", "off"]:
        print(f"    to_bool({text!r:<8}) -> {to_bool(text)}")
    for text in ["maybe", "", "2"]:
        try:
            to_bool(text)
        except ValueError as error:
            print(f"    to_bool({text!r:<8}) -> refused: {error}")

    print()
    print("Then the same discipline for the other types. An int setting read")
    print("from the environment:")
    for text in ["128", " 128 ", "12.5"]:
        try:
            config = resolve(APP_SPEC, argv=[], environ={"APP_BATCH_SIZE": text})
            print(f"    APP_BATCH_SIZE={text!r:<8} -> {config['batch_size']}")
        except ConfigError as error:
            print(f"    APP_BATCH_SIZE={text!r:<8} -> refused: {error}")

    print()
    print("And the difference the config file makes: TOML has real types, so")
    print("`batch_size = 64` in the file arrives as an int already and needs no")
    print("conversion at all. That is a genuine advantage of a typed file")
    print("format over the environment, and it is the reason a file is a better")
    print("home for structured configuration than a pile of variables.")
    config = resolve(APP_SPEC, argv=[], environ={}, config_path=CONFIG_FILE)
    print(f"    from config.toml: batch_size = {config['batch_size']!r} "
          f"({type(config['batch_size']).__name__}), "
          f"dry_run = {config['dry_run']!r} "
          f"({type(config['dry_run']).__name__})")


def demo_missing_versus_empty() -> None:
    banner("4. A missing variable and an empty one are different")

    print("These are three different states of one environment variable, and a")
    print("program that cannot tell them apart will eventually do the wrong")
    print("thing with at least one:")
    print()

    cases = [
        ("not set at all", {}),
        ("set to the empty string", {"APP_MODEL_NAME": ""}),
        ("set to a value", {"APP_MODEL_NAME": "large-encoder"}),
    ]
    for label, environ in cases:
        config = resolve(APP_SPEC, argv=[], environ=environ, config_path=CONFIG_FILE)
        resolved = config.settings["model_name"]
        print(f"  {label:<26} value={resolved.value!r:<18} source={resolved.source}")

    print()
    print("The distinction is made by asking `'APP_MODEL_NAME' in environ`")
    print("rather than `os.environ.get('APP_MODEL_NAME')`. `.get` returns None")
    print("for a variable that was never set and '' for one that was set to")
    print("nothing, and the usual `or default` idiom then collapses both to the")
    print("default:")
    print()
    print('    name = os.environ.get("APP_MODEL_NAME") or "tiny-baseline"')
    print()
    print("That line cannot express 'the operator deliberately blanked this'.")
    print("It matters because an empty variable is almost never an accident —")
    print("it is a deployment template that filled in nothing, a secret that")
    print("failed to inject, or a person who meant to clear a value. Silently")
    print("treating it as 'unset' hides all three.")
    print()
    print("For an int setting the empty string is not a value at all, and the")
    print("resolver says so rather than guessing:")
    try:
        resolve(APP_SPEC, argv=[], environ={"APP_BATCH_SIZE": ""})
    except ConfigError as error:
        print(f"    {error}")


def demo_validation() -> None:
    banner("5. Validating at startup, so nothing fails at 3 a.m.")

    print("A bad configuration value has two possible moments of discovery:")
    print("the second the process starts, or the first time the code path that")
    print("uses it runs — which may be hours later, in the middle of the night,")
    print("halfway through a job. Validation at startup chooses the first.")
    print()

    config = resolve(
        APP_SPEC,
        argv=["--batch-size", "0", "--log-level", "VERBOSE"],
        environ={"APP_SEED": "-1"},
        config_path=CONFIG_FILE,
    )
    problems = validate(config, APP_SPEC)
    print(f"  {len(problems)} problems found, all of them at once:")
    for problem in problems:
        print(f"    - {problem}")

    print()
    print("Two design decisions in those messages.")
    print()
    print("They are reported ALL AT ONCE rather than one per run, because")
    print("fixing configuration one error at a time is miserable and pushes")
    print("people towards guessing.")
    print()
    print("And every one names its PROVENANCE. 'batch_size must be at least 1'")
    print("tells you what is wrong. 'batch_size: 0 is below the minimum of 1")
    print("(from flag:--batch-size)' tells you where to go and change it. The")
    print("second message costs one extra field on a dataclass.")
    print()
    print("A good configuration then passes silently:")
    good = resolve(
        APP_SPEC,
        argv=["--batch-size", "128"],
        environ={"APP_SEED": "7"},
        config_path=CONFIG_FILE,
    )
    validate_or_die(good, APP_SPEC)
    print("    validate_or_die() returned; the program may start.")

    print()
    print("And a required secret that is absent is a configuration error too,")
    print("not a runtime surprise. Adding one rule to the spec:")
    required_key = Setting(
        name="api_key", kind="str", default="", env="APP_API_KEY",
        flag=None, secret=True, help="credential",
    )
    empty = resolve([required_key], argv=[], environ={})
    if not empty["api_key"]:
        print("    api_key: not set. Set APP_API_KEY in the environment.")
        print("    (the message names the variable and never the value)")


def main() -> None:
    demo_precedence()
    demo_provenance()
    demo_types()
    demo_missing_versus_empty()
    demo_validation()
    print()
    print("=" * 70)
    print("Configuration demonstration complete.")


if __name__ == "__main__":
    main()
