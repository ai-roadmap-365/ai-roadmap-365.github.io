#!/usr/bin/env bash
set -e
export PYTHONPATH="$(cd "$(dirname "$0")/.." && pwd)/examples"
python3 tests/test_advanced_rag_lib.py
