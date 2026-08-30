#!/usr/bin/env bash
set -e
export PYTHONPATH="$(cd "$(dirname "$0")/.." && pwd)/examples"
python3 tests/test_pdf_document_rag_lib.py
