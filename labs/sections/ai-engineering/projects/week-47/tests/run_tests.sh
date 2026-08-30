#!/usr/bin/env bash
# Run the week 47 project test suite.
# Offline, standard library plus pytest. No network, no API key.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
