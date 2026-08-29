"""Nine exercises in notebooks that reproduce.

Read `00_brief.md` first. Each function below is a `pytest.skip` naming
what to build and assert; replace the skip with real code. `nb_lib.py`
and `calc.py` are complete -- they are the machinery, not the exercise.
"""

import importlib
import sys

import nbformat as nbf
import pytest

import nb_lib
from nb_lib import CellExecutionError
from calc import clean_mean


def test_01_out_of_order_changes_the_answer():
    pytest.skip(
        "Execute nb_lib.analyst_notebook() clean (top to bottom) and in "
        "order [0, 2, 1]. Assert the two final answers (cell 2, via "
        "nb_lib.final_value) differ, and print both."
    )


def test_02_execution_count_is_the_evidence():
    pytest.skip(
        "From the scrambled run in exercise 1, assert "
        "nb_lib.execution_counts(...) is not monotonic. From the clean "
        "run, assert the counts are [1, 2, 3] and are monotonic."
    )


def test_03_hidden_state_survives_cell_deletion_in_a_dirty_kernel():
    pytest.skip(
        "Use nb_lib.hidden_state_pair() and "
        "nb_lib.run_in_dirty_kernel_after_deletion(...). Assert the "
        "one-cell result succeeds in the dirty kernel. Then run it "
        "through nb_lib.run_fresh_kernel and assert it raises "
        "CellExecutionError with .ename == 'NameError'."
    )


def test_04_nbclient_raises_on_a_failing_cell_and_names_it():
    pytest.skip(
        "Execute nb_lib.failing_notebook() and assert nb_lib.execute_clean "
        "raises CellExecutionError with .ename == 'ValueError', and that "
        "'In[2]' plus the raising line appear in str(error)."
    )


def test_05_stripping_outputs_makes_two_runs_identical():
    pytest.skip(
        "Execute nb_lib.analyst_notebook() twice independently. Assert "
        "the two unstripped notebooks (nbformat.writes) differ, and that "
        "nb_lib.strip_outputs on both makes them equal. Then find and "
        "assert exactly which field(s) differ between the unstripped pair."
    )


def test_06_parameterised_variants_differ_with_identical_code_cells():
    pytest.skip(
        "Build nb_lib.parameters_notebook(threshold=10) and threshold=5, "
        "execute both, and assert cell 3's filtered list differs as "
        "expected. Assert cells 0, 2 and 3 are identical text across "
        "variants and only cell 1 (injected-parameters) differs."
    )


def test_07_convert_to_markdown_carries_prose_and_computed_values():
    pytest.skip(
        "Build a two-cell notebook (one markdown cell of prose, one code "
        "cell computing a number), execute it, convert with "
        "nb_lib.to_markdown, and assert both the prose and the computed "
        "value appear in the result."
    )


def test_08_module_logic_is_covered_a_notebook_cell_is_not():
    pytest.skip(
        "Call calc.clean_mean directly and confirm it works (test_calc.py "
        "already covers it under pytest -- that is the point). Build a "
        "one-cell notebook with the same logic inlined, execute it, and "
        "assert it computes the right answer inside the kernel. Then "
        "assert importlib.import_module('some_name') raises "
        "ModuleNotFoundError for a name that only ever existed as a cell."
    )


def test_09_notebook_records_its_own_environment():
    pytest.skip(
        "Execute nb_lib.environment_cell_notebook() and assert its output "
        "contains the values from nb_lib.record_environment() (Python "
        "version, nbformat/nbclient/nbconvert versions). Build a stand-in "
        "for an older pin manifest with one version changed and assert it "
        "differs from the live record at exactly that key."
    )
