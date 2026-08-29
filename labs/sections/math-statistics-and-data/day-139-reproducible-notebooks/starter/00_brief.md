# Notebooks that reproduce — nine exercises

`nb_lib.py` and `calc.py` are complete and working: they are the
machinery, not the exercise. Your work is entirely in
`test_notebooks.py`, where each of the nine functions below is a
`pytest.skip("...")` naming exactly what to build and assert. Replace
each skip with real code and real assertions. `test_calc.py` is already
solved and passing — read it first, since it is exercise 8's other half.

Every notebook in this lab is built with `nbformat`, executed with a real
Jupyter kernel through `nbclient`, and inspected as JSON. Nothing here
opens a browser or a `.ipynb` file in an editor.

1. **Out-of-order changes the answer.** `nb_lib.analyst_notebook()` gives
   you a three-cell notebook: `setup` sets `x`, `transform` corrects it,
   `report` divides by two. Execute it top to bottom with
   `nb_lib.execute_clean`, then execute the *same* notebook in the order
   `[0, 2, 1]` with `nb_lib.execute_in_order` — the order an analyst uses
   when they check the report once, then add a cleaning step and never
   look again. Assert the two final answers (`nb_lib.final_value`,
   cell 2) differ, and report both.
2. **`execution_count` is the evidence.** From the same scrambled run,
   assert `nb_lib.execution_counts(...)` is non-monotonic
   (`not nb_lib.is_monotonic(...)`). From a clean run, assert the counts
   are `[1, 2, 3]` and monotonic.
3. **Hidden state.** `nb_lib.hidden_state_pair()` gives you two cells:
   one defines `helper_value`, the other uses it without defining it.
   `nb_lib.run_in_dirty_kernel_after_deletion(cell_defining, cell_using)`
   runs both, deletes the defining cell from the document, and reruns
   the remaining cell *in the same kernel process*. Assert that succeeds.
   Then run the resulting one-cell notebook in a brand-new kernel with
   `nb_lib.run_fresh_kernel` and assert it raises
   `nb_lib.CellExecutionError` with `.ename == "NameError"`.
4. **Execution as a test.** `nb_lib.failing_notebook()` has a cell that
   raises `ValueError`. Assert `nb_lib.execute_clean` raises
   `nb_lib.CellExecutionError`, that `.ename == "ValueError"`, and that
   the failing cell is named in the exception text (look for `"In[2]"`
   and the raising line in `str(error)`).
5. **Output stripping.** Execute `nb_lib.analyst_notebook()` twice with
   `nb_lib.execute_clean` (two independent runs). Assert the two
   unstripped notebooks (`nbformat.writes(...)`) are *not* equal. Assert
   that after `nb_lib.strip_outputs` on both, they *are* equal. Then
   inspect what actually differs between the unstripped pair — is it
   `execution_count`, or something else? Assert on the field name(s) you
   find, not on what you expect to find.
6. **Parameterisation.** Build two variants with
   `nb_lib.parameters_notebook(threshold=10)` and
   `nb_lib.parameters_notebook(threshold=5)`, execute both, and assert
   the final filtered lists (cell 3) differ as expected. Assert the
   non-parameter cells (0, 2, 3 — cell 0 is the untouched default) are
   character-identical text between variants, and only cell 1 (the
   injected-parameters cell) differs.
7. **Conversion.** Build a two-cell notebook: one markdown cell with a
   sentence of prose, one code cell that computes a number. Execute it,
   convert it with `nb_lib.to_markdown`, and assert both the prose
   sentence and the computed value appear in the resulting text.
8. **Notebook versus module.** Call `calc.clean_mean` directly and assert
   it works (it is already covered by `test_calc.py` — that is exercise
   8's point, not something to prove again here). Then build a one-cell
   notebook with the *same logic inlined*, execute it, and assert the
   inlined version also computes the right number inside the kernel.
   Finally assert that `importlib.import_module("some_name_for_that_cell")`
   raises `ModuleNotFoundError` — the module route is reachable by
   `pytest`; the inlined cell, structurally, is not.
9. **Environment record.** Execute `nb_lib.environment_cell_notebook()`
   and assert its recorded output contains the live
   `nb_lib.record_environment()` values (Python version, plus
   `nbformat`/`nbclient`/`nbconvert` versions). Then build a stand-in for
   an older pin manifest with one version changed, and assert it differs
   from the live record at exactly that key.

Run `.venv/bin/pytest starter -v` as you go; each skip message names the
one thing to assert next.
