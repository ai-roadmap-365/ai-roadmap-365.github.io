"""Shared helpers for building, executing and inspecting notebooks.

Every function here works on in-memory ``nbformat`` notebook objects.
Nothing in this module writes a notebook file to disk -- the tests build
notebooks in memory, execute them with real Jupyter kernels through
``nbclient``, and assert on the resulting JSON structure. That is how you
test a notebook without a UI.
"""

from __future__ import annotations

import copy
import sys
from typing import Iterable

import nbclient
import nbconvert
import nbformat as nbf
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError


def analyst_notebook() -> nbf.NotebookNode:
    """Build the three-cell notebook the lesson opens with.

    Cell 0 ("setup") sets ``x``. Cell 1 ("transform") is a cleaning step
    an analyst adds after already having looked at the answer once. Cell
    2 ("report") divides ``x`` by two and displays it. Run top to bottom
    the answer is 30.0; run in the order an analyst really used --
    setup, then a quick look at the report, then the transform, without
    ever re-running the report -- the notebook still displays a number
    with no error, and that number is wrong.
    """
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_code_cell("x = 100  # setup", id="setup"),
        nbf.v4.new_code_cell(
            "x = x - 40  # a cleaning step added after the first look at the report",
            id="transform",
        ),
        nbf.v4.new_code_cell("answer = x / 2\nanswer", id="report"),
    ]
    return nb


def execute_clean(nb: nbf.NotebookNode) -> nbf.NotebookNode:
    """Execute every cell top to bottom in a fresh kernel and return it."""
    nb = copy.deepcopy(nb)
    NotebookClient(nb, kernel_name="python3").execute()
    return nb


def execute_in_order(nb: nbf.NotebookNode, order: Iterable[int]) -> nbf.NotebookNode:
    """Execute the cells of ``nb`` in ``order`` (a sequence of cell indices).

    A single kernel is started once and reused across every cell in
    ``order``, exactly like clicking "Run" on cells in whatever sequence
    an analyst actually clicks them, rather than in document order.
    """
    nb = copy.deepcopy(nb)
    client = NotebookClient(nb, kernel_name="python3")
    with client.setup_kernel():
        for index in order:
            client.execute_cell(nb.cells[index], index)
    return nb


def final_value(nb: nbf.NotebookNode, cell_index: int) -> str:
    """Return the ``text/plain`` payload of a cell's last execute_result."""
    outputs = nb.cells[cell_index].get("outputs", [])
    for output in reversed(outputs):
        if output.get("output_type") == "execute_result":
            return output["data"]["text/plain"]
    raise AssertionError(f"cell {cell_index} has no execute_result output")


def execution_counts(nb: nbf.NotebookNode) -> list:
    return [cell.get("execution_count") for cell in nb.cells]


def is_monotonic(counts: list) -> bool:
    """True if every non-None count strictly increases with cell position."""
    seen = [c for c in counts if c is not None]
    return seen == sorted(seen) and len(seen) == len(set(seen))


def hidden_state_pair() -> tuple:
    """Build the two cells behind the hidden-state exercise.

    ``cell_defining`` sets a helper value. ``cell_using`` depends on it
    but does not define it. In the story, ``cell_defining`` is the cell an
    analyst deletes from the document once its job looks done -- while
    the kernel process, if it was never restarted, still remembers the
    value it set.
    """
    cell_defining = nbf.v4.new_code_cell(
        "helper_value = 42  # a cell that will be deleted from the document"
    )
    cell_using = nbf.v4.new_code_cell("total = helper_value + 8\ntotal")
    return cell_defining, cell_using


def run_in_dirty_kernel_after_deletion(cell_defining, cell_using) -> nbf.NotebookNode:
    """Run both cells, delete the defining cell from the document, rerun
    the remaining cell in the *same, still-alive* kernel, and return the
    notebook as it now stands on disk: one cell, whose variable the
    document itself never defines.
    """
    nb = nbf.v4.new_notebook()
    nb.cells = [copy.deepcopy(cell_defining), copy.deepcopy(cell_using)]
    client = NotebookClient(nb, kernel_name="python3")
    with client.setup_kernel():
        client.execute_cell(nb.cells[0], 0)
        client.execute_cell(nb.cells[1], 1)
        # Simulate deleting the defining cell from the document. The
        # kernel process behind `client` is untouched by this -- only the
        # notebook's list of cells changes.
        nb.cells = [nb.cells[1]]
        client.execute_cell(nb.cells[0], 0)
    return nb


def run_fresh_kernel(nb: nbf.NotebookNode) -> nbf.NotebookNode:
    """Execute ``nb`` (as it stands, with whatever cells it currently has)
    in a brand-new kernel that has no memory of any earlier session.
    """
    nb = copy.deepcopy(nb)
    NotebookClient(nb, kernel_name="python3").execute()
    return nb


def failing_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_code_cell("row_count = 12"),
        nbf.v4.new_code_cell("raise ValueError('row_count below the expected minimum')"),
        nbf.v4.new_code_cell("row_count * 2"),
    ]
    return nb


def strip_outputs(nb: nbf.NotebookNode) -> nbf.NotebookNode:
    """Return a deep copy with outputs, execution_count and the
    per-execution timestamp metadata removed -- the same three fields an
    ``nbstripout``-style pre-commit hook clears before a notebook is
    committed.
    """
    nb = copy.deepcopy(nb)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
            cell["metadata"].pop("execution", None)
    return nb


def parameters_notebook(threshold: int) -> nbf.NotebookNode:
    """Build a notebook with a papermill-style parameters cell.

    Cell 0 is tagged ``parameters`` and carries the default. Cell 1 is
    the *injected-parameters* cell papermill adds immediately after it
    -- papermill never edits the parameters cell itself, it appends a
    new cell that overrides the default, so the original default stays
    visible in the document. Cells 2 and 3 are the unchanged analysis:
    they never mention ``threshold``'s value directly and are identical
    text across every variant.
    """
    nb = nbf.v4.new_notebook()
    default_cell = nbf.v4.new_code_cell("threshold = 10  # default")
    default_cell["metadata"]["tags"] = ["parameters"]
    injected_cell = nbf.v4.new_code_cell(f"# Parameters\nthreshold = {threshold}\n")
    injected_cell["metadata"]["tags"] = ["injected-parameters"]
    nb.cells = [
        default_cell,
        injected_cell,
        nbf.v4.new_code_cell("data = [3, 12, 7, 15, 2]"),
        nbf.v4.new_code_cell("filtered = [d for d in data if d > threshold]\nfiltered"),
    ]
    return nb


def to_markdown(nb: nbf.NotebookNode) -> str:
    """Convert an executed notebook to Markdown with nbconvert."""
    exporter = nbconvert.MarkdownExporter()
    body, _resources = exporter.from_notebook_node(nb)
    return body


def to_html(nb: nbf.NotebookNode) -> str:
    exporter = nbconvert.HTMLExporter()
    exporter.template_name = "basic"
    body, _resources = exporter.from_notebook_node(nb)
    return body


def to_script(nb: nbf.NotebookNode) -> str:
    exporter = nbconvert.PythonExporter()
    body, _resources = exporter.from_notebook_node(nb)
    return body


def record_environment() -> dict:
    """What a reproducible notebook should record about the kernel that
    ran it: the interpreter version and the exact versions of the
    packages the notebook stack itself depends on.
    """
    return {
        "python_version": sys.version.split()[0],
        "nbformat": nbf.__version__,
        "nbclient": nbclient.__version__,
        "nbconvert": nbconvert.__version__,
    }


def environment_cell_notebook() -> nbf.NotebookNode:
    """A one-cell notebook that records its own environment when run."""
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_code_cell(
            "import sys, nbformat, nbclient, nbconvert\n"
            "record = {\n"
            "    'python_version': sys.version.split()[0],\n"
            "    'nbformat': nbformat.__version__,\n"
            "    'nbclient': nbclient.__version__,\n"
            "    'nbconvert': nbconvert.__version__,\n"
            "}\n"
            "record"
        )
    ]
    return nb


CellExecutionError = CellExecutionError  # re-exported for the tests
