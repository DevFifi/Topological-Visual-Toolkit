import sympy

from math_modules.finite_metric_spaces import (
    _get_distance_formula,
    compute_diam,
    compute_dist_sets,
    compute_distance,
    compute_distance_matrix,
    metric_formula_latex,
    metric_symbol_latex,
)
from ui.finite_metric_spaces_page import _default_points_text, _metric_options_order, _parse_points, _resize_points_text


def test_euclidean_distance():
    formula, status = _get_distance_formula("Euclidean", "", 2)
    assert status == "exact_and_numeric"
    dv = compute_distance((0, 0), (1, 1), formula, "Euclidean")
    assert dv.exact == "sqrt(2)"
    assert abs(float(dv.numeric) - 1.41421356) < 1e-6


def test_diam():
    pts = [(0, 0), (1, 0), (0, 1)]
    dv, _ = compute_diam(pts, "Euclidean")
    assert dv.exact == "sqrt(2)"


def test_dist():
    E = [(0, 0)]
    F = [(1, 1)]
    dv, _ = compute_dist_sets(E, F, "Euclidean")
    assert dv.exact == "sqrt(2)"


def test_minkowski_p_less_than_one_uses_lecture_definition():
    formula, status = _get_distance_formula("Minkowski", "1/2", 2)
    assert status == "exact_and_numeric"
    dv = compute_distance((0, 0), (4, 9), formula, "Minkowski")
    assert abs(float(dv.numeric) - 5.0) < 1e-9


def test_minkowski_p_one_matches_manhattan():
    formula, status = _get_distance_formula("Minkowski", "1", 2)
    assert status == "exact_and_numeric"
    dv = compute_distance((0, 0), (2, -3), formula, "Minkowski")
    assert abs(float(dv.numeric) - 5.0) < 1e-9


def test_custom_sum_abs_metric():
    formula, status = _get_distance_formula("custom", "SUM(|xi-yi|)", 3)
    assert status == "exact_and_numeric"
    dv = compute_distance((0, 1, 2), (2, 1, -1), formula, "custom")
    assert abs(float(dv.numeric) - 5.0) < 1e-9


def test_polish_metric_name_and_symbol():
    formula, status = _get_distance_formula("Euklidesowa", "", 2)
    assert status == "exact_and_numeric"
    assert metric_symbol_latex("Minkowskiego", "\\frac{1}{2}") == r"d_{\frac{1}{2}}"
    dv = compute_distance((0, 0), (3, 4), formula, "Euklidesowa")
    assert abs(float(dv.numeric) - 5.0) < 1e-9


def test_exact_latex_uses_euler_symbol():
    formula, status = _get_distance_formula("Euklidesowa", "", 2)
    assert status == "exact_and_numeric"
    dv = compute_distance((sympy.E, 0), (0, 0), formula, "Euklidesowa")
    assert dv.exact_latex == "e"


def test_distance_matrix_has_latex_for_symbolic_values():
    matrix = compute_distance_matrix([(0, 0), (sympy.E, sympy.sqrt(2))], "Euklidesowa")
    cell = matrix[0][1]
    assert cell.status == "exact_and_numeric"
    assert r"\sqrt" in cell.exact_latex
    assert "e" in cell.exact_latex
    assert "E" not in cell.exact_latex


def test_resize_points_to_higher_dimension_pads_each_point():
    resized, valid = _resize_points_text("(1, 2)\n(3, 4, 5)\ne", 4)
    assert valid
    assert resized.splitlines() == [
        "(1, 2, 0, 0)",
        "(3, 4, 5, 0)",
        "(e, 0, 0, 0)",
    ]


def test_resize_points_to_lower_dimension_truncates_each_point():
    resized, valid = _resize_points_text("(1, 2, 3), (4, 5), (6)", 2)
    assert valid
    assert resized.splitlines() == ["(1, 2)", "(4, 5)", "(6, 0)"]


def test_resize_points_invalid_input_is_preserved():
    original = "(1, 2)\n(3, sqrt()"
    resized, valid = _resize_points_text(original, 3)
    assert not valid
    assert resized == original


def test_default_points_match_selected_dimension():
    assert _default_points_text(1) == "[1, 2]"
    assert _default_points_text(3) == "[(0, 0, 0), (1, 1, 1)]"


def test_parse_points_accepts_loose_parenthesized_list():
    points, valid = _parse_points("(1, 2), (3, 4)", 2)
    assert valid
    assert points == [(sympy.Integer(1), sympy.Integer(2)), (sympy.Integer(3), sympy.Integer(4))]


def test_parse_points_rejects_wrong_dimension_in_strict_mode():
    points, valid = _parse_points("(1, 2)\n(3, 4, 5)", 2)
    assert not valid
    assert points == [(sympy.Integer(1), sympy.Integer(2))]


def test_minkowski_nonpositive_parameter_is_rejected():
    assert _get_distance_formula("Minkowskiego", "0", 2)[1] == "error"
    assert _get_distance_formula("Minkowskiego", "-1", 2)[1] == "error"


def test_minkowski_fraction_between_zero_and_one_has_no_root():
    formula, status = _get_distance_formula("Minkowskiego", "1/2", 2)
    assert status == "exact_and_numeric"
    dv = compute_distance((0, 0), (4, 9), formula, "Minkowskiego")
    assert dv.exact == "5"
    assert float(dv.numeric) == 5.0


def test_discrete_and_hamming_metrics():
    discrete_formula, _ = _get_distance_formula("Dyskretna", "", 2)
    hamming_formula, _ = _get_distance_formula("Hamminga", "", 3)
    same = compute_distance((sympy.E, 1), (sympy.E, 1), discrete_formula, "Dyskretna")
    different = compute_distance((sympy.E, 1), (sympy.E, 2), discrete_formula, "Dyskretna")
    hamming = compute_distance((1, 2, 3), (1, 0, 4), hamming_formula, "Hamminga")
    assert same.exact == "0"
    assert different.exact == "1"
    assert hamming.exact == "2"


def test_metric_symbols_and_formula_latex_are_readable():
    assert metric_symbol_latex("Czebyszewa") == r"d_{\infty}"
    assert metric_symbol_latex("Dyskretna") == r"\delta"
    assert metric_symbol_latex("Hamminga") == r"d_{H}"
    assert metric_symbol_latex("Własna") == r"\varphi"
    assert metric_symbol_latex("Minkowskiego", r"\frac{1}{2}") == r"d_{\frac{1}{2}}"
    assert metric_formula_latex("Euklidesowa", "", 2).startswith(r"d_{2}(x,y)")


def test_metric_options_are_ordered_from_discrete_to_minkowski_family():
    assert _metric_options_order() == [
        "Dyskretna",
        "Hamminga",
        "Manhattan",
        "Euklidesowa",
        "Minkowskiego",
        "Czebyszewa",
        "Własna",
    ]


def test_distance_set_rejects_mismatched_dimensions():
    dv, pair = compute_dist_sets([(0, 0)], [(1, 2, 3)], "Euklidesowa")
    assert dv.status == "error"
    assert pair == (-1, -1)
