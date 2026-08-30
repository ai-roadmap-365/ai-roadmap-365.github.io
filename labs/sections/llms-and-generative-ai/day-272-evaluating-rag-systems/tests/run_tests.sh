#!/usr/bin/env bash
set -e
export PYTHONPATH="$(cd "$(dirname "$0")/.." && pwd)/examples"
python3 tests/test_rag_eval_systems_lib.py
