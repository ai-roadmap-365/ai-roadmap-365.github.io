"""Grouped by what the image plan decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "examples"))

from image_plan import (  # noqa: E402
    COMPONENT_MB,
    Component,
    ImagePlan,
    Purpose,
    Stage,
    compare,
    pull_seconds,
    review,
    rollout_seconds,
)


def rt(*names):
    return [Component(n, Purpose.RUNTIME) for n in names]


def single(base="python-slim", comps=None):
    return ImagePlan(stages=[Stage("final", base, comps or [])], final_stage="final")


# ------------------------------------------------------------------ sizing


def test_a_stage_is_its_base_plus_its_components():
    s = Stage("final", "python-slim", rt("fastapi", "app-code"))
    assert s.size_mb == COMPONENT_MB["python-slim"] + COMPONENT_MB["fastapi"] + COMPONENT_MB["app-code"]


def test_an_unknown_component_contributes_nothing_rather_than_raising():
    assert Component("not-a-real-package", Purpose.RUNTIME).size_mb == 0


def test_only_the_final_stage_ships():
    # THE point of a multi-stage build: the builder is discarded entirely.
    plan = ImagePlan(
        stages=[
            Stage("builder", "python-full", [Component("cuda-devel", Purpose.BUILD)]),
            Stage("final", "python-slim", rt("app-code")),
        ],
        final_stage="final",
    )
    assert plan.size_mb == COMPONENT_MB["python-slim"] + COMPONENT_MB["app-code"]
    assert COMPONENT_MB["cuda-devel"] not in (plan.size_mb,)


def test_carried_components_do_count_toward_the_final_size():
    plan = ImagePlan(
        stages=[Stage("final", "python-slim", [])],
        final_stage="final",
        carried=rt("torch"),
    )
    assert plan.size_mb == COMPONENT_MB["python-slim"] + COMPONENT_MB["torch"]


def test_naming_a_stage_that_does_not_exist_is_an_error():
    plan = ImagePlan(stages=[Stage("final", "python-slim", [])], final_stage="typo")
    try:
        plan.size_mb
    except KeyError:
        return
    raise AssertionError("expected a KeyError for an unknown final stage")


# -------------------------------------------------------------- pull cost


def test_pull_time_scales_with_size():
    assert pull_seconds(200, mbps=200.0) == 8.0
    assert pull_seconds(400, mbps=200.0) == 16.0


def test_a_faster_link_pulls_proportionally_faster():
    assert pull_seconds(1000, mbps=100.0) == 2 * pull_seconds(1000, mbps=200.0)


def test_a_nonsensical_link_speed_does_not_divide_by_zero():
    assert pull_seconds(1000, mbps=0.0) == 0.0


def test_a_rollout_pays_the_pull_once_per_node():
    assert rollout_seconds(1000, 10) == 10 * pull_seconds(1000)


def test_a_rollout_to_no_nodes_costs_nothing():
    assert rollout_seconds(1000, 0) == 0.0
    assert rollout_seconds(1000, -5) == 0.0


# ------------------------------------------------------------------ review


def test_build_tooling_in_the_final_image_is_reported():
    plan = single(comps=[Component("cuda-devel", Purpose.BUILD), *rt("app-code")])
    f = next(x for x in review(plan) if x.rule == "build-tooling-shipped")
    assert f.saves_mb == COMPONENT_MB["cuda-devel"]


def test_build_tooling_confined_to_an_earlier_stage_is_not_reported():
    plan = ImagePlan(
        stages=[
            Stage("builder", "python-full", [Component("cuda-devel", Purpose.BUILD)]),
            Stage("final", "python-slim", rt("app-code")),
        ],
        final_stage="final",
    )
    assert "build-tooling-shipped" not in {f.rule for f in review(plan)}


def test_baked_in_weights_are_reported_with_what_they_cost():
    plan = single(comps=[Component("model-weights-7b", Purpose.DATA), *rt("app-code")])
    f = next(x for x in review(plan) if x.rule == "weights-baked-in")
    assert f.saves_mb == COMPONENT_MB["model-weights-7b"]


def test_mounted_weights_produce_no_finding():
    assert "weights-baked-in" not in {f.rule for f in review(single(comps=rt("app-code")))}


def test_a_full_base_in_the_final_stage_is_reported():
    f = next(x for x in review(single(base="python-full", comps=rt("app-code"))) if x.rule == "fat-base")
    assert f.saves_mb == COMPONENT_MB["python-full"] - COMPONENT_MB["python-slim"]


def test_a_clean_plan_has_no_findings():
    assert review(single(comps=rt("cuda-runtime", "torch", "fastapi", "app-code"))) == []


def test_carried_build_tooling_is_caught_too():
    # Copying a build artefact forward is fine; copying the toolchain is not.
    plan = ImagePlan(
        stages=[Stage("final", "python-slim", rt("app-code"))],
        final_stage="final",
        carried=[Component("build-essential", Purpose.BUILD)],
    )
    assert "build-tooling-shipped" in {f.rule for f in review(plan)}


# ----------------------------------------------------------------- compare


def test_compare_reports_what_was_saved_and_the_ratio():
    before = single(comps=[Component("model-weights-7b", Purpose.DATA), *rt("app-code")])
    after = single(comps=rt("app-code"))
    c = compare(before, after)
    assert c["saved_mb"] == COMPONENT_MB["model-weights-7b"]
    assert c["ratio"] > 1.0


def test_comparing_a_plan_with_itself_saves_nothing():
    p = single(comps=rt("app-code"))
    c = compare(p, p)
    assert c["saved_mb"] == 0 and c["ratio"] == 1.0


def test_moving_the_weights_out_beats_the_multi_stage_build():
    # The finding this lab exists for: multi-stage is the famous optimisation
    # and it is the SMALLER one for an AI image.
    one_stage = single(
        base="python-full",
        comps=[
            Component("build-essential", Purpose.BUILD),
            Component("cuda-devel", Purpose.BUILD),
            *rt("cuda-runtime", "torch", "app-code"),
            Component("model-weights-7b", Purpose.DATA),
        ],
    )
    staged = ImagePlan(
        stages=[
            Stage("builder", "python-full", [
                Component("build-essential", Purpose.BUILD),
                Component("cuda-devel", Purpose.BUILD),
            ]),
            Stage("final", "python-slim", [
                *rt("cuda-runtime", "torch", "app-code"),
                Component("model-weights-7b", Purpose.DATA),
            ]),
        ],
        final_stage="final",
    )
    mounted = ImagePlan(
        stages=staged.stages[:1] + [Stage("final", "python-slim", rt("cuda-runtime", "torch", "app-code"))],
        final_stage="final",
    )
    from_multistage = compare(one_stage, staged)["saved_mb"]
    from_mounting = compare(staged, mounted)["saved_mb"]

    # Moving the weights out is the bigger single win. How much bigger depends
    # on how much build tooling the one-stage image carried, so the claim
    # tested here is the ordering, not a fixed ratio -- an earlier version of
    # this test asserted 3x and failed on a fixture that shipped cuda-devel,
    # where the multi-stage saving is unusually large.
    assert from_mounting > from_multistage
    assert from_mounting == COMPONENT_MB["model-weights-7b"]
