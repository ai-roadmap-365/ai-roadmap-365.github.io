#!/usr/bin/env bash
# Run the day 362 documentation check test suite.
# Offline, standard library plus pytest. No network, no API key.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
