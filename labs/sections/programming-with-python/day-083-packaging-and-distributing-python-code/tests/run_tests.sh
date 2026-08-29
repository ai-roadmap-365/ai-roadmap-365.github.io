#!/usr/bin/env bash
# Tests for the Day 083 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# What this suite proves, in order of how much it is worth:
#
#   * the INSTALLED package imports from the environment's site-packages and
#     not from the working directory, even while you are standing inside the
#     project. A flat-layout copy of the same project is built alongside it and
#     shown to do the opposite. That contrast is the entire argument for the
#     src layout, and it is the most valuable check here;
#   * a wheel is a zip: it is opened with unzip and its contents are asserted
#     file by file, including the metadata directory and the console-script
#     declaration;
#   * the sdist carries files the wheel deliberately omits;
#   * installing the wheel into a fresh environment produces a COMMAND that
#     runs and exits 0;
#   * the declared version appears in both artifact filenames;
#   * removing one required metadata field makes the build fail loudly.
#
# NOTHING IS UPLOADED ANYWHERE. Every install below passes --no-index, which
# forbids pip from contacting any package index, and the last section of this
# file checks that claim mechanically.
#
# Non-interactive and deterministic. Exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="${lab_dir}/workspace"
failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

# Resolve python: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping.
resolve_python() {
  if [ -n "${PYTHON:-}" ] && [ -x "${PYTHON}" ]; then echo "${PYTHON}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/python" ]; then echo "${lab_dir}/.venv/bin/python"; return 0; fi
  if command -v python3 >/dev/null 2>&1; then command -v python3; return 0; fi
  return 1
}

resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

python_bin="$(resolve_python)" || {
  echo "FAIL: python3 not found." >&2
  echo "  Install Python 3.10 or newer, or point this suite at one:" >&2
  echo "    PYTHON=/path/to/python3 bash tests/run_tests.sh" >&2
  exit 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install it with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

if ! "${python_bin}" -c "import build" >/dev/null 2>&1; then
  echo "FAIL: the 'build' package is not installed for ${python_bin}." >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

if ! "${python_bin}" -c "import setuptools" >/dev/null 2>&1; then
  echo "FAIL: setuptools is not installed for ${python_bin}." >&2
  echo "  This lab builds with --no-isolation so that it never needs a network." >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  exit 1
fi

for tool in unzip tar; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "FAIL: ${tool} not found on PATH; this suite opens the built artifacts with it." >&2
    exit 1
  fi
done

echo "Day 083 — Build a Real Package and Install It"
echo

rm -rf "${work}"
mkdir -p "${work}"
trap 'rm -rf "${work}"' EXIT

# --------------------------------------------------------------------------
echo "1. The tools"
# --------------------------------------------------------------------------

build_version="$("${python_bin}" -m build --version 2>&1 | head -1)"
case "${build_version}" in
  build\ *) check "python -m build --version reports a build ( ${build_version%% (*} )" "yes" ;;
  *) check "python -m build --version reports a build ( ${build_version} )" "no" ;;
esac

py_version="$("${python_bin}" --version 2>&1)"
case "${py_version}" in
  Python\ 3.1[0-9]*) check "python is 3.10 or newer ( ${py_version} )" "yes" ;;
  *) check "python is 3.10 or newer ( ${py_version} )" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "2. Building the reference project"
# --------------------------------------------------------------------------

project="${work}/demo"
cp -R "${lab_dir}/examples/wordtally-tools" "${project}"
build_log="${work}/build.log"
(cd "${project}" && "${python_bin}" -m build --no-isolation) >"${build_log}" 2>&1
build_exit=$?
if [ "${build_exit}" -eq 0 ]; then
  check "python -m build exits 0" "yes"
else
  check "python -m build exits 0 (got ${build_exit})" "no"
  tail -20 "${build_log}"
fi

sdist="${project}/dist/wordtally_tools-0.3.1.tar.gz"
wheel="${project}/dist/wordtally_tools-0.3.1-py3-none-any.whl"

artifact_count="$(ls -1 "${project}/dist" 2>/dev/null | wc -l | tr -d ' ')"
if [ "${artifact_count}" = "2" ]; then
  check "the build produces exactly two artifacts" "yes"
else
  check "the build produces exactly two artifacts (got ${artifact_count})" "no"
fi

[ -f "${sdist}" ] && check "an sdist is produced, and the declared version 0.3.1 is in its name" "yes" \
                 || check "an sdist is produced, and the declared version 0.3.1 is in its name" "no"
[ -f "${wheel}" ] && check "a wheel is produced, and the declared version 0.3.1 is in its name" "yes" \
                 || check "a wheel is produced, and the declared version 0.3.1 is in its name" "no"

# py3-none-any is the compatibility tag of a pure-Python wheel: any Python 3,
# no ABI requirement, any platform. A compiled project would say something far
# more specific here.
case "${wheel}" in
  *-py3-none-any.whl) check "the wheel carries the pure-Python tag py3-none-any" "yes" ;;
  *) check "the wheel carries the pure-Python tag py3-none-any" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "3. A wheel is a zip — open it and look"
# --------------------------------------------------------------------------

if unzip -t "${wheel}" >/dev/null 2>&1; then
  check "unzip -t accepts the wheel: it is a valid zip archive" "yes"
else
  check "unzip -t accepts the wheel: it is a valid zip archive" "no"
fi

wheel_list="$(unzip -Z1 "${wheel}" 2>/dev/null)"

for entry in \
  "wordtally/__init__.py" \
  "wordtally/core.py" \
  "wordtally/cli.py" \
  "wordtally/data/stopwords.txt" \
  "wordtally_tools-0.3.1.dist-info/METADATA" \
  "wordtally_tools-0.3.1.dist-info/WHEEL" \
  "wordtally_tools-0.3.1.dist-info/RECORD" \
  "wordtally_tools-0.3.1.dist-info/entry_points.txt" \
  "wordtally_tools-0.3.1.dist-info/licenses/LICENSE"
do
  if printf '%s\n' "${wheel_list}" | grep -qx "${entry}"; then
    check "the wheel contains ${entry}" "yes"
  else
    check "the wheel contains ${entry}" "no"
  fi
done

# The wheel is an INSTALL image. It carries no build instructions and no tests.
for absent in "pyproject.toml" "MANIFEST.in" "tests/test_core.py" "src/wordtally/core.py"
do
  if printf '%s\n' "${wheel_list}" | grep -qx "${absent}"; then
    check "the wheel deliberately omits ${absent}" "no"
  else
    check "the wheel deliberately omits ${absent}" "yes"
  fi
done

metadata="$(unzip -p "${wheel}" wordtally_tools-0.3.1.dist-info/METADATA 2>/dev/null)"
for line in \
  "Name: wordtally-tools" \
  "Version: 0.3.1" \
  "Requires-Python: >=3.10" \
  "License-Expression: MIT" \
  "Provides-Extra: dev" \
  "Summary: Count and rank the words in a text file"
do
  if printf '%s\n' "${metadata}" | grep -q "^${line}"; then
    check "METADATA declares ${line}" "yes"
  else
    check "METADATA declares ${line}" "no"
  fi
done

# The extra's dependency is recorded conditionally: a plain install skips it.
if printf '%s\n' "${metadata}" | grep -q 'Requires-Dist: pytest>=8; extra == "dev"'; then
  check "the dev extra's dependency is recorded as conditional on the extra" "yes"
else
  check "the dev extra's dependency is recorded as conditional on the extra" "no"
fi

entry_points="$(unzip -p "${wheel}" wordtally_tools-0.3.1.dist-info/entry_points.txt 2>/dev/null)"
if printf '%s\n' "${entry_points}" | grep -q '^\[console_scripts\]'; then
  check "entry_points.txt declares a console_scripts group" "yes"
else
  check "entry_points.txt declares a console_scripts group" "no"
fi
if printf '%s\n' "${entry_points}" | grep -q '^wordtally = wordtally.cli:main$'; then
  check "the console script maps the name wordtally to wordtally.cli:main" "yes"
else
  check "the console script maps the name wordtally to wordtally.cli:main" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The sdist carries what the wheel does not"
# --------------------------------------------------------------------------

sdist_list="$(tar -tzf "${sdist}" 2>/dev/null)"

for entry in \
  "wordtally_tools-0.3.1/pyproject.toml" \
  "wordtally_tools-0.3.1/MANIFEST.in" \
  "wordtally_tools-0.3.1/README.md" \
  "wordtally_tools-0.3.1/LICENSE" \
  "wordtally_tools-0.3.1/PKG-INFO" \
  "wordtally_tools-0.3.1/tests/test_core.py" \
  "wordtally_tools-0.3.1/tests/test_cli.py" \
  "wordtally_tools-0.3.1/src/wordtally/core.py" \
  "wordtally_tools-0.3.1/src/wordtally/data/stopwords.txt"
do
  if printf '%s\n' "${sdist_list}" | grep -qx "${entry}"; then
    check "the sdist contains ${entry#wordtally_tools-0.3.1/}" "yes"
  else
    check "the sdist contains ${entry#wordtally_tools-0.3.1/}" "no"
  fi
done

# The three files the wheel does not have, named explicitly, because this is
# the difference the lesson is about.
for entry in "pyproject.toml" "MANIFEST.in" "tests/test_core.py"; do
  in_sdist="no"; in_wheel="no"
  printf '%s\n' "${sdist_list}" | grep -qx "wordtally_tools-0.3.1/${entry}" && in_sdist="yes"
  printf '%s\n' "${wheel_list}" | grep -qx "${entry}" && in_wheel="yes"
  if [ "${in_sdist}" = "yes" ] && [ "${in_wheel}" = "no" ]; then
    check "${entry} is in the sdist and not in the wheel" "yes"
  else
    check "${entry} is in the sdist and not in the wheel" "no"
  fi
done

# The sdist keeps the src/ prefix; the wheel has already flattened it away,
# because a wheel is unpacked straight into site-packages.
if printf '%s\n' "${sdist_list}" | grep -q '^wordtally_tools-0.3.1/src/wordtally/' \
   && ! printf '%s\n' "${wheel_list}" | grep -q '^src/'; then
  check "the sdist preserves the src/ prefix; the wheel has flattened it" "yes"
else
  check "the sdist preserves the src/ prefix; the wheel has flattened it" "no"
fi

# --------------------------------------------------------------------------
echo
echo "5. Install the wheel into a fresh environment"
# --------------------------------------------------------------------------

tryout="${work}/tryout"
"${python_bin}" -m venv "${tryout}" >/dev/null 2>&1
venv_exit=$?
if [ "${venv_exit}" -eq 0 ] && [ -x "${tryout}/bin/python" ]; then
  check "a fresh virtual environment is created" "yes"
else
  check "a fresh virtual environment is created (exit ${venv_exit})" "no"
fi

# Before installing, the environment knows nothing about this package.
if "${tryout}/bin/python" -c "import wordtally" >/dev/null 2>&1; then
  check "the fresh environment cannot import wordtally before installation" "no"
else
  check "the fresh environment cannot import wordtally before installation" "yes"
fi

# --no-index forbids pip from contacting any package index. The install is
# purely local, and it is offline by construction.
install_log="${work}/install.log"
"${tryout}/bin/pip" install --no-index --disable-pip-version-check -q "${wheel}" \
  >"${install_log}" 2>&1
install_exit=$?
if [ "${install_exit}" -eq 0 ]; then
  check "pip install --no-index of the wheel exits 0 (no index was contacted)" "yes"
else
  check "pip install --no-index of the wheel exits 0 (got ${install_exit})" "no"
  tail -20 "${install_log}"
fi

if [ -x "${tryout}/bin/wordtally" ]; then
  check "installing the wheel creates an executable named wordtally" "yes"
else
  check "installing the wheel creates an executable named wordtally" "no"
fi

# The generated launcher's first line points at the environment's interpreter,
# which is how a console script finds the right Python without a PATH game.
shebang="$(head -1 "${tryout}/bin/wordtally" 2>/dev/null)"
case "${shebang}" in
  \#\!*"/tryout/bin/python"*) check "the console script's shebang points at the environment's own python" "yes" ;;
  *) check "the console script's shebang points at the environment's own python (got ${shebang})" "no" ;;
esac

version_out="$("${tryout}/bin/wordtally" --version 2>&1)"
version_exit=$?
if [ "${version_exit}" -eq 0 ] && [ "${version_out}" = "wordtally 0.3.1" ]; then
  check "the installed command runs: wordtally --version prints 'wordtally 0.3.1', exit 0" "yes"
else
  check "the installed command runs: wordtally --version (got '${version_out}', exit ${version_exit})" "no"
fi

cp "${lab_dir}/examples/sample.txt" "${project}/sample.txt"
count_out="$(cd "${project}" && "${tryout}/bin/wordtally" count sample.txt 2>&1)"
count_exit=$?
if [ "${count_exit}" -eq 0 ] && [ "${count_out}" = "12" ]; then
  check "wordtally count sample.txt prints 12 and exits 0" "yes"
else
  check "wordtally count sample.txt prints 12 and exits 0 (got '${count_out}', exit ${count_exit})" "no"
fi

top_out="$(cd "${project}" && "${tryout}/bin/wordtally" top sample.txt -n 2 2>&1)"
top_exit=$?
expected_top="$(printf '     3  mat\n     1  cat')"
if [ "${top_exit}" -eq 0 ] && [ "${top_out}" = "${expected_top}" ]; then
  check "wordtally top sample.txt -n 2 ranks mat then cat, exit 0" "yes"
else
  check "wordtally top sample.txt -n 2 ranks mat then cat (got '${top_out}', exit ${top_exit})" "no"
fi

# `top` only works if the stop-word list was actually shipped inside the wheel.
if "${tryout}/bin/python" -c "from wordtally.core import load_stopwords; assert 'the' in load_stopwords()" >/dev/null 2>&1; then
  check "the packaged data file travelled inside the wheel and loads after install" "yes"
else
  check "the packaged data file travelled inside the wheel and loads after install" "no"
fi

# A bad exit code is as much a part of the interface as a good one.
missing_exit=0
(cd "${project}" && "${tryout}/bin/wordtally" count no-such-file.txt >/dev/null 2>&1) || missing_exit=$?
if [ "${missing_exit}" -eq 2 ]; then
  check "the installed command exits 2 on an unreadable file" "yes"
else
  check "the installed command exits 2 on an unreadable file (got ${missing_exit})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "6. src layout — the import came from the environment, not this directory"
# --------------------------------------------------------------------------

# Standing INSIDE the project, ask the installed interpreter where the package
# is. This is the check the whole lab exists for.
where="$(cd "${project}" && "${tryout}/bin/python" -c 'import wordtally; print(wordtally.__file__)' 2>&1)"
case "${where}" in
  "${tryout}"/lib/*/site-packages/wordtally/__init__.py)
    check "standing in the project, import wordtally resolves to the environment's site-packages" "yes" ;;
  *)
    check "standing in the project, import wordtally resolves to site-packages (got ${where})" "no" ;;
esac
case "${where}" in
  *"${project}"*)
    check "the resolved path is NOT inside the working directory" "no" ;;
  *)
    check "the resolved path is NOT inside the working directory" "yes" ;;
esac

# The contrast. Same code, same install, flat layout: the working-directory
# copy wins, and your tests stop testing what your users get.
flat="${work}/flat"
cp -R "${lab_dir}/examples/wordtally-tools" "${flat}"
mv "${flat}/src/wordtally" "${flat}/wordtally"
rmdir "${flat}/src"
flat_where="$(cd "${flat}" && "${tryout}/bin/python" -c 'import wordtally; print(wordtally.__file__)' 2>&1)"
case "${flat_where}" in
  "${flat}"/wordtally/__init__.py)
    check "in a FLAT layout the same import silently picks up the working-directory copy" "yes" ;;
  *)
    check "in a FLAT layout the same import picks up the working-directory copy (got ${flat_where})" "no" ;;
esac
if [ "${where}" != "${flat_where}" ]; then
  check "the two layouts resolve the same import to different files" "yes"
else
  check "the two layouts resolve the same import to different files" "no"
fi

# --------------------------------------------------------------------------
echo
echo "7. Distribution name versus import name"
# --------------------------------------------------------------------------

# You install `wordtally-tools`. You import `wordtally`. There is no module
# called `wordtally_tools` at all — the same split as beautifulsoup4 and bs4.
freeze="$("${tryout}/bin/pip" list --disable-pip-version-check --format=freeze 2>/dev/null)"
if printf '%s\n' "${freeze}" | grep -qi '^wordtally-tools=='; then
  check "pip lists the DISTRIBUTION name wordtally-tools" "yes"
else
  check "pip lists the DISTRIBUTION name wordtally-tools" "no"
fi
if "${tryout}/bin/python" -c "import wordtally" >/dev/null 2>&1; then
  check "the IMPORT name wordtally works after installation" "yes"
else
  check "the IMPORT name wordtally works after installation" "no"
fi
if "${tryout}/bin/python" -c "import wordtally_tools" >/dev/null 2>&1; then
  check "there is no module called wordtally_tools — the names genuinely differ" "no"
else
  check "there is no module called wordtally_tools — the names genuinely differ" "yes"
fi
meta_version="$("${tryout}/bin/python" -c 'from importlib.metadata import version; print(version("wordtally-tools"))' 2>&1)"
if [ "${meta_version}" = "0.3.1" ]; then
  check "importlib.metadata.version('wordtally-tools') returns 0.3.1 — the version is single-sourced" "yes"
else
  check "importlib.metadata.version('wordtally-tools') returns 0.3.1 (got ${meta_version})" "no"
fi
dunder_version="$("${tryout}/bin/python" -c 'import wordtally; print(wordtally.__version__)' 2>&1)"
if [ "${dunder_version}" = "0.3.1" ]; then
  check "wordtally.__version__ agrees, because it reads the same metadata" "yes"
else
  check "wordtally.__version__ agrees (got ${dunder_version})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "8. The package's own test suite"
# --------------------------------------------------------------------------

# Run against the project's source tree. The installed copy is byte-identical
# to it — the wheel was built from these files a few checks ago — and the
# `__file__` assertions in section 6 are what prove the installed copy is the
# one a user gets.
suite_out="$(cd "${project}" && PYTHONPATH="${project}/src" "${pytest_bin}" -q 2>&1)"
suite_exit=$?
if [ "${suite_exit}" -eq 0 ]; then
  check "the package's own pytest suite exits 0" "yes"
else
  check "the package's own pytest suite exits 0 (got ${suite_exit})" "no"
  printf '%s\n' "${suite_out}" | tail -20
fi
case "${suite_out}" in
  *"17 passed"*) check "the package's own suite reports 17 passed" "yes" ;;
  *) check "the package's own suite reports 17 passed" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "9. Missing required metadata makes the build fail"
# --------------------------------------------------------------------------

for field in name version; do
  broken="${work}/broken-${field}"
  cp -R "${lab_dir}/examples/wordtally-tools" "${broken}"
  grep -v "^${field} = " "${broken}/pyproject.toml" > "${broken}/pyproject.new"
  mv "${broken}/pyproject.new" "${broken}/pyproject.toml"
  if grep -q "^${field} = " "${broken}/pyproject.toml"; then
    check "the edit really removed the ${field} field" "no"
  else
    check "the edit really removed the ${field} field" "yes"
  fi
  broken_log="${work}/broken-${field}.log"
  (cd "${broken}" && "${python_bin}" -m build --no-isolation) >"${broken_log}" 2>&1
  broken_exit=$?
  if [ "${broken_exit}" -ne 0 ]; then
    check "building without a ${field} fails (exit ${broken_exit}, not 0)" "yes"
  else
    check "building without a ${field} fails — it did not, so the metadata is not enforced" "no"
  fi
  if grep -q "must contain \['name', 'version'\]" "${broken_log}" \
     || grep -q "must contain \['${field}'\]" "${broken_log}"; then
    check "the failure names the missing field rather than failing vaguely" "yes"
  else
    check "the failure names the missing field rather than failing vaguely" "no"
  fi
  if [ -d "${broken}/dist" ]; then
    check "a failed build produces no artifact for ${field}" "no"
  else
    check "a failed build produces no artifact for ${field}" "yes"
  fi
done

# --------------------------------------------------------------------------
echo
echo "10. The starter still has work in it"
# --------------------------------------------------------------------------

starter="${work}/starter"
cp -R "${lab_dir}/starter/wordtally-tools" "${starter}"
starter_log="${work}/starter.log"
(cd "${starter}" && "${python_bin}" -m build --no-isolation) >"${starter_log}" 2>&1
starter_exit=$?
if [ "${starter_exit}" -eq 0 ]; then
  check "the starter builds as shipped, so you can begin from a green state" "yes"
else
  check "the starter builds as shipped (got ${starter_exit})" "no"
  tail -20 "${starter_log}"
fi

starter_wheel="${starter}/dist/wordtally_tools-0.1.0-py3-none-any.whl"
if [ -f "${starter_wheel}" ] && [ -f "${starter}/dist/wordtally_tools-0.1.0.tar.gz" ]; then
  check "the starter's artifacts carry its own declared version, 0.1.0" "yes"
else
  check "the starter's artifacts carry its own declared version, 0.1.0" "no"
fi

starter_list="$(unzip -Z1 "${starter_wheel}" 2>/dev/null)"
if printf '%s\n' "${starter_list}" | grep -q 'entry_points.txt'; then
  check "the starter wheel has no console script yet — exercise 4 is real work" "no"
else
  check "the starter wheel has no console script yet — exercise 4 is real work" "yes"
fi
if printf '%s\n' "${starter_list}" | grep -q 'wordtally/data/stopwords.txt'; then
  check "the starter wheel omits the data file — exercise 5 is real work" "no"
else
  check "the starter wheel omits the data file — exercise 5 is real work" "yes"
fi

# The starter's exercises name the exact fields the finished file has, so a
# learner who follows them arrives somewhere real.
for field in "description" "readme" "requires-python" "license" "classifiers" "project.scripts" "package-data"; do
  if grep -q "${field}" "${lab_dir}/starter/wordtally-tools/pyproject.toml"; then
    check "the starter's exercises mention ${field}" "yes"
  else
    check "the starter's exercises mention ${field}" "no"
  fi
done

# --------------------------------------------------------------------------
echo
echo "11. Nothing is uploaded, and nothing is fetched"
# --------------------------------------------------------------------------

# This lab describes publishing and never performs it. That claim is checked
# here rather than merely asserted in prose.
lab_scripts="${lab_dir}/tests/run_tests.sh ${lab_dir}/examples/build_and_inspect.sh"

# metadata.yml is the complete list of commands this lab ever asks anyone to
# run. If publishing happened anywhere, it would have to appear there.
if [ ! -f "${lab_dir}/metadata.yml" ]; then
  check "metadata.yml exists, so the command surface can be checked" "no"
elif grep -niE 'twine|upload|testpypi|--repository' "${lab_dir}/metadata.yml" >/dev/null 2>&1; then
  check "metadata.yml declares no publishing command anywhere in this lab" "no"
  grep -niE 'twine|upload|testpypi|--repository' "${lab_dir}/metadata.yml"
else
  check "metadata.yml declares no publishing command anywhere in this lab" "yes"
fi

# Every pip install this lab performs must be index-free.
install_lines="$(grep -hn 'pip. install' ${lab_scripts} | grep -v 'no-index' | grep -v '^ *#' || true)"
if [ -z "${install_lines}" ]; then
  check "every pip install in this lab passes --no-index, so no index is ever contacted" "yes"
else
  check "every pip install in this lab passes --no-index" "no"
  printf '%s\n' "${install_lines}"
fi

# The reference project declares no runtime dependencies, so installing it
# needs nothing from anywhere. That is what made --no-index possible.
if grep -q '^dependencies = \[\]' "${lab_dir}/examples/wordtally-tools/pyproject.toml"; then
  check "the reference project declares an empty runtime dependency list" "yes"
else
  check "the reference project declares an empty runtime dependency list" "no"
fi

# Nothing in the packaged source opens a socket or reads the clock, so every
# number above is reproducible.
if grep -rqE 'import (socket|urllib|requests|http)|datetime\.now|time\.time|random\.' \
     "${lab_dir}/examples/wordtally-tools/src" "${lab_dir}/starter/wordtally-tools/src" 2>/dev/null; then
  check "no network, clock or randomness in the packaged source" "no"
else
  check "no network, clock or randomness in the packaged source" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
