"""The reference test suite: real pixels, real values, real disagreements.

Run from the LAB DIRECTORY:

    .venv/bin/pytest examples -q -p no:cacheprovider

Every float comparison states a tolerance. Every pixel comparison states
whether it is exact or within a stated number of grey levels, and the exact
ones say `==` on purpose, because that is the stronger claim.
"""

import math
import os
import random
import tempfile

import numpy as np
import pytest
from PIL import Image

import pattern
import warp

TOL = pattern.TOL
FILL = pattern.FILL


def pillow_affine(array, coefficients, out_shape=None, resample=None):
    height, width = array.shape
    out_h, out_w = out_shape or (height, width)
    image = Image.fromarray(array, mode="L")
    return np.asarray(
        image.transform(
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


# -- The image itself --------------------------------------------------------


def test_pattern_has_the_documented_shape_and_type(img):
    assert img.shape == pattern.EXPECTED_SHAPE == (9, 9)
    assert img.dtype == np.uint8
    assert img.nbytes == 81


def test_pattern_pixel_values_are_exactly_as_written(img):
    assert pattern.as_text(img) == pattern.EXPECTED_TEXT
    assert int(img[0, 1]) == pattern.INK
    assert int(img[0, 0]) == pattern.PAPER
    assert int(img[8, 8]) == pattern.MARK
    assert int((img == pattern.INK).sum()) == pattern.EXPECTED_INK_COUNT == 24
    assert int((img == pattern.MARK).sum()) == 1


def test_row_and_column_are_not_interchangeable(img):
    # The ordering trap, asserted rather than described.
    assert int(img[4, 3]) == pattern.INK
    assert int(img[3, 4]) == pattern.PAPER
    assert img[4, 3] != img[3, 4]


def test_the_pattern_is_asymmetric_under_every_operation_tested(img):
    assert not np.array_equal(img, np.fliplr(img))
    assert not np.array_equal(img, np.flipud(img))
    assert not np.array_equal(img, img.T)
    assert not np.array_equal(img, np.rot90(img))


def test_colour_is_three_stacked_planes(img):
    colour = pattern.make_colour_pattern()
    assert colour.shape == (9, 9, 3)
    assert np.array_equal(colour[:, :, 0], img)
    assert np.array_equal(colour[:, :, 1], np.fliplr(img))
    assert int(colour[:, :, 2].min()) == int(colour[:, :, 2].max()) == pattern.MARK


def test_the_pattern_is_generated_not_loaded():
    # Two independent calls must agree, and neither may touch the filesystem.
    assert np.array_equal(pattern.make_pattern(), pattern.make_pattern())


# -- Matrices ---------------------------------------------------------------


def test_every_affine_matrix_has_the_bottom_row_0_0_1():
    for matrix in (
        warp.identity(),
        warp.translation(3.0, -2.0),
        warp.scaling(2.0, 0.5),
        warp.rotation(1.1),
        warp.shear_x(2.0),
        warp.shear_y(-0.5),
        warp.flip_horizontal(9),
        warp.flip_vertical(9),
        warp.about_centre(warp.rotation(0.3), 9, 9),
    ):
        assert matrix[2] == [0.0, 0.0, 1.0]


def test_translation_is_not_linear_but_every_2x2_part_is():
    # A linear map must fix the origin; translation does not.
    assert warp.apply_point(warp.translation(3.0, -2.0), (0.0, 0.0)) == (3.0, -2.0)
    for matrix in (warp.rotation(1.1), warp.scaling(4.0, 0.2), warp.shear_x(9.0)):
        assert warp.apply_point(matrix, (0.0, 0.0)) == (0.0, 0.0)


def test_translation_composes_and_inverts():
    shift = warp.translation(3.0, -2.0)
    assert warp.determinant(shift) == 1.0
    assert warp.matrices_close(warp.invert(shift), warp.translation(-3.0, 2.0), TOL)
    assert warp.matrices_close(
        warp.compose(warp.invert(shift), shift), warp.identity(), TOL
    )


def test_quarter_turn_matrix_is_exact_where_trigonometry_is_not():
    exact = warp.rotation_quarter_turns(1)
    trig = warp.rotation(math.pi / 2)
    assert exact == [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    assert math.cos(math.pi / 2) != 0.0
    assert trig != exact
    assert warp.matrices_close(trig, exact, TOL)


def test_four_quarter_turns_return_to_the_identity():
    turn = warp.rotation_quarter_turns(1)
    assert warp.matrices_close(
        warp.compose(turn, turn, turn, turn), warp.identity(), TOL
    )


def test_composition_order_is_right_to_left():
    first = warp.translation(1.0, 0.0)
    second = warp.scaling(2.0, 2.0)
    combined = warp.compose(second, first)
    stepwise = warp.apply_point(second, warp.apply_point(first, (3.0, 5.0)))
    assert combined is not first
    for a, b in zip(warp.apply_point(combined, (3.0, 5.0)), stepwise):
        assert abs(a - b) <= TOL
    # And the other order is genuinely different.
    assert not warp.matrices_close(warp.compose(first, second), combined, TOL)


def test_determinant_of_a_composition_is_the_product():
    parts = [warp.scaling(1.5, 1.5), warp.shear_x(0.5), warp.rotation(0.7)]
    combined = warp.compose(*parts)
    product = 1.0
    for matrix in parts:
        product *= warp.determinant(matrix)
    assert abs(warp.determinant(combined) - product) <= TOL


def test_determinants_of_the_named_transformations():
    assert warp.determinant(warp.identity()) == 1.0
    assert warp.determinant(warp.translation(7.0, -3.0)) == 1.0
    assert warp.determinant(warp.shear_x(9.0)) == 1.0
    assert warp.determinant(warp.flip_horizontal(9)) == -1.0
    assert warp.determinant(warp.scaling(2.0, 3.0)) == 6.0


def test_inverse_round_trips_within_tolerance():
    matrix = warp.compose(
        warp.shear_x(0.5), warp.about_centre(warp.rotation(math.radians(37)), 9, 9)
    )
    assert warp.matrices_close(
        warp.compose(warp.invert(matrix), matrix), warp.identity(), TOL
    )
    assert warp.matrices_close(
        warp.compose(matrix, warp.invert(matrix)), warp.identity(), TOL
    )


def test_a_collapsing_transformation_cannot_be_inverted(img):
    collapse = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    assert warp.determinant(collapse) == 0.0
    with pytest.raises(warp.SingularTransform):
        warp.invert(collapse)
    # And therefore it cannot be applied at all, because inverse mapping needs
    # the inverse.
    with pytest.raises(warp.SingularTransform):
        warp.warp_nearest(img, collapse, fill=FILL)


def test_singular_transform_is_catchable_as_a_value_error():
    assert issubclass(warp.SingularTransform, ValueError)


def test_affine_maps_send_parallel_lines_to_parallel_lines():
    for matrix in (warp.rotation(0.7), warp.shear_x(2.0), warp.scaling(3.0, 0.5)):
        p0 = warp.apply_point(matrix, (0.0, 0.0))
        p1 = warp.apply_point(matrix, (1.0, 0.0))
        p2 = warp.apply_point(matrix, (0.0, 5.0))
        p3 = warp.apply_point(matrix, (1.0, 5.0))
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        assert abs(v1[0] * v2[1] - v1[1] * v2[0]) <= TOL


# -- Forward mapping: the failure, asserted ---------------------------------


def test_forward_mapping_leaves_holes_on_a_rotation(img):
    matrix = warp.about_centre(warp.rotation(math.radians(30)), 9, 9)
    _, holes = warp.warp_forward(img, matrix, fill=FILL)
    assert int(holes.sum()) == 22
    assert holes.shape == (9, 9)


def test_forward_mapping_holes_are_arithmetically_unavoidable_when_enlarging(img):
    _, holes = warp.warp_forward(
        img, warp.scaling(2.0, 2.0), out_shape=(18, 18), fill=FILL
    )
    # 81 input pixels cannot fill 324 output pixels, whatever the rounding does.
    assert int(holes.sum()) == 243
    assert int(holes.sum()) >= holes.size - img.size


def test_forward_mapping_overwrites_when_shrinking(img):
    _, holes = warp.warp_forward(
        img, warp.scaling(0.5, 0.5), out_shape=(5, 5), fill=FILL
    )
    assert int(holes.sum()) == 0  # no holes ...
    landings = {}
    for y in range(9):
        for x in range(9):
            fx, fy = warp.apply_point(warp.scaling(0.5, 0.5), (x + 0.5, y + 0.5))
            landings.setdefault((math.floor(fy), math.floor(fx)), []).append((y, x))
    # ... but 24 of the 25 output pixels were written more than once.
    assert sum(1 for v in landings.values() if len(v) > 1) == 24
    assert max(len(v) for v in landings.values()) == 4


def test_inverse_mapping_has_no_holes_only_clipping(img):
    matrix = warp.about_centre(warp.rotation(math.radians(30)), 9, 9)
    out = warp.warp_nearest(img, matrix, fill=FILL)
    back = warp.invert(matrix)
    filled = np.argwhere(out == FILL)
    assert len(filled) == 12
    for oy, ox in filled:
        sx, sy = warp.apply_point(back, (ox + 0.5, oy + 0.5))
        inside = 0 <= math.floor(sx) < 9 and 0 <= math.floor(sy) < 9
        assert not inside, (oy, ox)


# -- Inverse mapping: exact answers ------------------------------------------


@pytest.mark.parametrize("turns", [1, 2, 3, 4])
def test_quarter_turns_match_numpy_rot90_exactly(img, turns):
    matrix = warp.about_centre(warp.rotation_quarter_turns(turns), 9, 9)
    out = warp.warp_nearest(img, matrix, fill=FILL)
    assert np.array_equal(out, np.rot90(img, -turns))
    assert int((out == FILL).sum()) == 0


def test_a_quarter_turn_moves_named_pixels_to_named_places(img):
    matrix = warp.about_centre(warp.rotation_quarter_turns(1), 9, 9)
    out = warp.warp_nearest(img, matrix, fill=FILL)
    # The corner mark: bottom-right to bottom-left.
    assert tuple(int(v) for v in np.argwhere(img == pattern.MARK)[0]) == (8, 8)
    assert tuple(int(v) for v in np.argwhere(out == pattern.MARK)[0]) == (8, 0)
    # The top bar, row 0 columns 1..6, becomes column 8 rows 1..6.
    bar = sorted(int(r) for r, c in np.argwhere(out == pattern.INK) if c == 8)
    assert bar == list(range(1, 7))
    assert len(pattern.ink_cells(out)) == len(pattern.ink_cells(img)) == 24


def test_the_trigonometric_quarter_turn_gives_identical_pixels(img):
    exact = warp.warp_nearest(
        img, warp.about_centre(warp.rotation_quarter_turns(1), 9, 9), fill=FILL
    )
    trig = warp.warp_nearest(
        img, warp.about_centre(warp.rotation(math.pi / 2), 9, 9), fill=FILL
    )
    assert np.array_equal(exact, trig)


def test_flips_match_numpy_exactly(img):
    assert np.array_equal(
        warp.warp_nearest(img, warp.flip_horizontal(9), fill=FILL), np.fliplr(img)
    )
    assert np.array_equal(
        warp.warp_nearest(img, warp.flip_vertical(9), fill=FILL), np.flipud(img)
    )


def test_flipping_twice_restores_the_original(img):
    once = warp.warp_nearest(img, warp.flip_horizontal(9), fill=FILL)
    twice = warp.warp_nearest(once, warp.flip_horizontal(9), fill=FILL)
    assert np.array_equal(twice, img)


def test_doubling_is_exact_pixel_replication(img):
    out = warp.warp_nearest(img, warp.scaling(2.0, 2.0), out_shape=(18, 18), fill=FILL)
    assert np.array_equal(out, np.kron(img, np.ones((2, 2), dtype=np.uint8)))
    assert int((out == FILL).sum()) == 0
    # Four times the pixels, exactly the same information.
    assert len(np.unique(out)) == len(np.unique(img)) == 3


def test_halving_is_exactly_a_strided_slice(img):
    out = warp.warp_nearest(img, warp.scaling(0.5, 0.5), out_shape=(4, 4), fill=FILL)
    assert np.array_equal(out, img[1::2, 1::2])
    # The single-pixel corner mark is one of the pixels thrown away.
    assert int((out == pattern.MARK).sum()) == 0


def test_translation_matches_a_slice_and_pad(img):
    out = warp.warp_nearest(img, warp.translation(2.0, 1.0), fill=FILL)
    reference = np.full_like(img, FILL)
    reference[1:, 2:] = img[:-1, :-2]
    assert np.array_equal(out, reference)
    assert int((out == FILL).sum()) == 2 * 9 + 9 - 2


@pytest.mark.parametrize(
    "k,out_width,expected_row0_shift", [(0.5, 14, 0), (1.0, 18, 0), (2.0, 27, 1)]
)
def test_the_half_pixel_offset_decides_whether_row_0_moves(
    img, k, out_width, expected_row0_shift
):
    """The question Day 102 deferred, asserted as a number.

    Row 0's output pixels are sampled at y = 0.5, not y = 0, so the shear term
    contributes k * 0.5 even in the top row.
    """
    out = warp.warp_nearest(
        img, warp.shear_x(k), out_shape=(9, out_width), fill=FILL
    )
    first_ink = int(np.argmax(out[0] == pattern.INK))
    assert first_ink - 1 == expected_row0_shift
    assert first_ink - 1 == -math.floor(warp.SAMPLE_OFFSET - k * warp.SAMPLE_OFFSET)


def test_a_shear_preserves_the_ink_count(img):
    out = warp.warp_nearest(img, warp.shear_x(1.0), out_shape=(9, 18), fill=FILL)
    assert warp.determinant(warp.shear_x(1.0)) == 1.0
    assert int((out == pattern.INK).sum()) == int((img == pattern.INK).sum()) == 24


def test_colour_is_transformed_plane_by_plane_with_the_same_matrix():
    colour = pattern.make_colour_pattern()
    matrix = warp.about_centre(warp.rotation_quarter_turns(1), 9, 9)
    out = warp.warp_colour(colour, matrix, fill=FILL)
    assert out.shape == (9, 9, 3)
    for channel in range(3):
        assert np.array_equal(out[:, :, channel], np.rot90(colour[:, :, channel], -1))


def test_warp_rejects_a_colour_array_with_a_helpful_message():
    colour = pattern.make_colour_pattern()
    with pytest.raises(ValueError) as caught:
        warp.warp_nearest(colour, warp.identity(), fill=FILL)
    assert "(height, width)" in str(caught.value)


# -- Composing versus repeating ---------------------------------------------


def test_a_full_turn_as_one_matrix_is_pixel_exact(img):
    out = warp.warp_nearest(
        img, warp.about_centre(warp.rotation(2.0 * math.pi), 9, 9), fill=FILL
    )
    assert np.array_equal(out, img)


def test_twelve_separate_thirty_degree_turns_are_not(img):
    step = warp.about_centre(warp.rotation(math.radians(30)), 9, 9)
    out = img
    for _ in range(12):
        out = warp.warp_nearest(out, step, fill=FILL)
    assert int((out != img).sum()) == 16
    assert not np.array_equal(out, img)


def test_the_same_twelve_turns_composed_into_one_matrix_are_exact(img):
    step = warp.about_centre(warp.rotation(math.radians(30)), 9, 9)
    combined = warp.identity()
    for _ in range(12):
        combined = warp.compose(step, combined)
    assert warp.matrices_close(combined, warp.identity(), TOL)
    assert np.array_equal(warp.warp_nearest(img, combined, fill=FILL), img)


def test_one_composed_matrix_agrees_with_three_separate_steps_on_every_point():
    steps = [
        warp.about_centre(warp.rotation(math.radians(30)), 9, 9),
        warp.shear_x(0.5),
        warp.about_centre(warp.scaling(1.5, 1.5), 9, 9),
    ]
    combined = warp.identity()
    for matrix in steps:
        combined = warp.compose(matrix, combined)
    for y in range(9):
        for x in range(9):
            point = (x + 0.5, y + 0.5)
            stepwise = point
            for matrix in steps:
                stepwise = warp.apply_point(matrix, stepwise)
            at_once = warp.apply_point(combined, point)
            for a, b in zip(stepwise, at_once):
                assert abs(a - b) <= TOL


def test_an_integer_shear_round_trip_is_lossy_across_two_passes(img):
    """A boundary case that is asserted rather than hidden.

    k = 1.0 puts every sample exactly on a pixel boundary, where floor must
    make an arbitrary choice; k = 0.5 keeps samples well inside a pixel.
    """
    half = warp.warp_nearest(img, warp.shear_x(0.5), out_shape=(9, 14), fill=FILL)
    half_back = warp.warp_nearest(half, warp.shear_x(-0.5), out_shape=(9, 9), fill=FILL)
    assert np.array_equal(half_back, img)

    unit = warp.warp_nearest(img, warp.shear_x(1.0), out_shape=(9, 18), fill=FILL)
    unit_back = warp.warp_nearest(unit, warp.shear_x(-1.0), out_shape=(9, 9), fill=FILL)
    assert int((unit_back != img).sum()) == 28

    # As ONE composed matrix it is exact for both.
    for k in (0.5, 1.0):
        combined = warp.compose(warp.shear_x(-k), warp.shear_x(k))
        assert warp.matrices_close(combined, warp.identity(), TOL)
        assert np.array_equal(warp.warp_nearest(img, combined, fill=FILL), img)


# -- Against Pillow ----------------------------------------------------------


def test_pillow_coefficients_run_output_to_input():
    probe = np.zeros((1, 8), dtype=np.uint8)
    probe[0, 3] = 255
    out = pillow_affine(probe, (1, 0, 1, 0, 1, 0))
    # A positive c moved the content LEFT: the coefficients are the inverse.
    assert int(np.argmax(out[0])) == 2


def test_to_pillow_coefficients_inverts_the_matrix():
    coefficients = warp.to_pillow_coefficients(warp.translation(1.0, 0.0))
    assert tuple(round(v, 12) for v in coefficients) == (1.0, 0.0, -1.0, 0.0, 1.0, 0.0)
    assert warp.coefficients_to_matrix(coefficients)[2] == [0.0, 0.0, 1.0]


def test_pillow_samples_at_pixel_centres_not_at_integer_corners():
    """Settles the sampling question Day 102 deferred, by measurement."""
    row = (np.arange(8, dtype=np.uint8) * 10).reshape(1, 8)
    observed = [int(v) for v in pillow_affine(row, (2, 0, 0, 0, 1, 0))[0]]

    def predict(rule):
        return [
            int(row[0, rule(x)]) if 0 <= rule(x) < 8 else FILL for x in range(8)
        ]

    centres = predict(lambda x: math.floor(2 * (x + 0.5)))
    corners = predict(lambda x: math.floor(2 * x + 0.5))
    assert observed == centres
    assert observed != corners
    assert warp.SAMPLE_OFFSET == 0.5


def test_pillows_shear_moves_row_zero_and_the_offset_explains_it():
    strip = np.zeros((3, 9), dtype=np.uint8)
    strip[:, 4] = 255
    out = pillow_affine(strip, (1, 2, 0, 0, 1, 0))
    for y, expected_shift in ((0, 1), (1, 3)):
        found = np.flatnonzero(out[y] == 255)
        assert found.size == 1
        assert int(found[0]) == 4 - expected_shift
        assert expected_shift == math.floor(0.5 + 2 * (y + 0.5))


def test_ours_and_pillow_agree_exactly_on_510_affine_transformations(img):
    rng = random.Random(105)
    cases = []
    for _ in range(500):
        theta = rng.uniform(-math.pi, math.pi)
        scale = rng.uniform(0.4, 2.5)
        skew = rng.uniform(-2.5, 2.5)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        cases.append((
            scale * cos_t,
            scale * (cos_t * skew - sin_t),
            rng.uniform(-6, 6),
            scale * sin_t,
            scale * (sin_t * skew + cos_t),
            rng.uniform(-6, 6),
        ))
    cases += [
        (1, 0, 0, 0, 1, 0),
        (1, 0, 1, 0, 1, 0),
        (1, 0, 0.5, 0, 1, 0),
        (1, 2, 0, 0, 1, 0),
        (2, 0, 0, 0, 2, 0),
        (0.5, 0, 0, 0, 0.5, 0),
        (0, -1, 9, 1, 0, 0),
        (-1, 0, 9, 0, -1, 9),
        (1, 0, -3, 0, 1, -3),
        (1, 0.5, 0, 0, 1, 0),
    ]
    assert len(cases) == 510
    for coefficients in cases:
        mine = warp.warp_nearest_with_inverse(
            img, warp.coefficients_to_matrix(coefficients), fill=FILL
        )
        theirs = pillow_affine(img, coefficients)
        assert int((mine != theirs).sum()) == pattern.PIXEL_TOL == 0


def test_where_ours_and_pillow_disagree_the_sample_is_on_a_pixel_boundary(img):
    """The honest half of the comparison.

    Eight of the 360 whole-degree rotations differ, by at most 2 pixels of 81,
    and every disagreeing sample lands within one ulp of a pixel boundary.
    """
    disagreeing = []
    furthest = 0.0
    for degrees in range(360):
        matrix = warp.about_centre(warp.rotation(math.radians(degrees)), 9, 9)
        coefficients = warp.to_pillow_coefficients(matrix)
        mine = warp.warp_nearest(img, matrix, fill=FILL)
        theirs = pillow_affine(img, coefficients)
        wrong = np.argwhere(mine != theirs)
        if len(wrong):
            disagreeing.append((degrees, len(wrong)))
        a, b, c, d, e, f = coefficients
        for oy, ox in wrong:
            xs = a * (ox + 0.5) + b * (oy + 0.5) + c
            ys = d * (ox + 0.5) + e * (oy + 0.5) + f
            furthest = max(
                furthest, min(abs(xs - round(xs)), abs(ys - round(ys)))
            )

    assert [deg for deg, _ in disagreeing] == [30, 60, 120, 150, 210, 240, 300, 330]
    assert max(count for _, count in disagreeing) == 2
    assert furthest < 1e-9


def test_the_thirty_degree_disagreement_is_one_pixel_at_a_tie(img):
    matrix = warp.about_centre(warp.rotation(math.radians(30)), 9, 9)
    coefficients = warp.to_pillow_coefficients(matrix)
    mine = warp.warp_nearest(img, matrix, fill=FILL)
    theirs = pillow_affine(img, coefficients)
    wrong = np.argwhere(mine != theirs)
    assert len(wrong) == 1
    oy, ox = int(wrong[0][0]), int(wrong[0][1])
    assert (oy, ox) == (4, 3)
    a, b, c, d, e, f = coefficients
    ys = d * (ox + 0.5) + e * (oy + 0.5) + f
    assert abs(ys - 5.0) < 1e-14
    assert ys != 5.0
    assert math.floor(ys) == 4


def test_pillow_agrees_a_full_turn_is_exact(img):
    matrix = warp.about_centre(warp.rotation(2.0 * math.pi), 9, 9)
    assert math.sin(2.0 * math.pi) != 0.0
    assert warp.matrices_close(matrix, warp.identity(), TOL)
    assert np.array_equal(warp.warp_nearest(img, matrix, fill=FILL), img)
    assert np.array_equal(
        pillow_affine(img, warp.to_pillow_coefficients(matrix)), img
    )


def test_a_non_square_output_agrees_about_which_way_round_the_size_goes(img):
    matrix = warp.shear_x(1.0)
    mine = warp.warp_nearest(img, matrix, out_shape=(9, 18), fill=FILL)
    theirs = pillow_affine(
        img, warp.to_pillow_coefficients(matrix), out_shape=(9, 18)
    )
    assert mine.shape == theirs.shape == (9, 18)
    assert np.array_equal(mine, theirs)


# -- Interpolation -----------------------------------------------------------


def test_bilinear_invents_values_that_nearest_neighbour_cannot(img):
    matrix = warp.translation(0.5, 0.0)
    nearest = warp.warp_nearest(img, matrix, fill=FILL)
    blended = warp.warp_bilinear_with_inverse(
        img, warp.invert(matrix), fill=float(FILL)
    )
    assert set(np.unique(nearest).tolist()) <= set(np.unique(img).tolist()) | {FILL}
    assert len(np.unique(np.round(blended, 6))) > len(np.unique(nearest))


def test_bilinear_at_a_whole_pixel_offset_reduces_to_nearest_neighbour(img):
    matrix = warp.translation(2.0, 1.0)
    nearest = warp.warp_nearest(img, matrix, fill=0)
    blended = warp.warp_bilinear_with_inverse(img, warp.invert(matrix), fill=0.0)
    # No fractional part, so every weight is 0 or 1 and no blending happens.
    assert np.abs(blended - nearest.astype(float)).max() <= 1e-9


@pytest.mark.parametrize(
    "name,matrix",
    [
        ("translate", warp.translation(0.25, 0.25)),
        ("rotate30", warp.about_centre(warp.rotation(math.radians(30)), 9, 9)),
        ("rotate17", warp.about_centre(warp.rotation(math.radians(17)), 9, 9)),
        ("scale", warp.about_centre(warp.scaling(1.5, 1.5), 9, 9)),
        ("shear", warp.shear_x(0.4)),
    ],
)
def test_bilinear_matches_pillow_wherever_all_four_neighbours_are_inside(
    img, name, matrix
):
    """The precise boundary of the agreement, stated as a tolerance.

    Where all four contributing pixels are inside the image, ours and Pillow
    agree to within 1 grey level -- the rounding of a float average into a
    byte. Where a contributor lies outside, they extrapolate differently.
    """
    inverse = warp.invert(matrix)
    mine = warp.warp_bilinear_with_inverse(img, inverse, fill=0.0)
    theirs = pillow_affine(
        img,
        warp.to_pillow_coefficients(matrix),
        resample=Image.Resampling.BILINEAR,
    ).astype(float)

    inside = np.zeros((9, 9), dtype=bool)
    for oy in range(9):
        for ox in range(9):
            sx, sy = warp.apply_point(inverse, (ox + 0.5, oy + 0.5))
            x0 = math.floor(sx - warp.SAMPLE_OFFSET)
            y0 = math.floor(sy - warp.SAMPLE_OFFSET)
            inside[oy, ox] = 0 <= x0 and x0 + 1 < 9 and 0 <= y0 and y0 + 1 < 9

    assert inside.any()
    assert np.abs(mine - theirs)[inside].max() <= 1.0


def test_bilinear_and_pillow_do_diverge_at_the_border(img):
    matrix = warp.about_centre(warp.rotation(math.radians(30)), 9, 9)
    mine = warp.warp_bilinear_with_inverse(img, warp.invert(matrix), fill=0.0)
    theirs = pillow_affine(
        img,
        warp.to_pillow_coefficients(matrix),
        resample=Image.Resampling.BILINEAR,
    ).astype(float)
    # Asserted rather than glossed over: the border difference is large.
    assert np.abs(mine - theirs).max() > 100.0


# -- Files and hygiene -------------------------------------------------------


def test_a_png_round_trip_is_lossless_and_leaves_nothing_behind(img):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "pattern.png")
        Image.fromarray(img, mode="L").save(path)
        assert os.path.getsize(path) > 0
        reloaded = np.asarray(Image.open(path).convert("L"))
        assert np.array_equal(reloaded, img)
    assert not os.path.exists(path)


def test_the_lab_writes_no_image_into_its_own_directory():
    """No image file in the lab's own tree -- the pattern is generated.

    `.venv` is skipped deliberately. It is the documented setup from the
    README, not litter, and Pillow ships a large collection of its own test
    images inside site-packages. Walking into it would fail this test for
    following the installation instructions.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    lab = os.path.dirname(here)
    found = []
    for root, dirs, files in os.walk(lab):
        dirs[:] = [d for d in dirs if d != ".venv"]
        for name in files:
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                found.append(os.path.join(root, name))
    assert found == []


def test_the_installed_versions_are_the_ones_this_lab_was_written_against():
    from importlib.metadata import version

    assert version("numpy").split(".")[0] == "2"
    assert int(version("pillow").split(".")[0]) >= 12
