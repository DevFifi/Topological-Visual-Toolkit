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
    assert abs(max_x[0] - float((sympy.pi/2).evalf())) < 1e-3
