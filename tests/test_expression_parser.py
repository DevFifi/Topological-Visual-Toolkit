import sympy
from core.expression_parser import parse_expression

def test_parse_sqrt():
    res = parse_expression("sqrt(2)")
    assert res.is_valid
    assert res.expr == sympy.sqrt(2)

def test_parse_constants():
    res = parse_expression("pi")
    assert res.is_valid
    assert res.expr == sympy.pi
    
    res = parse_expression("E")
    assert res.is_valid
    assert res.expr == sympy.E

def test_parse_rational():
    res = parse_expression("1/3")
    assert res.is_valid
    assert res.expr == sympy.Rational(1, 3)

def test_parse_functions():
    res = parse_expression("sin(pi*x)")
    assert res.is_valid
    x = sympy.Symbol("x", real=True)
    assert res.expr == sympy.sin(sympy.pi * x)

def test_parse_multivar():
    res = parse_expression("x^2 + y^2")
    assert res.is_valid
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    assert res.expr == x**2 + y**2
