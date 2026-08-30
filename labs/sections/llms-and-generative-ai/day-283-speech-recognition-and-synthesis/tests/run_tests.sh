#!/usr/bin/env bash
set -e
export PYTHONPATH=examples:.
PYTEST="${PYTEST:-pytest}"
$PYTEST tests/test_speech_pipeline.py -v
