#!/usr/bin/env bash
# Run the day 334 hosting-cost test suite.
# Offline, standard library plus pytest. No cloud account, no spending.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
