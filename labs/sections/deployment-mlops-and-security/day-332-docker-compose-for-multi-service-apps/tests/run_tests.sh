#!/usr/bin/env bash
# Run the day 332 compose-graph test suite.
# Offline, standard library plus pytest. Docker Compose is not required.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
