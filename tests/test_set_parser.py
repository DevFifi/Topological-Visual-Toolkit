import numpy as np

from core.set_parser import (
    CompositeSet,
    FinitePointSet,
    Interval1D,
    Rectangle2D,
    Relation2D,
    parse_set_1d,
    parse_set_2d,
    set_latex,
)


def test_parse_closed_and_open_interval_membership():
    closed = parse_set_1d("[0, 1]")
    open_set = parse_set_1d("(0, 1)")
    assert closed.contains_numeric(0)
    assert not open_set.contains_numeric(0)


def test_parse_finite_set_with_latex_fraction():
    parsed = parse_set_1d("{\\frac{1}{2}, pi}")
    assert parsed.contains_numeric(0.5)


def test_parse_rectangle_with_times_symbol():
    parsed = parse_set_2d("[-1,1]×[-1,1]")
    assert parsed.contains_numeric((0, 0))
    assert not parsed.contains_numeric((2, 0))


def test_parse_relation_2d_leq_and_equals():
    disk = parse_set_2d("x^2 + y^2 <= 1")
    circle = parse_set_2d("x^2 + y^2 = 1")
    assert disk.contains_numeric((0, 0))
    assert disk.contains_numeric((1, 0))
    assert circle.contains_numeric((1, 0))
    assert not circle.contains_numeric((0, 0))


def test_parse_relation_2d_uv_variables():
    target = parse_set_2d("u^2 + v^2 <= 1")
    assert target.contains_numeric((0.5, 0.5))
    assert not target.contains_numeric((2.0, 0.0))


def test_reject_reversed_interval_and_malformed_sets():
    assert parse_set_1d("[2, 1]") is None
    assert parse_set_1d("{1, sqrt(}") is None
    assert parse_set_2d("x^2 + <= 1") is None


def test_empty_finite_set_is_valid_but_contains_nothing():
    parsed = parse_set_1d("{}")
    assert parsed is not None
    assert not parsed.contains_numeric(0)


def test_open_interval_boundary_classification():
    parsed = parse_set_1d("(0, 1)")
    assert parsed.classify_numeric(0.0) == "boundary"
    assert parsed.classify_numeric(0.5) == "true"
    assert parsed.classify_numeric(2.0) == "false"


def test_parse_rectangle_with_latex_times_and_unicode_times():
    latex_rect = parse_set_2d(r"[-1,1]\times[-2,2]")
    unicode_rect = parse_set_2d("[-1,1]\u00d7[-2,2]")
    assert isinstance(latex_rect, Rectangle2D)
    assert isinstance(unicode_rect, Rectangle2D)
    assert latex_rect.contains_numeric((0.5, -1.5))
    assert not unicode_rect.contains_numeric((1.5, 0.0))


def test_parse_relations_with_latex_and_unicode_operators():
    le_relation = parse_set_2d(r"x^2 + y^2 \le 1")
    ge_relation = parse_set_2d("u + v \u2265 0")
    neq_relation = parse_set_2d("x != y")
    assert isinstance(le_relation, Relation2D)
    assert isinstance(ge_relation, Relation2D)
    assert le_relation.contains_numeric((0.0, 0.0))
    assert ge_relation.contains_numeric((1.0, -0.5))
    assert neq_relation.contains_numeric((1.0, 2.0))
    assert not neq_relation.contains_numeric((1.0, 1.0))


def test_single_equals_is_treated_as_equality():
    parsed = parse_set_2d("x^2 + y^2 = 1")
    assert isinstance(parsed, Relation2D)
    assert parsed.contains_numeric((1.0, 0.0))
    assert not parsed.contains_numeric((0.0, 0.0))


def test_set_latex_for_relation_and_rectangle():
    disk = parse_set_2d("x^2 + y^2 <= 1")
    rect = parse_set_2d("[-1,1]x[0,2]")
    assert r"\le" in set_latex(disk, "B")
    assert r"\times" in set_latex(rect, "C")


def test_vectorized_contains_arrays_for_rectangle_and_relation():
    rect = parse_set_2d("[-1,1]x[-1,1]")
    disk = parse_set_2d("u^2 + v^2 <= 1")
    xs = np.array([[-2.0, 0.0], [1.0, 2.0]])
    ys = np.array([[0.0, 0.0], [1.0, 2.0]])
    rect_mask = rect.contains_arrays(xs, ys)
    disk_mask = disk.contains_arrays(xs, ys)
    assert rect_mask.tolist() == [[False, True], [True, False]]
    assert disk_mask.tolist() == [[False, True], [False, False]]


def test_vectorized_open_relation_excludes_boundary():
    open_halfplane = parse_set_2d("x < 0")
    xs = np.array([[-1.0, 0.0, 1.0]])
    ys = np.array([[0.0, 0.0, 0.0]])
    assert open_halfplane.contains_arrays(xs, ys).tolist() == [[True, False, False]]


def test_interval_latex_keeps_endpoint_types():
    closed_open = parse_set_1d("[0, 1)")
    assert isinstance(closed_open, Interval1D)
    assert closed_open.to_latex() == "[0, 1)"


def test_parse_composite_1d_union_and_intersection():
    union_set = parse_set_1d("[-1, -1/2] \\lor [1/2, 1]")
    intersection_set = parse_set_1d("[0, 2] and (1, 3)")
    assert isinstance(union_set, CompositeSet)
    assert union_set.contains_numeric(-0.75)
    assert not union_set.contains_numeric(0.0)
    assert intersection_set.contains_numeric(1.5)
    assert not intersection_set.contains_numeric(1.0)


def test_parse_composite_2d_intersection_and_union():
    cap_set = parse_set_2d("(x^2 + y^2 <= 1) \\land (x >= 0)")
    cup_set = parse_set_2d("(x <= -1) or (x >= 1)")
    latex_wrapped = parse_set_2d("(x <= -1) \\(\\lor\\) (x >= 1)")
    assert isinstance(cap_set, CompositeSet)
    assert cap_set.contains_numeric((0.5, 0.0))
    assert not cap_set.contains_numeric((-0.5, 0.0))
    assert cup_set.contains_numeric((-2.0, 0.0))
    assert cup_set.contains_numeric((2.0, 0.0))
    assert not cup_set.contains_numeric((0.0, 0.0))
    assert latex_wrapped.contains_numeric((2.0, 0.0))


def test_parse_chained_inequality_2d():
    annulus = parse_set_2d("1/4 < x^2 + y^2 <= 1")
    assert isinstance(annulus, CompositeSet)
    assert annulus.contains_numeric((0.75, 0.0))
    assert not annulus.contains_numeric((0.25, 0.0))
    assert annulus.classify_numeric((0.5, 0.0)) == "boundary"


def test_parse_finite_point_set_2d_and_symbolic_points():
    points = parse_set_2d("{(0, 0), (e, sqrt(2)), (pi, 1/2)}")
    assert isinstance(points, FinitePointSet)
    assert points.contains_numeric((0.0, 0.0))
    assert points.contains_numeric((float(np.e), float(np.sqrt(2))))
    assert not points.contains_numeric((1.0, 1.0))


def test_composite_set_vectorized_mask():
    parsed = parse_set_2d("(x^2 + y^2 <= 1) && (x >= 0)")
    xs = np.array([[-0.5, 0.5], [2.0, 0.0]])
    ys = np.array([[0.0, 0.0], [0.0, 0.0]])
    assert parsed.contains_arrays(xs, ys).tolist() == [[False, True], [False, True]]


def test_composite_set_latex_uses_union_and_intersection_symbols():
    parsed = parse_set_2d("(x^2 + y^2 <= 1) \\cap (x >= 0)")
    rendered = set_latex(parsed, "C")
    assert r"\cap" in rendered
    assert r"\le" in rendered


def test_parse_unparenthesized_cap_between_relations_before_chained_relation():
    parsed = parse_set_2d(r"x^2 + y^2 <= 1 \cap x*y < 1")
    assert isinstance(parsed, CompositeSet)
    rendered = set_latex(parsed, "C")
    assert r"\cap" in rendered
    assert "AND" not in rendered
    assert parsed.contains_numeric((0.0, 0.0))


def test_parse_top_level_comma_as_intersection_between_relations():
    parsed = parse_set_2d("x^2 + y^2 <= 1, x*y < 1")
    assert isinstance(parsed, CompositeSet)
    assert parsed.contains_numeric((0.0, 0.0))
    assert not parsed.contains_numeric((2.0, 0.0))
