#!/bin/bash
set -e
PYTHONPATH="$(cd "$(dirname "$0")/.." && pwd)/examples" pytest examples/ -v
