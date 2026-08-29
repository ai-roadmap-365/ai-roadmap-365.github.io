"""Print what your application promises, and check it for a leak.

    python3 starter/schema.py

This is Exercise 8. FastAPI builds this document from your annotations —
you never write it — and it is the same document `/openapi.json` serves and
the same document the interactive `/docs` page renders. A machine-readable
contract is the entire point of declaring types at the boundary: another
program can read this and generate a client, or a test, or a tool
definition, without a human explaining anything.

The last line is the leak check. If `owner_token` appears in the output
schema, some handler is returning the stored object without a
`response_model` to filter it.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

warnings.filterwarnings(
    "ignore", message="Using `httpx` with `starlette.testclient` is deprecated"
)

from app import app  # noqa: E402


def main() -> int:
    schema = app.openapi()

    print(f"OpenAPI version : {schema['openapi']}")
    print(f"Title / version : {schema['info']['title']} {schema['info']['version']}")

    print("\nPaths and the status codes each one declares:")
    for path in sorted(schema["paths"]):
        for method in sorted(schema["paths"][path]):
            codes = ", ".join(sorted(schema["paths"][path][method]["responses"]))
            print(f"  {method.upper():7} {path:28} -> {codes}")

    print("\nComponent schemas:", ", ".join(sorted(schema["components"]["schemas"])))

    out = schema["components"]["schemas"].get("BookmarkOut")
    if out is None:
        print("\nNo BookmarkOut schema yet — Exercise 2 creates it.")
        return 0

    fields = sorted(out["properties"])
    print("BookmarkOut fields:", ", ".join(fields))
    if "owner_token" in fields:
        print("\nLEAK: owner_token is part of the public output schema.")
        return 1
    print("\nNo leak: owner_token is stored but never declared as output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
