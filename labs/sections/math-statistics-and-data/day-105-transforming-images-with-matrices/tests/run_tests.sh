#!/usr/bin/env bash
# Tests for the Day 105 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# The harness proves the lesson's claims by running code and reading real
# values, never by reading source:
#
#   * an image is a matrix, its shape is (height, width), and img[4, 3] is a
#     different pixel from img[3, 4] -- the ordering trap, measured;
#   * forward mapping leaves 22 of 81 output pixels unwritten on a 30 degree
#     rotation and 243 of 324 when doubling, and inverse mapping leaves none;
#   * a quarter turn is EXACTLY numpy.rot90(img, -1), a flip is exactly
#     numpy.fliplr, doubling is exactly numpy.kron, and halving is exactly the
#     strided slice img[1::2, 1::2];
#   * translation is not linear, needs a third coordinate, and then composes
#     with everything else -- checked as a matrix and as pixels;
#   * Pillow's affine coefficients run OUTPUT to INPUT, and Pillow samples at
#     each output pixel's CENTRE -- both settled by measurement, which is the
#     question Day 102 deferred to today;
#   * a shear coefficient of 2.0 moves row 0 by one whole pixel, and the half-
#     pixel offset explains exactly why;
#   * this implementation and Pillow produce byte-for-byte identical output on
#     510 affine transformations, and differ on 8 of the 360 whole-degree
#     rotations by at most 2 pixels -- every disagreement a floating-point tie
#     at a pixel boundary, which is asserted rather than hidden;
#   * a 360 degree rotation as ONE matrix is pixel-exact; as twelve separate
#     resampling passes it loses 16 of 81 pixels;
#   * nothing is downloaded, no image is written into the lab, and nothing is
#     left behind on disk.
#
# Everything runs offline. Nothing binds a port, nothing writes outside the
# lab or a temporary directory, nothing needs a key. Deterministic,
# non-interactive, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Bytecode left by an EARLIER command is not this run's litter. The README
# documents `pytest starter -q`, and running it writes .pyc files that would
# then fail the cleanliness check at the end of this script -- failing the
# reader for following the instructions. Clearing them here makes that final
# check measure what it claims to: what THIS run left behind. `.venv` is
# untouched, because the packages' own bytecode is theirs, not ours.
find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

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

check_eq() {
  # check_eq <label> <expected> <actual>
  if [ "$2" = "$3" ]; then
    check "$1" "yes"
  else
    check "$1 (expected [$2], got [$3])" "no"
  fi
}

# Resolve pytest: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping checks.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install the lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest:" >&2
  echo "    PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

# The Python that owns that pytest is the one with numpy and Pillow installed.
python_bin="$(dirname "${pytest_bin}")/python3"
if [ ! -x "${python_bin}" ]; then
  python_bin="$(command -v python3 || true)"
fi
if [ -z "${python_bin}" ]; then
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
fi

for module in numpy PIL; do
  if ! "${python_bin}" -c "import ${module}" >/dev/null 2>&1; then
    echo "FAIL: ${module} is not importable from ${python_bin}." >&2
    echo "  Install the lab's dependencies with:" >&2
    echo "    python3 -m venv .venv" >&2
    echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
    exit 1
  fi
done

echo "Day 105 — Rotate It Yourself"
echo

# --------------------------------------------------------------------------
echo "1. The tools and the versions this lab was written against"
# --------------------------------------------------------------------------

versions="$("${python_bin}" - <<'PY'
import platform
import sys
from importlib.metadata import version

print(f"python   {platform.python_version()}")
for name in ("numpy", "pillow", "pytest"):
    print(f"{name:<8} {version(name)}")
print(f"platform {platform.platform()}")
print(f"exe      {sys.executable.rsplit('/', 3)[-1]}")
PY
)"
echo "${versions}" | sed 's/^/  /'

for package in numpy pillow pytest; do
  pinned="$(grep -iE "^${package}==" "${lab_dir}/requirements/requirements.txt" | cut -d= -f3)"
  installed="$("${python_bin}" -c "from importlib.metadata import version; print(version('${package}'))")"
  check_eq "installed ${package} matches requirements.txt" "${pinned}" "${installed}"
done

major="$("${python_bin}" -c "import numpy; print(numpy.__version__.split('.')[0])")"
check_eq "numpy is version 2 or later" "2" "${major}"

pil_major="$("${python_bin}" -c "import PIL; print(PIL.__version__.split('.')[0])")"
check_eq "Pillow is version 12 or later" "12" "${pil_major}"

# --------------------------------------------------------------------------
echo
echo "2. Every reference script runs and every assertion inside it holds"
# --------------------------------------------------------------------------

for script in 01_an_image_is_a_matrix 02_forward_mapping_leaves_holes \
              03_inverse_mapping 04_scale_shear_flip \
              05_homogeneous_and_composition 06_against_pillow; do
  out="$(cd "${lab_dir}/examples" && "${python_bin}" "${script}.py" 2>&1)"
  status=$?
  if [ "${status}" -ne 0 ]; then
    check "${script}.py exits 0" "no"
    echo "${out}" | tail -5 | sed 's/^/      /'
  else
    check "${script}.py exits 0" "yes"
  fi
  case "${out}" in
    *"${script}.py: every assertion held."*)
      check "${script}.py reports every assertion held" "yes" ;;
    *) check "${script}.py reports every assertion held" "no" ;;
  esac
done

# --------------------------------------------------------------------------
echo
echo "3. The reference pytest suite: real pixels, real values"
# --------------------------------------------------------------------------

ref_out="$(cd "${lab_dir}" && "${pytest_bin}" examples -q -p no:cacheprovider 2>&1)"
ref_status=$?
echo "${ref_out}" | tail -3 | sed 's/^/  /'
if [ "${ref_status}" -eq 0 ]; then
  check "pytest examples exits 0" "yes"
else
  check "pytest examples exits 0" "no"
fi
case "${ref_out}" in
  *" failed"*) check "no test in the reference suite failed" "no" ;;
  *)           check "no test in the reference suite failed" "yes" ;;
esac
ref_passed="$(printf '%s\n' "${ref_out}" | grep -o '[0-9][0-9]* passed' | head -1 | cut -d' ' -f1)"
if [ "${ref_passed:-0}" -ge 60 ]; then
  check "the reference suite ran at least 60 tests (ran ${ref_passed})" "yes"
else
  check "the reference suite ran at least 60 tests (ran ${ref_passed:-0})" "no"
fi

# --------------------------------------------------------------------------
echo
echo "4. The starter suite skips unattempted work instead of failing it"
# --------------------------------------------------------------------------

start_out="$(cd "${lab_dir}" && "${pytest_bin}" starter -q -p no:cacheprovider 2>&1)"
start_status=$?
echo "${start_out}" | tail -3 | sed 's/^/  /'
if [ "${start_status}" -eq 0 ]; then
  check "pytest starter exits 0 on an untouched checkout" "yes"
else
  check "pytest starter exits 0 on an untouched checkout" "no"
fi
case "${start_out}" in
  *" failed"*) check "the starter suite reports no failures" "no" ;;
  *)           check "the starter suite reports no failures" "yes" ;;
esac
case "${start_out}" in
  *skipped*) check "unwritten exercises are reported as skipped, not passed" "yes" ;;
  *) check "unwritten exercises are reported as skipped, not passed" "no" ;;
esac

# The import guard. Both directories contain modules called `warp` and
# `pattern`, and pytest imports test files by putting their directory on
# sys.path -- so collecting both suites at once would otherwise let the starter
# tests import the REFERENCE solution and report unwritten exercises as
# passing. Each directory's conftest.py prevents that. This check proves it
# still does: across both suites, the skip count must be unchanged.
both_out="$(cd "${lab_dir}" && "${pytest_bin}" -q -p no:cacheprovider 2>&1)"
start_skipped="$(printf '%s\n' "${start_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
both_skipped="$(printf '%s\n' "${both_out}" | grep -o '[0-9][0-9]* skipped' | head -1 | cut -d' ' -f1)"
check_eq "collecting both suites at once does not turn skips into passes" \
  "${start_skipped:-none}" "${both_skipped:-none}"

# --------------------------------------------------------------------------
echo
echo "5. The lesson's claims, checked one value at a time"
# --------------------------------------------------------------------------

facts="$(cd "${lab_dir}/examples" && "${python_bin}" - <<'PY'
import math
import os
import random
import tempfile

import numpy as np
from PIL import Image

import pattern
import warp

FILL = pattern.FILL
img = pattern.make_pattern()
H, W = img.shape


def pil(array, coefficients, out_shape=None, resample=None):
    h, w = array.shape
    oh, ow = out_shape or (h, w)
    return np.asarray(
        Image.fromarray(array, mode="L").transform(
            (ow, oh), Image.Transform.AFFINE, coefficients,
            resample=resample or Image.Resampling.NEAREST, fillcolor=FILL,
        )
    )


# -- the image itself
print("shape", img.shape)
print("colour_shape", pattern.make_colour_pattern().shape)
print("dtype", img.dtype)
print("ink_count", int((img == pattern.INK).sum()))
print("row_col_swap_differs", int(img[4, 3]), int(img[3, 4]))
print("asymmetric", (not np.array_equal(img, np.fliplr(img)),
                     not np.array_equal(img, np.flipud(img)),
                     not np.array_equal(img, img.T)))
print("generated_twice_identical",
      np.array_equal(pattern.make_pattern(), pattern.make_pattern()))

# -- forward mapping
rot30 = warp.about_centre(warp.rotation(math.radians(30)), W, H)
_, holes = warp.warp_forward(img, rot30, fill=FILL)
print("forward_holes_rot30", int(holes.sum()))
print("forward_holes_inside_glyph", int(holes[2:7, 2:7].sum()) > 0)
_, big_holes = warp.warp_forward(img, warp.scaling(2.0, 2.0),
                                 out_shape=(18, 18), fill=FILL)
print("forward_holes_double", int(big_holes.sum()), 18 * 18 - img.size)

inv30 = warp.warp_nearest(img, rot30, fill=FILL)
back = warp.invert(rot30)
filled = np.argwhere(inv30 == FILL)
outside = sum(
    1 for oy, ox in filled
    if not (0 <= math.floor(warp.apply_point(back, (ox + .5, oy + .5))[0]) < W
            and 0 <= math.floor(warp.apply_point(back, (ox + .5, oy + .5))[1]) < H)
)
print("inverse_fill_count", len(filled))
print("inverse_fill_all_outside", len(filled) == outside and len(filled) > 0)

# -- exact answers
q = warp.about_centre(warp.rotation_quarter_turns(1), W, H)
turned = warp.warp_nearest(img, q, fill=FILL)
print("quarter_turn_is_rot90", np.array_equal(turned, np.rot90(img, -1)))
print("quarter_turn_no_fill", int((turned == FILL).sum()))
print("mark_before", tuple(int(v) for v in np.argwhere(img == pattern.MARK)[0]))
print("mark_after", tuple(int(v) for v in np.argwhere(turned == pattern.MARK)[0]))
print("flip_h_is_fliplr", np.array_equal(
    warp.warp_nearest(img, warp.flip_horizontal(W), fill=FILL), np.fliplr(img)))
print("flip_v_is_flipud", np.array_equal(
    warp.warp_nearest(img, warp.flip_vertical(H), fill=FILL), np.flipud(img)))
print("double_is_kron", np.array_equal(
    warp.warp_nearest(img, warp.scaling(2.0, 2.0), out_shape=(18, 18), fill=FILL),
    np.kron(img, np.ones((2, 2), dtype=np.uint8))))
print("halve_is_strided_slice", np.array_equal(
    warp.warp_nearest(img, warp.scaling(0.5, 0.5), out_shape=(4, 4), fill=FILL),
    img[1::2, 1::2]))

# -- translation and homogeneous coordinates
print("translation_moves_origin",
      warp.apply_point(warp.translation(3.0, -2.0), (0.0, 0.0)))
print("linear_fixes_origin", all(
    warp.apply_point(m, (0.0, 0.0)) == (0.0, 0.0)
    for m in (warp.rotation(1.1), warp.scaling(4.0, .2), warp.shear_x(9.0))))
print("translation_det", warp.determinant(warp.translation(7.0, -3.0)))
print("bottom_row_always", all(
    m[2] == [0.0, 0.0, 1.0] for m in (
        warp.translation(3, -2), warp.scaling(2, .5), warp.rotation(1.1),
        warp.shear_x(2), warp.flip_horizontal(9), q)))
det_parts = [warp.scaling(1.5, 1.5), warp.shear_x(0.5), warp.rotation(0.7)]
prod = 1.0
for m in det_parts:
    prod *= warp.determinant(m)
print("det_of_composition_is_product",
      abs(warp.determinant(warp.compose(*det_parts)) - prod) <= warp.TOL)

# -- resampling once versus repeatedly
full = warp.about_centre(warp.rotation(2.0 * math.pi), W, H)
print("full_turn_one_matrix_diff",
      int((warp.warp_nearest(img, full, fill=FILL) != img).sum()))
cur = img
for _ in range(12):
    cur = warp.warp_nearest(cur, rot30, fill=FILL)
print("full_turn_twelve_passes_diff", int((cur != img).sum()))
comb = warp.identity()
for _ in range(12):
    comb = warp.compose(rot30, comb)
print("full_turn_twelve_composed_diff",
      int((warp.warp_nearest(img, comb, fill=FILL) != img).sum()))

# -- the Pillow conventions, measured
probe = np.zeros((1, 8), dtype=np.uint8)
probe[0, 3] = 255
print("pillow_positive_c_moves_left",
      int(np.argmax(probe[0])), int(np.argmax(pil(probe, (1, 0, 1, 0, 1, 0))[0])))
print("to_pillow_coefficients_inverts",
      tuple(round(v, 12) for v in warp.to_pillow_coefficients(warp.translation(1.0, 0.0))))

row = (np.arange(8, dtype=np.uint8) * 10).reshape(1, 8)
obs = [int(v) for v in pil(row, (2, 0, 0, 0, 1, 0))[0]]
centres = [int(row[0, math.floor(2 * (x + .5))])
           if math.floor(2 * (x + .5)) < 8 else FILL for x in range(8)]
corners = [int(row[0, math.floor(2 * x + .5)])
           if math.floor(2 * x + .5) < 8 else FILL for x in range(8)]
print("pillow_matches_centres", obs == centres)
print("pillow_matches_corners", obs == corners)
print("sample_offset", warp.SAMPLE_OFFSET)

strip = np.zeros((3, 9), dtype=np.uint8)
strip[:, 4] = 255
sh = pil(strip, (1, 2, 0, 0, 1, 0))
print("shear_row0_line_at", int(np.flatnonzero(sh[0] == 255)[0]))
print("shear_row1_line_at", int(np.flatnonzero(sh[1] == 255)[0]))
print("shear_row0_shift_predicted", math.floor(0.5 + 2 * 0.5))

# -- ours against theirs
rng = random.Random(105)
cases = []
for _ in range(500):
    th = rng.uniform(-math.pi, math.pi)
    sc = rng.uniform(0.4, 2.5)
    sk = rng.uniform(-2.5, 2.5)
    ca, sa = math.cos(th), math.sin(th)
    cases.append((sc * ca, sc * (ca * sk - sa), rng.uniform(-6, 6),
                  sc * sa, sc * (sa * sk + ca), rng.uniform(-6, 6)))
cases += [(1, 0, 0, 0, 1, 0), (1, 0, 1, 0, 1, 0), (1, 0, .5, 0, 1, 0),
          (1, 2, 0, 0, 1, 0), (2, 0, 0, 0, 2, 0), (.5, 0, 0, 0, .5, 0),
          (0, -1, 9, 1, 0, 0), (-1, 0, 9, 0, -1, 9), (1, 0, -3, 0, 1, -3),
          (1, .5, 0, 0, 1, 0)]
worst = 0
for co in cases:
    mine = warp.warp_nearest_with_inverse(
        img, warp.coefficients_to_matrix(co), fill=FILL)
    worst = max(worst, int((mine != pil(img, co)).sum()))
print("random_cases", len(cases))
print("random_worst_differing_pixels", worst)

bad_angles, worst_rot, furthest = [], 0, 0.0
for deg in range(360):
    M = warp.about_centre(warp.rotation(math.radians(deg)), W, H)
    co = warp.to_pillow_coefficients(M)
    wrong = np.argwhere(warp.warp_nearest(img, M, fill=FILL) != pil(img, co))
    if len(wrong):
        bad_angles.append(deg)
        worst_rot = max(worst_rot, len(wrong))
    a, b, c, d, e, f = co
    for oy, ox in wrong:
        xs = a * (ox + .5) + b * (oy + .5) + c
        ys = d * (ox + .5) + e * (oy + .5) + f
        furthest = max(furthest, min(abs(xs - round(xs)), abs(ys - round(ys))))
print("rotation_sweep_disagreeing", bad_angles)
print("rotation_sweep_worst_pixels", worst_rot)
print("rotation_sweep_all_at_boundaries", furthest < 1e-9)

M30 = warp.about_centre(warp.rotation(math.radians(30)), W, H)
co30 = warp.to_pillow_coefficients(M30)
w30 = np.argwhere(warp.warp_nearest(img, M30, fill=FILL) != pil(img, co30))
oy, ox = int(w30[0][0]), int(w30[0][1])
ys30 = co30[3] * (ox + .5) + co30[4] * (oy + .5) + co30[5]
print("thirty_degree_disagreements", len(w30))
print("thirty_degree_pixel", (oy, ox))
print("thirty_degree_source_y_is_just_under_5",
      abs(ys30 - 5.0) < 1e-14 and ys30 != 5.0)

# -- bilinear
worst_inside, worst_any = 0.0, 0.0
for M in (warp.translation(.25, .25),
          warp.about_centre(warp.rotation(math.radians(30)), W, H),
          warp.about_centre(warp.rotation(math.radians(17)), W, H),
          warp.about_centre(warp.scaling(1.5, 1.5), W, H),
          warp.shear_x(0.4)):
    inv = warp.invert(M)
    mine = warp.warp_bilinear_with_inverse(img, inv, fill=0.0)
    theirs = pil(img, warp.to_pillow_coefficients(M),
                 resample=Image.Resampling.BILINEAR).astype(float)
    d = np.abs(mine - theirs)
    inside = np.zeros((H, W), dtype=bool)
    for y in range(H):
        for x in range(W):
            sx, sy = warp.apply_point(inv, (x + .5, y + .5))
            x0, y0 = math.floor(sx - .5), math.floor(sy - .5)
            inside[y, x] = 0 <= x0 and x0 + 1 < W and 0 <= y0 and y0 + 1 < H
    worst_inside = max(worst_inside, float(d[inside].max()))
    worst_any = max(worst_any, float(d.max()))
print("bilinear_worst_all_inside", round(worst_inside, 6))
print("bilinear_worst_anywhere_exceeds_100", worst_any > 100.0)

# -- files
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, "pattern.png")
    Image.fromarray(img, mode="L").save(p)
    reloaded = np.asarray(Image.open(p).convert("L"))
    print("png_round_trip_lossless", np.array_equal(reloaded, img))
print("temp_file_removed", not os.path.exists(p))
PY
)"

get() { printf '%s\n' "${facts}" | grep "^$1 " | cut -d' ' -f2-; }

check_eq "the image is a (height, width) array of 9 by 9" "(9, 9)" "$(get shape)"
check_eq "the colour image is three stacked planes" "(9, 9, 3)" "$(get colour_shape)"
check_eq "one byte per pixel" "uint8" "$(get dtype)"
check_eq "the pattern has 24 ink pixels" "24" "$(get ink_count)"
check_eq "img[4, 3] and img[3, 4] are DIFFERENT pixels" \
  "255 0" "$(get row_col_swap_differs)"
check_eq "the pattern is asymmetric under mirror, flip and transpose" \
  "(True, True, True)" "$(get asymmetric)"
check_eq "the pattern is generated, not loaded: two calls agree" \
  "True" "$(get generated_twice_identical)"

check_eq "forward mapping leaves 22 holes on a 30 degree rotation" \
  "22" "$(get forward_holes_rot30)"
check_eq "and some of those holes are INSIDE the glyph, not at the edge" \
  "True" "$(get forward_holes_inside_glyph)"
check_eq "forward mapping cannot fill a doubled output: 243 holes of 324" \
  "243 243" "$(get forward_holes_double)"
check_eq "inverse mapping leaves 12 pixels at the fill value" \
  "12" "$(get inverse_fill_count)"
check_eq "and every one of them is clipping, not a hole" \
  "True" "$(get inverse_fill_all_outside)"

check_eq "a quarter turn is EXACTLY numpy.rot90(img, -1)" \
  "True" "$(get quarter_turn_is_rot90)"
check_eq "a quarter turn of a square image clips nothing" \
  "0" "$(get quarter_turn_no_fill)"
check_eq "the corner mark starts at row 8, column 8" "(8, 8)" "$(get mark_before)"
check_eq "and a clockwise quarter turn puts it at row 8, column 0" \
  "(8, 0)" "$(get mark_after)"
check_eq "a horizontal flip is EXACTLY numpy.fliplr" "True" "$(get flip_h_is_fliplr)"
check_eq "a vertical flip is EXACTLY numpy.flipud" "True" "$(get flip_v_is_flipud)"
check_eq "doubling is EXACTLY numpy.kron with a 2 by 2 block of ones" \
  "True" "$(get double_is_kron)"
check_eq "halving is EXACTLY the strided slice img[1::2, 1::2]" \
  "True" "$(get halve_is_strided_slice)"

check_eq "translation moves the origin, so it is not linear" \
  "(3.0, -2.0)" "$(get translation_moves_origin)"
check_eq "every purely linear part leaves the origin alone" \
  "True" "$(get linear_fixes_origin)"
check_eq "a translation's determinant is exactly 1" \
  "1.0" "$(get translation_det)"
check_eq "every affine matrix has the bottom row (0, 0, 1)" \
  "True" "$(get bottom_row_always)"
check_eq "the determinant of a composition is the product of the parts" \
  "True" "$(get det_of_composition_is_product)"

check_eq "a full turn as ONE matrix changes no pixel" \
  "0" "$(get full_turn_one_matrix_diff)"
check_eq "the same full turn as twelve passes loses 16 pixels" \
  "16" "$(get full_turn_twelve_passes_diff)"
check_eq "and composing those twelve into one matrix is exact again" \
  "0" "$(get full_turn_twelve_composed_diff)"

check_eq "a POSITIVE Pillow c coefficient moves the picture LEFT" \
  "3 2" "$(get pillow_positive_c_moves_left)"
check_eq "to_pillow_coefficients reads off the INVERSE, so c is negative" \
  "(1.0, 0.0, -1.0, 0.0, 1.0, 0.0)" "$(get to_pillow_coefficients_inverts)"

# Section 6 re-runs this script with D105_SELF_TEST=1, which swaps ONE
# expectation below for a deliberately wrong one. That is how the harness
# proves it can fail rather than merely asserting that it could.
expected_centres="True"
if [ -n "${D105_SELF_TEST:-}" ]; then
  expected_centres="False"   # the naive belief, deliberately wrong here
fi
check_eq "Pillow samples at each output pixel's CENTRE" \
  "${expected_centres}" "$(get pillow_matches_centres)"
check_eq "Pillow does NOT sample at integer corners" \
  "False" "$(get pillow_matches_corners)"
check_eq "this lab uses the same half-pixel offset" "0.5" "$(get sample_offset)"

check_eq "a shear coefficient of 2 moves row 0 by one whole pixel" \
  "3" "$(get shear_row0_line_at)"
check_eq "and moves row 1 by three" "1" "$(get shear_row1_line_at)"
check_eq "the half-pixel offset predicts that row 0 shift exactly" \
  "1" "$(get shear_row0_shift_predicted)"

check_eq "510 affine transformations were compared with Pillow" \
  "510" "$(get random_cases)"
check_eq "and every one of them agreed byte for byte" \
  "0" "$(get random_worst_differing_pixels)"
check_eq "8 of the 360 whole-degree rotations DO disagree, and they are named" \
  "[30, 60, 120, 150, 210, 240, 300, 330]" "$(get rotation_sweep_disagreeing)"
check_eq "no disagreement is larger than 2 pixels of 81" \
  "2" "$(get rotation_sweep_worst_pixels)"
check_eq "and every disagreeing sample sits on a pixel boundary" \
  "True" "$(get rotation_sweep_all_at_boundaries)"
check_eq "the 30 degree case differs in exactly one pixel" \
  "1" "$(get thirty_degree_disagreements)"
check_eq "that pixel is row 4, column 3" "(4, 3)" "$(get thirty_degree_pixel)"
check_eq "its source row is 4.999999999999999 rather than 5" \
  "True" "$(get thirty_degree_source_y_is_just_under_5)"

check_eq "bilinear agrees with Pillow within 1 grey level away from the border" \
  "1.0" "$(get bilinear_worst_all_inside)"
check_eq "and diverges by more than 100 levels AT the border, which is stated" \
  "True" "$(get bilinear_worst_anywhere_exceeds_100)"

check_eq "a PNG round trip is lossless" "True" "$(get png_round_trip_lossless)"
check_eq "and the temporary file is gone afterwards" "True" "$(get temp_file_removed)"

# --------------------------------------------------------------------------
echo
echo "6. The harness can actually fail"
# --------------------------------------------------------------------------

# A green test suite proves nothing until you have watched it go red. This
# section re-runs the whole script with one expectation deliberately swapped
# for the naive belief that Pillow samples at integer pixel corners, and
# asserts that the re-run reports the failure and exits non-zero. If this
# section passes, section 5 is not decorative.
if [ -z "${D105_SELF_TEST:-}" ]; then
  self_out="$(D105_SELF_TEST=1 bash "${BASH_SOURCE[0]}" 2>&1)"
  self_status=$?
  if [ "${self_status}" -ne 0 ]; then
    check "a deliberately wrong expectation makes the harness exit non-zero (${self_status})" "yes"
  else
    check "a deliberately wrong expectation makes the harness exit non-zero" "no"
  fi
  case "${self_out}" in
    *"FAIL: Pillow samples at each output pixel's CENTRE"*)
      check "the failing check is named in the output with both values" "yes" ;;
    *) check "the failing check is named in the output with both values" "no" ;;
  esac
  case "${self_out}" in
    *", 1 failure(s)."*)
      check "the summary line counts exactly one failure" "yes" ;;
    *) check "the summary line counts exactly one failure" "no" ;;
  esac
else
  echo "  (self-test run: section 6 does not recurse)"
fi

# --------------------------------------------------------------------------
echo
echo "7. Nothing was downloaded, and nothing was left behind"
# --------------------------------------------------------------------------

# Every find below PRUNES .venv first, and it is not optional. The README tells
# you to create a lab-local virtual environment, so `.venv` is the documented
# setup rather than litter -- and NumPy and Pillow both ship their own compiled
# bytecode and their own test images inside it. Without the prune, this section
# would fail the lab for following its own installation instructions.
if find "${lab_dir}" -name '.venv' -prune -o -type d -name '__pycache__' -print -quit 2>/dev/null | grep -q .; then
  check "no __pycache__ directory left under the lab (ignoring .venv)" "no"
else
  check "no __pycache__ directory left under the lab (ignoring .venv)" "yes"
fi

if find "${lab_dir}" -name '.venv' -prune -o -type d -name '.pytest_cache' -print -quit 2>/dev/null | grep -q .; then
  check "no .pytest_cache directory left under the lab (ignoring .venv)" "no"
else
  check "no .pytest_cache directory left under the lab (ignoring .venv)" "yes"
fi

# The test image is GENERATED, not downloaded and not committed. If an image
# file ever appears in the lab's own tree, either something was committed by
# mistake or a script wrote one and failed to clean up. Pillow ships a pile of
# its own test images inside site-packages, so .venv is pruned here too.
image_files="$(find "${lab_dir}" -name '.venv' -prune -o -type f \
  \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.bmp' \
     -o -name '*.gif' -o -name '*.tif' -o -name '*.tiff' \) -print 2>/dev/null \
  | wc -l | tr -d ' ')"
check_eq "no image file in the lab's own tree: the pattern is generated" \
  "0" "${image_files}"

if grep -rqE 'urlopen|requests\.|socket\.|http://|https://' \
     "${lab_dir}/examples" "${lab_dir}/starter" 2>/dev/null; then
  check "no lab source opens a network connection" "no"
else
  check "no lab source opens a network connection" "yes"
fi

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
