#!/usr/bin/env bash
# Build wordtally-tools, look inside both artifacts, install the wheel into a
# throwaway environment, and run the installed command.
#
# Run from the LAB directory:
#   bash examples/build_and_inspect.sh
#
# Everything happens under workspace/, which is disposable and is not tracked
# by version control. Nothing is uploaded anywhere: the only `pip install` here
# passes --no-index, which forbids pip from contacting any index at all.
set -eu

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="${lab_dir}/workspace"
project="${work}/demo"

# Resolve python and build the same way tests/run_tests.sh does.
python_bin=""
for candidate in "${PYTHON:-}" "${lab_dir}/.venv/bin/python" "$(command -v python3 || true)"; do
  if [ -n "${candidate}" ] && [ -x "${candidate}" ]; then python_bin="${candidate}"; break; fi
done
if [ -z "${python_bin}" ]; then
  echo "python3 not found. Install Python 3.10 or newer and try again." >&2
  exit 1
fi
if ! "${python_bin}" -c "import build" >/dev/null 2>&1; then
  echo "The 'build' package is not installed for ${python_bin}." >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

rm -rf "${project}"
mkdir -p "${work}"
cp -R "${lab_dir}/examples/wordtally-tools" "${project}"
cd "${project}"

echo "=== 1. Build both artifacts ================================================"
# --no-isolation reuses the setuptools already installed here instead of
# creating a fresh environment and downloading one. That keeps this script
# offline and repeatable. A real release uses plain `python -m build`.
"${python_bin}" -m build --no-isolation
echo
ls -1 dist/

echo
echo "=== 2. The sdist: a source snapshot ========================================"
tar -tzf dist/wordtally_tools-0.3.1.tar.gz

echo
echo "=== 3. The wheel: a built artifact, and just a zip =========================="
unzip -l dist/wordtally_tools-0.3.1-py3-none-any.whl

echo
echo "=== 4. The metadata the index would display ================================"
unzip -p dist/wordtally_tools-0.3.1-py3-none-any.whl \
  wordtally_tools-0.3.1.dist-info/METADATA | sed -n '1,22p'

echo
echo "=== 5. The console script declaration ======================================"
unzip -p dist/wordtally_tools-0.3.1-py3-none-any.whl \
  wordtally_tools-0.3.1.dist-info/entry_points.txt

echo
echo "=== 6. Install the wheel into a fresh, throwaway environment ==============="
rm -rf "${work}/tryout"
"${python_bin}" -m venv "${work}/tryout"
"${work}/tryout/bin/pip" install --no-index --disable-pip-version-check -q \
  "${project}/dist/wordtally_tools-0.3.1-py3-none-any.whl"
echo "installed:"
"${work}/tryout/bin/pip" list --disable-pip-version-check --format=freeze | grep -i wordtally

echo
echo "=== 7. Run the installed COMMAND ==========================================="
cp "${lab_dir}/examples/sample.txt" "${project}/sample.txt"
"${work}/tryout/bin/wordtally" --version
"${work}/tryout/bin/wordtally" count sample.txt
"${work}/tryout/bin/wordtally" top sample.txt -n 3

echo
echo "=== 8. Where did the import come from? ====================================="
echo "standing in: $(pwd)"
"${work}/tryout/bin/python" -c "import wordtally; print(wordtally.__file__)"
echo "That path is inside the environment, not inside this directory."
echo "src layout is what guarantees it."

echo
echo "Done. Remove everything with:  rm -rf ${work}"
