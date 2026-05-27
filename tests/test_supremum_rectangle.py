import sympy
from math_modules.supremum_rectangle import compute_supremum_rectangle

def test_supremum_rectangle():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    dv, pts, _, _, _ = compute_supremum_rectangle(x**2 + y**2, sympy.sympify(0), (-1.0, 1.0), (-1.0, 1.0))
    assert abs(float(dv.numeric) - 2.0) < 1e-2
