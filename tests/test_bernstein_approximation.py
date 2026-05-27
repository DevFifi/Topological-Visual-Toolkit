import sympy
from math_modules.bernstein_approximation import compute_bernstein_polynomial

def test_bernstein_linear():
    x = sympy.Symbol("x", real=True)
    exact_b, _ = compute_bernstein_polynomial(x, 2)
    assert sympy.simplify(exact_b - x) == 0

def test_bernstein_quadratic():
    x = sympy.Symbol("x", real=True)
    exact_b, _ = compute_bernstein_polynomial(x**2, 2)
    expected = x**2 + x*(1-x)/2
    assert sympy.simplify(exact_b - expected) == 0
