import sympy

from math_modules.supremum_interval import compute_supremum_interval


def test_supremum_interval_poly():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(x**2, x, 0.0, 1.0)
    assert abs(float(dv.numeric) - 0.25) < 1e-5
    assert abs(max_x[0] - 0.5) < 1e-3


def test_supremum_interval_trig():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(sympy.sin(x), sympy.sympify(0), 0.0, float(sympy.pi.evalf()))
    assert abs(float(dv.numeric) - 1.0) < 1e-5
    assert abs(max_x[0] - float((sympy.pi / 2).evalf())) < 1e-3


def test_supremum_interval_endpoint_maximum():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(x, sympy.sympify(0), 0.0, 2.0)
    assert abs(float(dv.numeric) - 2.0) < 1e-7
    assert abs(max_x[0] - 2.0) < 1e-5


def test_supremum_interval_invalid_bounds():
    x = sympy.Symbol("x", real=True)
    dv, _, _, _, _ = compute_supremum_interval(x, sympy.sympify(0), 2.0, 0.0)
    assert dv.status == "error"


def test_supremum_interval_constant_function():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(sympy.sympify(3), sympy.sympify(1), -5.0, 5.0)
    assert dv.status in {"exact_and_numeric", "numeric"}
    assert abs(float(dv.numeric) - 2.0) < 1e-8
    assert max_x


def test_supremum_interval_many_maxima():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(sympy.sin(2 * sympy.pi * x), sympy.sympify(0), 0.0, 1.0)
    assert abs(float(dv.numeric) - 1.0) < 1e-5
    assert any(abs(point - 0.25) < 1e-3 or abs(point - 0.75) < 1e-3 for point in max_x)


def test_supremum_interval_single_point_domain():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(x**2, sympy.sympify(1), 2.0, 2.0)
    assert abs(float(dv.numeric) - 3.0) < 1e-8
    assert max_x
    assert all(abs(point - 2.0) < 1e-9 for point in max_x)


def test_supremum_interval_no_finite_values():
    x = sympy.Symbol("x", real=True)
    dv, max_x, _, _, _ = compute_supremum_interval(sympy.log(-x**2 - 1), sympy.sympify(0), -1.0, 1.0)
    assert dv.status == "error"
    assert max_x == []
