#!/usr/bin/env bash
set -e
export PYTHONPATH=examples:.
PYTEST="${PYTEST:-pytest}"
$PYTEST tests/test_customization_decision_engine.py -v
