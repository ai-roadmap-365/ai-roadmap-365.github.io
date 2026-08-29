"""Make this directory's own modules the ones its tests import.

Both `examples/` and `starter/` contain modules called `experiment` and
`dataset`, and pytest imports test files by putting their directory on
`sys.path`. Without this file, running pytest across both directories at
once would import whichever copy was seen first and reuse it for the other
-- so the starter tests could silently import the REFERENCE solution and
report unwritten exercises as passing. Each directory's own copy of this
file prevents that.
"""

import sys
from pathlib import Path

HERE = str(Path(__file__).parent.resolve())

if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)

for name in ("experiment", "dataset"):
    module = sys.modules.get(name)
    origin = getattr(module, "__file__", "") or ""
    if module is not None and not origin.startswith(HERE):
        del sys.modules[name]
