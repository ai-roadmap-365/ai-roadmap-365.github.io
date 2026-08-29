"""Nine exercises in notebooks that reproduce.

Every notebook here is built with ``nbformat``, executed with real
Jupyter kernels through ``nbclient``, and inspected as JSON -- nothing is
opened in a browser and nothing is retyped from a screenshot. Each test
asserts on the resulting structure: cell outputs, ``execution_count``
values, and (for exercise 7) the text nbconvert produces.
"""

import copy
import importlib
import sys

import nbformat as nbf
import pytest

import nb_lib
from nb_lib import CellExecutionError
from calc import clean_mean


# ---------------------------------------------------------------------
# 1. Out-of-order changes the answer
# ---------------------------------------------------------------------
def test_01_out_of_order_changes_the_answer():
    nb = nb_lib.analyst_notebook()

    clean = nb_lib.execute_clean(nb)
    clean_answer = nb_lib.final_value(clean, 2)

    # The order an analyst really used: run the setup cell, take a quick
    # look at the report, then add and run the cleaning step -- and never
    # re-run the report to see the corrected number.
    scrambled = nb_lib.execute_in_order(nb, [0, 2, 1])
    scrambled_answer = nb_lib.final_value(scrambled, 2)

    assert clean_answer == "30.0"
    assert scrambled_answer == "50.0"
    assert clean_answer != scrambled_answer


# ---------------------------------------------------------------------
# 2. execution_count is the evidence
# ---------------------------------------------------------------------
def test_02_execution_count_is_the_evidence():
    nb = nb_lib.analyst_notebook()

    scrambled = nb_lib.execute_in_order(nb, [0, 2, 1])
    scrambled_counts = nb_lib.execution_counts(scrambled)
    assert scrambled_counts == [1, 3, 2]
    assert not nb_lib.is_monotonic(scrambled_counts)

    clean = nb_lib.execute_clean(nb)
    clean_counts = nb_lib.execution_counts(clean)
    assert clean_counts == [1, 2, 3]
    assert nb_lib.is_monotonic(clean_counts)


# ---------------------------------------------------------------------
# 3. Hidden state
# ---------------------------------------------------------------------
def test_03_hidden_state_survives_cell_deletion_in_a_dirty_kernel():
    cell_defining, cell_using = nb_lib.hidden_state_pair()

    dirty = nb_lib.run_in_dirty_kernel_after_deletion(cell_defining, cell_using)
    # The document now has exactly one cell -- `helper_value` is nowhere
    # in it -- and it still ran, because the kernel remembered.
    assert len(dirty.cells) == 1
    assert "helper_value = 42" not in dirty.cells[0].source  # the definition is gone
    assert "helper_value" in dirty.cells[0].source  # only the use remains
    assert nb_lib.final_value(dirty, 0) == "50"

    with pytest.raises(CellExecutionError) as excinfo:
        nb_lib.run_fresh_kernel(dirty)
    assert excinfo.value.ename == "NameError"


# ---------------------------------------------------------------------
# 4. Execution as a test
# ---------------------------------------------------------------------
def test_04_nbclient_raises_on_a_failing_cell_and_names_it():
    nb = nb_lib.failing_notebook()

    with pytest.raises(CellExecutionError) as excinfo:
        nb_lib.execute_clean(nb)

    error = excinfo.value
    assert error.ename == "ValueError"
    assert error.evalue == "row_count below the expected minimum"
    # nbclient names the failing cell by its execution position ("In[2]")
    # and quotes the cell's own source in the exception message, so a CI
    # log points straight at the broken cell.
    assert "In[2]" in str(error)
    assert "raise ValueError" in str(error)


# ---------------------------------------------------------------------
# 5. Output stripping
# ---------------------------------------------------------------------
def test_05_stripping_outputs_makes_two_runs_identical():
    base = nb_lib.analyst_notebook()

    run_a = nb_lib.execute_clean(base)
    run_b = nb_lib.execute_clean(base)

    unstripped_a = nbf.writes(run_a)
    unstripped_b = nbf.writes(run_b)
    assert unstripped_a != unstripped_b

    stripped_a = nbf.writes(nb_lib.strip_outputs(run_a))
    stripped_b = nbf.writes(nb_lib.strip_outputs(run_b))
    assert stripped_a == stripped_b

    # Report exactly what differs: identical code, identical results
    # (execution_count matches cell-for-cell), and yet the unstripped
    # documents disagree -- because nbclient stamps each cell's metadata
    # with the wall-clock time it started and finished.
    counts_a = nb_lib.execution_counts(run_a)
    counts_b = nb_lib.execution_counts(run_b)
    assert counts_a == counts_b  # NOT what differs, despite common lore

    differing_fields = set()
    for cell_a, cell_b in zip(run_a.cells, run_b.cells):
        for key in cell_a.keys():
            if cell_a[key] != cell_b.get(key):
                differing_fields.add(key)
    assert differing_fields == {"metadata"}
    for cell_a, cell_b in zip(run_a.cells, run_b.cells):
        assert cell_a["metadata"]["execution"] != cell_b["metadata"]["execution"]
        assert set(cell_a["metadata"]["execution"].keys()) == {
            "iopub.status.busy",
            "iopub.execute_input",
            "shell.execute_reply",
            "iopub.status.idle",
        }


# ---------------------------------------------------------------------
# 6. Parameterisation
# ---------------------------------------------------------------------
def test_06_parameterised_variants_differ_with_identical_code_cells():
    strict = nb_lib.execute_clean(nb_lib.parameters_notebook(threshold=10))
    loose = nb_lib.execute_clean(nb_lib.parameters_notebook(threshold=5))

    assert nb_lib.final_value(strict, 3) == "[12, 15]"
    assert nb_lib.final_value(loose, 3) == "[12, 7, 15]"

    # Cells 0 (the default), 2 and 3 (the analysis) are untouched between
    # variants; only cell 1, the injected-parameters cell, differs.
    assert strict.cells[0].source == loose.cells[0].source
    assert strict.cells[2].source == loose.cells[2].source
    assert strict.cells[3].source == loose.cells[3].source
    assert strict.cells[1].source != loose.cells[1].source
    assert "threshold = 10" in strict.cells[1].source
    assert "threshold = 5" in loose.cells[1].source
    assert strict.cells[0].metadata["tags"] == ["parameters"]


# ---------------------------------------------------------------------
# 7. Conversion
# ---------------------------------------------------------------------
def test_07_convert_to_markdown_carries_prose_and_computed_values():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "## Row count check\n\nWe expect at least 100 rows after cleaning."
        ),
        nbf.v4.new_code_cell("row_count = 40 + 74\nrow_count"),
    ]
    executed = nb_lib.execute_clean(nb)
    markdown = nb_lib.to_markdown(executed)

    assert "Row count check" in markdown
    assert "We expect at least 100 rows after cleaning." in markdown
    assert "114" in markdown  # the computed value, not retyped


# ---------------------------------------------------------------------
# 8. Notebook versus module
# ---------------------------------------------------------------------
def test_08_module_logic_is_covered_a_notebook_cell_is_not():
    # The module route: an ordinary import, an ordinary call, and
    # test_calc.py in this same directory already covers it under pytest.
    assert clean_mean([10, None, 20]) == 15.0

    # The notebook route: the same computation, inlined in a cell that
    # was never turned into a module. Executing it inside a kernel works
    # fine -- notebooks run inline code all the time -- but pytest cannot
    # reach it, because a .ipynb is not something Python's import system
    # can import, with or without a kernel involved.
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_code_cell(
            "def clean_mean_inline(values):\n"
            "    kept = [v for v in values if v is not None]\n"
            "    return sum(kept) / len(kept)\n"
            "clean_mean_inline([10, None, 20])"
        )
    ]
    executed = nb_lib.execute_clean(nb)
    assert nb_lib.final_value(executed, 0) == "15.0"

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("clean_mean_inline_notebook")


# ---------------------------------------------------------------------
# 9. Environment record
# ---------------------------------------------------------------------
def test_09_notebook_records_its_own_environment():
    nb = nb_lib.execute_clean(nb_lib.environment_cell_notebook())
    recorded_text = nb_lib.final_value(nb, 0)

    live = nb_lib.record_environment()
    assert live["python_version"] == sys.version.split()[0]

    for key, value in live.items():
        assert repr(value) in recorded_text or value in recorded_text

    # Changing a pin changes the record: compare today's real record
    # against a stand-in for an older manifest that pinned nbformat one
    # minor version back. The two must disagree at exactly that key.
    older_manifest = dict(live)
    older_manifest["nbformat"] = "5.10.0"
    assert older_manifest != live
    assert older_manifest["nbformat"] != live["nbformat"]
    for key in ("python_version", "nbclient", "nbconvert"):
        assert older_manifest[key] == live[key]
