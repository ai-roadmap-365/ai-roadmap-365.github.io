#!/usr/bin/env bash
set -e
export PYTHONPATH=examples:.
if [ -n "$PYTEST" ]; then
    $PYTEST tests/test_*.py -v
elif command -v pytest &> /dev/null; then
    pytest tests/test_*.py -v
else
    python3 -m unittest discover -s tests -p 'test_*.py' -v
fi
