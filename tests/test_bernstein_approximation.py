import sympy

from math_modules.bernstein_approximation import compute_bernstein_error, compute_bernstein_polynomial


def test_bernstein_linear():
    x = sympy.Symbol("x", real=True)
    exact_b, _ = compute_bernstein_polynomial(x, 2)
    assert sympy.simplify(exact_b - x) == 0


def test_bernstein_quadratic():
    x = sympy.Symbol("x", real=True)
    exact_b, _ = compute_bernstein_polynomial(x**2, 2)
    expected = x**2 + x * (1 - x) / 2
    assert sympy.simplify(exact_b - expected) == 0


def test_bernstein_quadratic_error():
    x = sympy.Symbol("x", real=True)
    _, b_num = compute_bernstein_polynomial(x**2, 10)
    dv = compute_bernstein_error(x**2, None, b_num, 10)
    assert abs(float(dv.numeric) - 0.025) < 5e-4


def test_bernstein_large_n_runs():
    x = sympy.Symbol("x", real=True)
    _, b_num = compute_bernstein_polynomial(sympy.sin(x), 80)
    val = b_num([0.5])[0]
    assert abs(val) < 1


def test_bernstein_constant_function_is_exact():
    exact_b, b_num = compute_bernstein_polynomial(sympy.sympify(7), 12)
    assert sympy.simplify(exact_b - 7) == 0
    assert abs(float(b_num([0.25])[0]) - 7.0) < 1e-12


def test_bernstein_n_one_for_quadratic_is_linear_interpolant():
    x = sympy.Symbol("x", real=True)
    exact_b, _ = compute_bernstein_polynomial(x**2, 1)
    assert sympy.simplify(exact_b - x) == 0


def test_bernstein_error_for_linear_function_is_zero():
    x = sympy.Symbol("x", real=True)
    _, b_num = compute_bernstein_polynomial(3 * x - 1, 20)
    dv = compute_bernstein_error(3 * x - 1, None, b_num, 20)
    assert abs(float(dv.numeric)) < 1e-10


def test_bernstein_error_for_quadratic_decreases_with_n():
    x = sympy.Symbol("x", real=True)
    _, b_num_5 = compute_bernstein_polynomial(x**2, 5)
    _, b_num_30 = compute_bernstein_polynomial(x**2, 30)
    err_5 = compute_bernstein_error(x**2, None, b_num_5, 5)
    err_30 = compute_bernstein_error(x**2, None, b_num_30, 30)
    assert float(err_30.numeric) < float(err_5.numeric)
