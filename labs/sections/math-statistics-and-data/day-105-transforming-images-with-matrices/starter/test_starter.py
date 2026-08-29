"""Your running score. Run from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Anything you have not written yet is SKIPPED, not failed. A skip means "not
attempted"; a failure means "attempted and wrong", and the failure prints both
your answer and the real one.

Float comparisons use the tolerance TOL stated in warp.py. Pixel comparisons
are EXACT, because nearest-neighbour produces whole pixel values and there is
nothing to round.
"""

import math

import numpy as np
import pytest
from PIL import Image

import answers
import pattern
import warp

TOL = warp.TOL
FILL = pattern.FILL


def written(fn, *args, **kwargs):
    """Run part of your work, or skip the test if it is not written yet."""
    try:
        return fn(*args, **kwargs)
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")


def predicted(name):
    """Read one prediction from answers.py, or skip if it is still None."""
    value = getattr(answers, name)
    if value is None:
        pytest.skip(f"answers.{name} is still unanswered")
    return value


def centred(matrix, width=9, height=9):
    """`about_centre`, routed through `written` so an unwritten helper skips.

    `about_centre` is written for you, but it calls YOUR `compose`, `matmul`
    and `translation`. Calling it directly at an argument position would let a
    NotImplementedError escape and be reported as a failure rather than as
    "not attempted", so every test goes through here instead.
    """
    return written(warp.about_centre, matrix, width, height)


def close(a, b, tol=TOL):
    """Elementwise closeness for points and for 3 by 3 matrices."""
    if isinstance(a[0], (list, tuple)):
        return all(close(ra, rb, tol) for ra, rb in zip(a, b))
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def pillow_affine(array, coefficients, out_shape=None, resample=None):
    height, width = array.shape
    out_h, out_w = out_shape or (height, width)
    return np.asarray(
        Image.fromarray(array, mode="L").transform(
            (out_w, out_h),
            Image.Transform.AFFINE,
            coefficients,
            resample=resample or Image.Resampling.NEAREST,
            fillcolor=FILL,
        )
    )


@pytest.fixture
def img():
    return pattern.make_pattern()


# -- Exercise 0: the environment ---------------------------------------------


def test_0_the_environment_is_ready():
    """Always passes once the install worked. Everything below is your work."""
    import PIL

    assert np.__version__, "numpy is importable"
    assert PIL.__version__, "Pillow is importable"
    assert warp.identity() == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    assert warp.SAMPLE_OFFSET == 0.5
    assert pattern.make_pattern().shape == (9, 9)
    assert pattern.as_text(pattern.make_pattern()) == pattern.EXPECTED_TEXT


# -- Exercise 1.1: translation ------------------------------------------------


def test_1_1_translation_has_the_right_shape():
    M = written(warp.translation, 3.0, -2.0)
    assert len(M) == 3 and all(len(row) == 3 for row in M), "3 by 3, rows of 3"
    assert M[2] == [0.0, 0.0, 1.0], "the bottom row of an affine matrix"


def test_1_1_translation_is_derived_correctly():
    M = written(warp.translation, 3.0, -2.0)
    assert close(M, [[1.0, 0.0, 3.0], [0.0, 1.0, -2.0], [0.0, 0.0, 1.0]])


# -- Exercise 1.2: scaling ----------------------------------------------------


def test_1_2_scaling_is_derived_correctly():
    M = written(warp.scaling, 2.0, 3.0)
    assert close(M, [[2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 1.0]])


# -- Exercise 1.3: rotation ---------------------------------------------------


def test_1_3_rotation_is_derived_correctly():
    M = written(warp.rotation, math.pi / 2)
    assert close(M, [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])


def test_1_3_rotation_by_zero_is_the_identity():
    M = written(warp.rotation, 0.0)
    assert close(M, warp.identity())


# -- Exercise 1.4: shear ------------------------------------------------------


def test_1_4_shear_is_derived_correctly():
    M = written(warp.shear_x, 2.0)
    assert close(M, [[1.0, 2.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])


# -- Exercise 1.5: flip -------------------------------------------------------


def test_1_5_flip_mirrors_about_the_centre_line_not_about_zero():
    M = written(warp.flip_horizontal, 9.0)
    assert close(M, [[-1.0, 0.0, 9.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])


# -- Exercise 1.6: matrix product --------------------------------------------


def test_1_6_matmul_matches_numpy():
    a = [[1.0, 2.0, 3.0], [0.0, 1.0, -1.0], [0.0, 0.0, 1.0]]
    b = [[2.0, 0.0, 1.0], [1.0, 3.0, 0.0], [0.0, 0.0, 1.0]]
    mine = written(warp.matmul, a, b)
    theirs = (np.array(a) @ np.array(b)).tolist()
    assert close(mine, theirs)


def test_1_6_compose_applies_right_to_left():
    first = written(warp.translation, 1.0, 0.0)
    second = written(warp.scaling, 2.0, 2.0)
    combined = written(warp.compose, second, first)
    # Do the translation FIRST, then the scale: (3, 5) -> (4, 5) -> (8, 10)
    assert close(combined, [[2.0, 0.0, 2.0], [0.0, 2.0, 0.0], [0.0, 0.0, 1.0]])


# -- Exercise 1.7: applying to a point ---------------------------------------


def test_1_7_apply_point_matches_the_worked_example():
    M = written(warp.translation, 3.0, -2.0)
    assert close(written(warp.apply_point, M, (8.0, 8.0)), (11.0, 6.0))


def test_1_7_a_linear_part_fixes_the_origin_and_a_translation_does_not():
    assert close(
        written(warp.apply_point, written(warp.scaling, 4.0, 0.2), (0.0, 0.0)),
        (0.0, 0.0),
    )
    assert close(
        written(warp.apply_point, written(warp.translation, 3.0, 0.0), (0.0, 0.0)),
        (3.0, 0.0),
    )


# -- Exercise 1.8: determinant ------------------------------------------------


def test_1_8_determinants_are_exact_for_whole_numbers():
    assert written(warp.determinant, written(warp.shear_x, 9.0)) == 1.0
    assert written(warp.determinant, written(warp.flip_horizontal, 9.0)) == -1.0
    assert written(warp.determinant, written(warp.scaling, 2.0, 3.0)) == 6.0
    assert written(warp.determinant, written(warp.translation, 7.0, -3.0)) == 1.0


# -- Exercise 1.9: inverse ----------------------------------------------------


def test_1_9_inverse_undoes_a_translation_and_a_shear():
    assert close(
        written(warp.invert, written(warp.translation, 3.0, -2.0)),
        written(warp.translation, -3.0, 2.0),
    )
    assert close(
        written(warp.invert, written(warp.shear_x, 2.0)),
        written(warp.shear_x, -2.0),
    )


def test_1_9_inverse_round_trips_to_the_identity():
    M = written(
        warp.compose,
        written(warp.shear_x, 0.5),
        centred(written(warp.rotation, math.radians(37))),
    )
    assert close(written(warp.compose, written(warp.invert, M), M), warp.identity())


def test_1_9_inverse_refuses_a_collapsing_transformation():
    collapse = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    try:
        warp.invert(collapse)
    except NotImplementedError as exc:
        pytest.skip(f"not written yet: {exc}")
    except warp.SingularTransform:
        return
    pytest.fail("invert should raise SingularTransform on a determinant of 0")


# -- Exercise 1.10: forward mapping, and its holes ---------------------------


def test_1_10_forward_mapping_leaves_22_holes_on_a_30_degree_rotation(img):
    matrix = centred(written(warp.rotation, math.radians(30)))
    out, holes = written(warp.warp_forward, img, matrix, fill=FILL)
    assert out.shape == (9, 9)
    assert holes.shape == (9, 9)
    assert holes.dtype == bool
    assert int(holes.sum()) == 22


def test_1_10_the_holes_are_not_all_at_the_edges(img):
    """The point of the exercise: holes appear INSIDE the glyph."""
    matrix = centred(written(warp.rotation, math.radians(30)))
    _, holes = written(warp.warp_forward, img, matrix, fill=FILL)
    interior = holes[2:7, 2:7]
    assert int(interior.sum()) > 0


def test_1_10_enlarging_forward_cannot_fill_the_output(img):
    _, holes = written(
        warp.warp_forward, img, written(warp.scaling, 2.0, 2.0),
        out_shape=(18, 18), fill=FILL,
    )
    assert int(holes.sum()) == 243


# -- Exercise 1.11: inverse mapping ------------------------------------------


def test_1_11_a_quarter_turn_is_exactly_numpy_rot90(img):
    matrix = centred(warp.rotation_quarter_turns(1))
    inverse = written(warp.invert, matrix)
    out = written(warp.warp_nearest_with_inverse, img, inverse, fill=FILL)
    assert np.array_equal(out, np.rot90(img, -1))


def test_1_11_no_pixel_is_left_unassigned(img):
    """Inverse mapping has no holes. Not fewer holes -- none."""
    matrix = centred(warp.rotation_quarter_turns(1))
    out = written(warp.warp_nearest, img, matrix, fill=FILL)
    assert int((out == FILL).sum()) == 0


def test_1_11_flips_match_numpy_exactly(img):
    assert np.array_equal(
        written(warp.warp_nearest, img, written(warp.flip_horizontal, 9.0), fill=FILL),
        np.fliplr(img),
    )
    assert np.array_equal(
        written(warp.warp_nearest, img, warp.flip_vertical(9), fill=FILL),
        np.flipud(img),
    )


def test_1_11_doubling_is_exact_pixel_replication(img):
    out = written(
        warp.warp_nearest, img, written(warp.scaling, 2.0, 2.0),
        out_shape=(18, 18), fill=FILL,
    )
    assert np.array_equal(out, np.kron(img, np.ones((2, 2), dtype=np.uint8)))


def test_1_11_halving_is_exactly_a_strided_slice(img):
    """If this fails by half a pixel, you left SAMPLE_OFFSET out."""
    out = written(
        warp.warp_nearest, img, written(warp.scaling, 0.5, 0.5),
        out_shape=(4, 4), fill=FILL,
    )
    assert np.array_equal(out, img[1::2, 1::2])


def test_1_11_translation_matches_a_slice_and_pad(img):
    out = written(warp.warp_nearest, img, written(warp.translation, 2.0, 1.0),
                  fill=FILL)
    reference = np.full_like(img, FILL)
    reference[1:, 2:] = img[:-1, :-2]
    assert np.array_equal(out, reference)


def test_1_11_a_full_turn_as_one_matrix_is_pixel_exact(img):
    matrix = centred(written(warp.rotation, 2.0 * math.pi))
    out = written(warp.warp_nearest, img, matrix, fill=FILL)
    assert np.array_equal(out, img)


def test_1_11_out_of_range_sources_take_the_fill_value_and_nothing_else(img):
    matrix = centred(written(warp.rotation, math.radians(30)))
    out = written(warp.warp_nearest, img, matrix, fill=FILL)
    back = written(warp.invert, matrix)
    for oy, ox in np.argwhere(out == FILL):
        sx, sy = warp.apply_point(back, (ox + 0.5, oy + 0.5))
        assert not (0 <= math.floor(sx) < 9 and 0 <= math.floor(sy) < 9)


# -- Exercise 1.12: Pillow's coefficients, and the comparison ----------------


def test_1_12_coefficients_are_read_off_the_inverse():
    coeffs = written(warp.to_pillow_coefficients, written(warp.translation, 1.0, 0.0))
    assert tuple(round(v, 12) for v in coeffs) == (1.0, 0.0, -1.0, 0.0, 1.0, 0.0)


def test_1_12_yours_and_pillow_agree_pixel_for_pixel(img):
    """The day's strongest claim, checked on your own code."""
    cases = [
        (1, 0, 0, 0, 1, 0),
        (1, 0, 1, 0, 1, 0),
        (1, 0, 0.5, 0, 1, 0),
        (1, 2, 0, 0, 1, 0),
        (2, 0, 0, 0, 2, 0),
        (0.5, 0, 0, 0, 0.5, 0),
        (0, -1, 9, 1, 0, 0),
        (-1, 0, 9, 0, -1, 9),
        (1, 0, -3, 0, 1, -3),
        (0.9231, 0.3129, -1.2044, -0.3129, 0.9231, 2.1177),
    ]
    for coefficients in cases:
        mine = written(
            warp.warp_nearest_with_inverse,
            img,
            warp.coefficients_to_matrix(coefficients),
            fill=FILL,
        )
        theirs = pillow_affine(img, coefficients)
        assert int((mine != theirs).sum()) == 0, f"coefficients {coefficients}"


def test_1_12_a_rotation_built_by_you_matches_pillow(img):
    matrix = centred(written(warp.rotation, math.radians(17)))
    coefficients = written(warp.to_pillow_coefficients, matrix)
    mine = written(warp.warp_nearest, img, matrix, fill=FILL)
    theirs = pillow_affine(img, coefficients)
    assert np.array_equal(mine, theirs)


# -- Exercise 2: an image is a matrix ----------------------------------------


def test_2_1_shape(img):
    assert tuple(predicted("SHAPE")) == img.shape == (9, 9)


def test_2_2_colour_shape():
    assert tuple(predicted("COLOUR_SHAPE")) == pattern.make_colour_pattern().shape


def test_2_3_the_mark_as_a_point(img):
    guess = tuple(predicted("MARK_AS_POINT"))
    assert guess == (8, 8)
    # x is the column and y is the row, so reading it back needs img[y, x].
    assert int(img[guess[1], guess[0]]) == pattern.MARK


def test_2_4_swapping_row_and_column_reads_a_different_pixel(img):
    assert predicted("VALUE_AT_SWAPPED_INDEX") == int(img[3, 4]) == pattern.PAPER
    assert int(img[4, 3]) == pattern.INK


def test_2_5_ink_pixel_count(img):
    assert predicted("INK_PIXEL_COUNT") == int((img == pattern.INK).sum()) == 24


# -- Exercise 3: forward mapping ---------------------------------------------


def test_3_1_minimum_holes_when_doubling(img):
    assert predicted("MINIMUM_HOLES_WHEN_DOUBLING") == 18 * 18 - img.size == 243


def test_3_2_holes_when_shrinking(img):
    _, holes = written(
        warp.warp_forward, img, written(warp.scaling, 0.5, 0.5),
        out_shape=(5, 5), fill=FILL,
    )
    assert predicted("HOLES_WHEN_SHRINKING") == int(holes.sum()) == 0


def test_3_3_what_shrinking_does():
    assert predicted("WHAT_SHRINKING_DOES") == "overwriting"


def test_3_4_and_3_5_fill_pixels_are_clipping_not_holes(img):
    assert predicted("FILL_PIXELS_ARE_HOLES") is False
    assert predicted("NAME_FOR_FILL_PIXELS") == "clipping"


# -- Exercise 4: inverse mapping ---------------------------------------------


def test_4_1_where_the_mark_goes(img):
    matrix = centred(warp.rotation_quarter_turns(1))
    out = written(warp.warp_nearest, img, matrix, fill=FILL)
    where = tuple(int(v) for v in np.argwhere(out == pattern.MARK)[0])
    assert tuple(predicted("MARK_AFTER_QUARTER_TURN")) == where == (8, 0)


def test_4_2_which_numpy_rotation_it_equals(img):
    k = predicted("NUMPY_ROT90_K")
    matrix = centred(warp.rotation_quarter_turns(1))
    out = written(warp.warp_nearest, img, matrix, fill=FILL)
    assert k == -1
    assert np.array_equal(out, np.rot90(img, k))


def test_4_3_no_fill_pixels_after_a_square_quarter_turn(img):
    matrix = centred(warp.rotation_quarter_turns(1))
    out = written(warp.warp_nearest, img, matrix, fill=FILL)
    assert predicted("FILL_COUNT_AFTER_QUARTER_TURN") == int((out == FILL).sum()) == 0


def test_4_4_enlarging_invents_no_new_values(img):
    out = written(
        warp.warp_nearest, img, written(warp.scaling, 2.0, 2.0),
        out_shape=(18, 18), fill=FILL,
    )
    assert predicted("DISTINCT_VALUES_AFTER_DOUBLING") == len(np.unique(out)) == 3


def test_4_5_which_slice_the_downscale_is(img):
    out = written(
        warp.warp_nearest, img, written(warp.scaling, 0.5, 0.5),
        out_shape=(4, 4), fill=FILL,
    )
    assert predicted("DOWNSCALE_IS_THE_SLICE") == "img[1::2, 1::2]"
    assert np.array_equal(out, img[1::2, 1::2])


# -- Exercise 5: homogeneous coordinates -------------------------------------


def test_5_1_why_2x2_cannot_translate():
    assert predicted("WHY_2X2_CANNOT_TRANSLATE") == "it cannot move the origin"
    for matrix in (warp.rotation_quarter_turns(1), warp.shear_y(3.0)):
        assert warp.apply_point(matrix, (0.0, 0.0)) == (0.0, 0.0)


def test_5_2_determinant_of_a_translation():
    M = written(warp.translation, 7.0, -3.0)
    assert predicted("DETERMINANT_OF_A_TRANSLATION") == written(warp.determinant, M)


def test_5_3_compose_order():
    assert predicted("COMPOSE_APPLIES_FIRST") == "A"


def test_5_4_twelve_separate_rotations_lose_pixels(img):
    assert predicted("TWELVE_SEPARATE_ROTATIONS_ARE_EXACT") is False
    step = centred(written(warp.rotation, math.radians(30)))
    out = img
    for _ in range(12):
        out = written(warp.warp_nearest, out, step, fill=FILL)
    assert int((out != img).sum()) == 16


def test_5_5_the_same_twelve_composed_are_exact(img):
    assert predicted("TWELVE_COMPOSED_ROTATIONS_ARE_EXACT") is True
    step = centred(written(warp.rotation, math.radians(30)))
    combined = warp.identity()
    for _ in range(12):
        combined = written(warp.compose, step, combined)
    assert np.array_equal(written(warp.warp_nearest, img, combined, fill=FILL), img)


# -- Exercise 6: Pillow and the half pixel -----------------------------------


def test_6_1_and_6_2_the_coefficient_direction():
    assert predicted("PILLOW_COEFFICIENT_DIRECTION") == "output to input"
    assert predicted("PICTURE_MOVES_WHEN_C_IS_POSITIVE") == "left"
    probe = np.zeros((1, 8), dtype=np.uint8)
    probe[0, 3] = 255
    assert int(np.argmax(pillow_affine(probe, (1, 0, 1, 0, 1, 0))[0])) == 2


def test_6_3_pillow_samples_at_pixel_centres():
    assert predicted("PILLOW_SAMPLES_AT") == "its centre"
    row = (np.arange(8, dtype=np.uint8) * 10).reshape(1, 8)
    observed = [int(v) for v in pillow_affine(row, (2, 0, 0, 0, 1, 0))[0]]
    centres = [
        int(row[0, math.floor(2 * (x + 0.5))])
        if math.floor(2 * (x + 0.5)) < 8 else FILL
        for x in range(8)
    ]
    assert observed == centres


def test_6_4_row_zero_moves_under_a_shear_of_two():
    """The question Day 102 deferred, answered as a number."""
    assert predicted("ROW_ZERO_SHIFT_WITH_B_EQUALS_2") == 1
    strip = np.zeros((3, 9), dtype=np.uint8)
    strip[:, 4] = 255
    out = pillow_affine(strip, (1, 2, 0, 0, 1, 0))
    assert int(np.flatnonzero(out[0] == 255)[0]) == 3  # was 4, moved by 1


def test_6_5_a_full_turn_changes_nothing(img):
    assert predicted("PIXELS_CHANGED_BY_A_FULL_TURN") == 0
    assert math.sin(2.0 * math.pi) != 0.0
    matrix = centred(written(warp.rotation, 2.0 * math.pi))
    assert int((written(warp.warp_nearest, img, matrix, fill=FILL) != img).sum()) == 0


def test_6_6_why_those_angles_disagree():
    assert (
        predicted("WHY_THOSE_ANGLES_DISAGREE")
        == "their sines and cosines land samples exactly on pixel boundaries"
    )
