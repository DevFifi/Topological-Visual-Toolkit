import numpy as np

from core.set_parser import parse_set_2d
from ui.bernstein_approximation_page import _animation_degrees
from ui.components import _format_point_history_option


def test_point_history_option_formats_large_generator_like_table_row():
    label = _format_point_history_option("E", "random(count=1000, dim=50, seed=11, scale=2)")
    assert label.startswith("[E] | n=50 | 1000 | random(")
    assert "pkt" not in label
    assert "Zbiór" not in label
    assert "Zbior" not in label


def test_point_history_option_formats_finite_points_with_dimension_and_count():
    label = _format_point_history_option("Zbior F", "(0,0,2)\n(1,1,0)\n(e,sqrt(2),pi)")
    assert label.startswith("[F] | n=3 | 3 | [(0,0,2), (1,1,0), ...]")


def test_point_history_option_formats_box_sets_as_infinite():
    label = _format_point_history_option("E", "[-1,1]x[-1,1]x[0,2]")
    assert label.startswith("[E] | n=3 | ∞ | ")


def test_animation_degrees_uses_all_small_degrees():
    assert _animation_degrees(8, 20) == list(range(1, 9))


def test_animation_degrees_samples_full_large_range():
    degrees = _animation_degrees(10000, 101)
    assert degrees[0] == 1
    assert degrees[-1] == 10000
    assert len(degrees) <= 101
    assert degrees == sorted(set(degrees))
    assert 4800 < degrees[len(degrees) // 2] < 5200


def test_open_relation_grid_does_not_erode_near_boundary_points():
    half_plane = parse_set_2d("y < 0")
    x_values = np.asarray([[0.0, 0.0, 0.0]])
    y_values = np.asarray([[-1e-12, 0.0, 1e-12]])
    mask = half_plane.contains_arrays(x_values, y_values, tolerance=1e-6)
    assert mask.tolist() == [[True, False, False]]
