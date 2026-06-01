import sympy

from core.expression_parser import parse_expression


def test_parse_sqrt():
    res = parse_expression("sqrt(2)")
    assert res.is_valid
    assert res.expr == sympy.sqrt(2)


def test_parse_constants():
    assert parse_expression("pi").expr == sympy.pi
    assert parse_expression("\\pi").expr == sympy.pi
    assert parse_expression("e").expr == sympy.E


def test_parse_rational_and_latex_fraction():
    assert parse_expression("1/3").expr == sympy.Rational(1, 3)
    assert parse_expression("\\frac{1}{2}").expr == sympy.Rational(1, 2)


def test_parse_latex_sqrt_and_functions():
    x = sympy.Symbol("x", real=True)
    assert parse_expression("\\sqrt{x}").expr == sympy.sqrt(x)
    assert parse_expression("\\sin(pi*x)").expr == sympy.sin(sympy.pi * x)


def test_parse_multivar_and_exp_e():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    assert parse_expression("x^2 + y^2").expr == x**2 + y**2
    assert parse_expression("e^x").expr == sympy.E**x


def test_parse_nested_latex_fraction_and_sqrt():
    x = sympy.Symbol("x", real=True)
    res = parse_expression(r"\frac{1 + \sqrt{x}}{2}")
    assert res.is_valid
    assert sympy.simplify(res.expr - (1 + sympy.sqrt(x)) / 2) == 0


def test_parse_unicode_sqrt_and_math_symbols():
    x = sympy.Symbol("x", real=True)
    assert parse_expression("√(x)").expr == sympy.sqrt(x)
    assert parse_expression("2·x + 3π").expr == 2 * x + 3 * sympy.pi
    assert parse_expression(r"2 \times x").expr == 2 * x


def test_parse_latex_parentheses_and_functions():
    x = sympy.Symbol("x", real=True)
    res = parse_expression(r"\left(\sin(x)+\cos(x)\right)^2")
    assert res.is_valid
    assert sympy.simplify(res.expr - (sympy.sin(x) + sympy.cos(x)) ** 2) == 0


def test_parse_abs_bars_and_min_max():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    assert parse_expression("|x-y|").expr == sympy.Abs(x - y)
    assert parse_expression("Max(|x|, |y|)").expr == sympy.Max(sympy.Abs(x), sympy.Abs(y))


def test_parse_exp_compatibility_and_small_e_constant():
    x = sympy.Symbol("x", real=True)
    assert parse_expression("exp(x)").expr == sympy.exp(x)
    assert parse_expression("e^(1/2)").expr == sympy.sqrt(sympy.E)


def test_reject_empty_and_malformed_expressions():
    assert not parse_expression("").is_valid
    assert not parse_expression("sqrt(").is_valid
    assert not parse_expression(r"\frac{1}{").is_valid
