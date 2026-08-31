#!/usr/bin/env bash
# Run the day 335 CI pipeline test suite.
# Offline, standard library plus pytest. No runner and no GitHub account.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests -q "$@"
