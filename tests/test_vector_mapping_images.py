import numpy as np
import sympy

from core.set_parser import parse_set_2d
from math_modules.vector_mapping_images import (
    compute_image_points,
    compute_preimage_grid,
    compute_preimage_relation_grid,
    sample_relation_grid,
    sample_set_grid,
)
from ui.vector_mapping_images_page import _add_relation_region, _is_identity_mapping


def test_vector_mapping_rectangle_image():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    c_set = parse_set_2d("[-1, 1]x[-1, 1]")
    u, v = compute_image_points(x, y, c_set, ((-1.0, 1.0), (-1.0, 1.0)), 10)
    assert len(u) > 0
    assert min(u) >= -1.0
    assert max(u) <= 1.0


def test_vector_mapping_preimage_relation():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    target = parse_set_2d("u^2 + v^2 <= 1")
    _, _, z = compute_preimage_grid(x, y, target, ((-2.0, 2.0), (-2.0, 2.0)), 40)
    assert z.any()
    assert not z.all()


def test_identity_mapping_detection():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    assert _is_identity_mapping(x, y)
    assert not _is_identity_mapping(x + y, y)


def test_sample_set_grid_heart_relation_is_not_blocky_scatter_data():
    heart = parse_set_2d("(x^2 + y^2 - 1)^3 - x^2*y^3 < 0")
    x_grid, y_grid, mask = sample_set_grid(heart, ((-1.6, 1.6), (-1.3, 1.4)), resolution=120)
    assert x_grid.shape == (120, 120)
    assert y_grid.shape == (120, 120)
    assert mask.shape == (120, 120)
    assert mask.any()
    assert not mask.all()
    assert 0.05 < mask.mean() < 0.6


def test_sample_relation_grid_heart_has_smooth_implicit_boundary_values():
    heart = parse_set_2d("(x^2 + y^2 - 1)^3 - x^2*y^3 < 0")
    X, Y, Z = sample_relation_grid(heart, ((-1.6, 1.6), (-1.3, 1.4)), resolution=120)
    assert X.shape == (120, 120)
    assert Y.shape == (120, 120)
    assert Z.shape == (120, 120)
    assert Z[np.isfinite(Z)].min() < 0
    assert Z[np.isfinite(Z)].max() > 0


def test_compute_preimage_grid_keeps_shape_and_finite_mask():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    target = parse_set_2d("u >= 0")
    X, Y, mask = compute_preimage_grid(x**2 - y, x + y, target, ((-1.0, 1.0), (-1.0, 1.0)), 55)
    assert X.shape == (55, 55)
    assert Y.shape == (55, 55)
    assert mask.shape == (55, 55)
    assert mask.any()
    assert not mask.all()


def test_compute_preimage_relation_grid_substitutes_mapping_into_target_relation():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    target = parse_set_2d("u + v <= 1")
    X, Y, Z = compute_preimage_relation_grid(x + y, x - y, target, ((-1.0, 1.0), (-1.0, 1.0)), 40)
    assert X.shape == (40, 40)
    assert Y.shape == (40, 40)
    assert Z.shape == (40, 40)
    assert abs(float(Z[20, 20]) - float(2 * X[20, 20] - 1)) < 1e-9


def test_add_relation_region_adds_implicit_fill_and_boundary():
    import plotly.graph_objects as go

    heart = parse_set_2d("(x^2 + y^2 - 1)^3 - x^2*y^3 < 0")
    X, Y, Z = sample_relation_grid(heart, ((-1.6, 1.6), (-1.3, 1.4)), resolution=50)
    fig = go.Figure()
    assert _add_relation_region(fig, X[0, :], Y[:, 0], Z, heart.operator, "#1f5f9f", "test")
    assert len(fig.data) >= 2
    fill_values = np.asarray(fig.data[0].z)
    assert fill_values.min() == 0
    assert fill_values.max() == 1
    assert fig.data[-1].line.dash == "dash"


def test_add_relation_region_closed_boundary_is_solid():
    import plotly.graph_objects as go

    disk = parse_set_2d("x^2 + y^2 <= 1")
    X, Y, Z = sample_relation_grid(disk, ((-2.0, 2.0), (-2.0, 2.0)), resolution=40)
    fig = go.Figure()
    assert _add_relation_region(fig, X[0, :], Y[:, 0], Z, disk.operator, "#1f5f9f", "test")
    fill_values = np.asarray(fig.data[0].z)
    assert 0 < fill_values.mean() < 1
    assert fig.data[-1].line.dash == "solid"


def test_compute_image_points_for_non_identity_mapping():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    c_set = parse_set_2d("x^2 + y^2 <= 1")
    u, v = compute_image_points(x + y, x - y, c_set, ((-1.0, 1.0), (-1.0, 1.0)), 60)
    assert len(u) == len(v)
    assert len(u) > 100
    assert min(u) >= -2.0
    assert max(u) <= 2.0


def test_compute_image_points_subsamples_large_scatter_output():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    c_set = parse_set_2d("x^2 + y^2 <= 2")
    u, v = compute_image_points(x, y, c_set, ((-1.0, 1.0), (-1.0, 1.0)), 80, max_points=500)
    assert len(u) == len(v)
    assert 0 < len(u) <= 500


def test_preimage_rejects_points_where_mapping_is_not_finite():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    target = parse_set_2d("u^2 + v^2 <= 100")
    _, _, mask = compute_preimage_grid(1 / (x - y), y, target, ((-1.0, 1.0), (-1.0, 1.0)), 41)
    assert mask.shape == (41, 41)
    assert not mask.all()
