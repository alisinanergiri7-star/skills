"""
Tests for slack-gif-creator easing functions.

All easing functions f(t) must satisfy:
  - f(0) == 0  (start at zero)
  - f(1) == 1  (end at one)
  - output is in a reasonable range (elastic/back can overshoot slightly)
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "slack-gif-creator"))

from core.easing import (
    linear,
    ease_in_quad,
    ease_out_quad,
    ease_in_out_quad,
    ease_in_cubic,
    ease_out_cubic,
    ease_in_out_cubic,
    ease_in_bounce,
    ease_out_bounce,
    ease_in_out_bounce,
    ease_in_elastic,
    ease_out_elastic,
    ease_in_out_elastic,
    ease_back_in,
    ease_back_out,
    ease_back_in_out,
    get_easing,
    interpolate,
    apply_squash_stretch,
    calculate_arc_motion,
    EASING_FUNCTIONS,
)

# All standard easing functions that must satisfy f(0)=0, f(1)=1
STANDARD_EASING_FUNCTIONS = [
    linear,
    ease_in_quad,
    ease_out_quad,
    ease_in_out_quad,
    ease_in_cubic,
    ease_out_cubic,
    ease_in_out_cubic,
    ease_in_bounce,
    ease_out_bounce,
    ease_in_out_bounce,
    ease_in_elastic,
    ease_out_elastic,
    ease_in_out_elastic,
    ease_back_in,
    ease_back_out,
    ease_back_in_out,
]


class TestBoundaryConditions:
    """All easing functions must map 0->0 and 1->1."""

    @pytest.mark.parametrize("fn", STANDARD_EASING_FUNCTIONS)
    def test_starts_at_zero(self, fn):
        assert fn(0) == pytest.approx(0.0, abs=1e-9), f"{fn.__name__}(0) should be 0"

    @pytest.mark.parametrize("fn", STANDARD_EASING_FUNCTIONS)
    def test_ends_at_one(self, fn):
        assert fn(1) == pytest.approx(1.0, abs=1e-9), f"{fn.__name__}(1) should be 1"


class TestLinear:
    def test_midpoint(self):
        assert linear(0.5) == pytest.approx(0.5)

    def test_quarter(self):
        assert linear(0.25) == pytest.approx(0.25)

    def test_identity(self):
        for t in [0.0, 0.1, 0.3, 0.7, 0.9, 1.0]:
            assert linear(t) == pytest.approx(t)


class TestQuadEasing:
    def test_ease_in_quad_accelerates(self):
        # ease_in should be slow at start: f(0.5) < 0.5
        assert ease_in_quad(0.5) < 0.5

    def test_ease_out_quad_decelerates(self):
        # ease_out should be fast at start: f(0.5) > 0.5
        assert ease_out_quad(0.5) > 0.5

    def test_ease_in_out_quad_symmetric_midpoint(self):
        assert ease_in_out_quad(0.5) == pytest.approx(0.5)

    def test_ease_in_out_quad_slow_at_start(self):
        assert ease_in_out_quad(0.25) < 0.25

    def test_ease_in_out_quad_fast_at_end(self):
        assert ease_in_out_quad(0.75) > 0.75


class TestCubicEasing:
    def test_ease_in_cubic_slower_than_quad(self):
        # cubic ease-in accelerates more aggressively than quad
        assert ease_in_cubic(0.5) < ease_in_quad(0.5)

    def test_ease_out_cubic_faster_than_quad_at_start(self):
        assert ease_out_cubic(0.5) > ease_out_quad(0.5)

    def test_ease_in_out_cubic_midpoint(self):
        assert ease_in_out_cubic(0.5) == pytest.approx(0.5)


class TestBounceEasing:
    def test_bounce_out_lands_at_one(self):
        assert ease_out_bounce(1.0) == pytest.approx(1.0)

    def test_bounce_in_starts_at_zero(self):
        assert ease_in_bounce(0.0) == pytest.approx(0.0)

    def test_bounce_in_out_midpoint(self):
        assert ease_in_out_bounce(0.5) == pytest.approx(0.5)

    def test_bounce_out_always_positive(self):
        for t in [i / 20 for i in range(21)]:
            assert ease_out_bounce(t) >= -1e-9

    def test_bounce_in_out_symmetric(self):
        # f(t) + f(1-t) should equal 1 due to symmetry
        for t in [0.1, 0.2, 0.3, 0.4]:
            assert ease_in_out_bounce(t) + ease_in_out_bounce(1 - t) == pytest.approx(1.0, abs=1e-9)


class TestElasticEasing:
    def test_elastic_in_boundary_values(self):
        assert ease_in_elastic(0) == 0.0
        assert ease_in_elastic(1) == 1.0

    def test_elastic_out_boundary_values(self):
        assert ease_out_elastic(0) == 0.0
        assert ease_out_elastic(1) == 1.0

    def test_elastic_can_overshoot(self):
        # Elastic functions can exceed [0, 1] range — that's expected
        values = [ease_out_elastic(t) for t in [i / 20 for i in range(1, 20)]]
        assert any(v > 1.0 or v < 0.0 for v in values), "Elastic should overshoot [0,1]"


class TestBackEasing:
    def test_back_in_can_go_negative(self):
        # ease_back_in overshoots backward before moving forward
        mid_values = [ease_back_in(t) for t in [0.1, 0.2, 0.3]]
        assert any(v < 0 for v in mid_values), "ease_back_in should dip below 0"

    def test_back_out_can_exceed_one(self):
        mid_values = [ease_back_out(t) for t in [0.7, 0.8, 0.9]]
        assert any(v > 1.0 for v in mid_values), "ease_back_out should overshoot 1"

    def test_back_in_out_midpoint(self):
        assert ease_back_in_out(0.5) == pytest.approx(0.5, abs=1e-9)


class TestGetEasing:
    def test_known_names(self):
        assert get_easing("linear") is linear
        assert get_easing("ease_in") is ease_in_quad
        assert get_easing("bounce_out") is ease_out_bounce

    def test_unknown_name_falls_back_to_linear(self):
        assert get_easing("nonexistent_easing") is linear

    def test_all_registry_entries_are_callable(self):
        for name, fn in EASING_FUNCTIONS.items():
            assert callable(fn), f"EASING_FUNCTIONS['{name}'] is not callable"


class TestInterpolate:
    def test_start_value_at_t0(self):
        assert interpolate(10, 20, 0.0) == pytest.approx(10.0)

    def test_end_value_at_t1(self):
        assert interpolate(10, 20, 1.0) == pytest.approx(20.0)

    def test_midpoint_linear(self):
        assert interpolate(0, 100, 0.5, "linear") == pytest.approx(50.0)

    def test_negative_range(self):
        assert interpolate(-10, 10, 0.5, "linear") == pytest.approx(0.0)

    def test_with_easing(self):
        # ease_in_quad at t=0.5 should give a value < midpoint
        result = interpolate(0, 100, 0.5, "ease_in")
        assert result < 50.0


class TestApplySquashStretch:
    def test_vertical_squash(self):
        w, h = apply_squash_stretch((1.0, 1.0), 0.5, "vertical")
        assert h < 1.0
        assert w > 1.0

    def test_horizontal_squash(self):
        w, h = apply_squash_stretch((1.0, 1.0), 0.5, "horizontal")
        assert w < 1.0
        assert h > 1.0

    def test_both_squash(self):
        w, h = apply_squash_stretch((1.0, 1.0), 0.5, "both")
        assert w < 1.0
        assert h < 1.0

    def test_zero_intensity_no_change(self):
        w, h = apply_squash_stretch((1.0, 1.0), 0.0, "vertical")
        assert w == pytest.approx(1.0)
        assert h == pytest.approx(1.0)

    def test_returns_tuple(self):
        result = apply_squash_stretch((1.0, 1.0), 0.3)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestCalculateArcMotion:
    def test_starts_at_start(self):
        x, y = calculate_arc_motion((0, 0), (100, 100), 50, 0.0)
        assert x == pytest.approx(0.0)
        assert y == pytest.approx(0.0)

    def test_ends_at_end(self):
        x, y = calculate_arc_motion((0, 0), (100, 100), 50, 1.0)
        assert x == pytest.approx(100.0)
        assert y == pytest.approx(100.0)

    def test_midpoint_x_linear(self):
        x, _ = calculate_arc_motion((0, 0), (100, 0), 50, 0.5)
        assert x == pytest.approx(50.0)

    def test_arc_peaks_at_midpoint(self):
        # With upward arc (positive height), y at t=0.5 should be lower (upward = negative y offset)
        _, y_mid = calculate_arc_motion((0, 0), (0, 0), 50, 0.5)
        _, y_start = calculate_arc_motion((0, 0), (0, 0), 50, 0.0)
        _, y_end = calculate_arc_motion((0, 0), (0, 0), 50, 1.0)
        # arc_offset peaks at midpoint, so y_mid should differ from start/end
        assert y_mid != y_start

    def test_zero_height_is_linear(self):
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            x, y = calculate_arc_motion((0, 0), (100, 100), 0, t)
            assert x == pytest.approx(100 * t)
            assert y == pytest.approx(100 * t)
