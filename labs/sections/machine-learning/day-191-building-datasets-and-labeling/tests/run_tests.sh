#!/usr/bin/env bash
set -euo pipefail
echo "========================================"
echo "Running Day 191 Lab Test Suite"
echo "========================================"
pytest tests/ -v
echo "All tests passed successfully."
