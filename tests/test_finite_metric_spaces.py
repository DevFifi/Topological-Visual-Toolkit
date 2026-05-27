import sympy
from math_modules.finite_metric_spaces import compute_distance, compute_diam, compute_dist_sets, _get_distance_formula

def test_euclidean_distance():
    f, _ = _get_distance_formula("Euclidean", "", 2)
    dv = compute_distance((0, 0), (1, 1), f, "Euclidean")
    assert dv.exact == "sqrt(2)"
    assert abs(float(dv.numeric) - 1.41421356) < 1e-6

def test_diam():
    pts = [(0,0), (1,0), (0,1)]
    dv, _ = compute_diam(pts, "Euclidean")
    assert dv.exact == "sqrt(2)"

def test_dist():
    E = [(0,0)]
    F = [(1,1)]
    dv, _ = compute_dist_sets(E, F, "Euclidean")
    assert dv.exact == "sqrt(2)"
