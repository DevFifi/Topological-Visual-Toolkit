import sympy

from math_modules.supremum_rectangle import compute_supremum_rectangle


def test_supremum_rectangle_corner_maximum():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    dv, pts, _, _, _ = compute_supremum_rectangle(x**2 + y**2, sympy.sympify(0), (-1.0, 1.0), (-1.0, 1.0))
    assert abs(float(dv.numeric) - 2.0) < 1e-2
    assert pts


def test_supremum_rectangle_invalid_bounds():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    dv, _, _, _, _ = compute_supremum_rectangle(x + y, sympy.sympify(0), (1.0, -1.0), (-1.0, 1.0))
    assert dv.status == "error"


def test_supremum_rectangle_interior_maximum():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    dv, pts, _, _, _ = compute_supremum_rectangle(1 - x**2 - y**2, sympy.sympify(0), (-0.5, 0.5), (-0.5, 0.5), resolution=80)
    assert abs(float(dv.numeric) - 1.0) < 1e-3
    assert any(abs(px) < 1e-2 and abs(py) < 1e-2 for px, py in pts)


def test_supremum_rectangle_edge_maximum():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    dv, pts, _, _, _ = compute_supremum_rectangle(x, sympy.sympify(0), (-2.0, 1.0), (-1.0, 1.0), resolution=60)
    assert abs(float(dv.numeric) - 2.0) < 1e-4
    assert any(abs(px + 2.0) < 1e-3 for px, _ in pts)


def test_supremum_rectangle_constant_function():
    dv, pts, _, _, _ = compute_supremum_rectangle(sympy.sympify(5), sympy.sympify(2), (-1.0, 1.0), (-1.0, 1.0), resolution=30)
    assert abs(float(dv.numeric) - 3.0) < 1e-9
    assert pts


def test_supremum_rectangle_no_finite_values():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    dv, pts, _, _, _ = compute_supremum_rectangle(sympy.log(-x**2 - y**2 - 1), sympy.sympify(0), (-1.0, 1.0), (-1.0, 1.0))
    assert dv.status == "error"
    assert pts == []
