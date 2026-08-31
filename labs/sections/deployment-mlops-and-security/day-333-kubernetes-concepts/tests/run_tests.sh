#!/usr/bin/env bash
# Run the day 333 reconciliation test suite.
# Offline, standard library plus pytest. No cluster is required.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
