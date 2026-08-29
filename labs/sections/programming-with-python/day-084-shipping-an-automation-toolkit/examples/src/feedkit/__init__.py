"""feedkit — a small, installable, scheduled automation toolkit.

The package is deliberately layered so that the boundaries sit at the edges:

    core            pure data in, pure data out — no network, no clock, no disk
    config          the four-layer precedence, resolved by a pure function
    logging_setup   structured JSON logging with secret redaction
    state           the state file, written atomically, plus the run lock
    adapters        the network and the clock — the only impure module
    runner          the order of one unattended run
    cli             argparse subcommands and the two console entry points

Read `core.py` first. It is where the interesting decisions live, and it is
readable without knowing anything about HTTP.
"""

__all__ = ["__version__"]

__version__ = "1.0.0"
