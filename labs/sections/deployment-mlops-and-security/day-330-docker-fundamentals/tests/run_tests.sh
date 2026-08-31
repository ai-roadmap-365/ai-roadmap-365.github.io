#!/usr/bin/env bash
# Run the day 330 layer-cache test suite.
# Offline, standard library plus pytest. Docker is not required.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
