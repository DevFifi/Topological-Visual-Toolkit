import sympy
from core.set_parser import parse_set_1d
from math_modules.scalar_preimage import compute_scalar_preimage_membership

def test_scalar_preimage():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    f = x**2 + y**2
    a_set = parse_set_1d("[0, 1]")
    
    # Inside
    status1, _ = compute_scalar_preimage_membership(f, a_set, (0.0, 0.0))
    assert status1 == "true"
    
    # Outside
    status2, _ = compute_scalar_preimage_membership(f, a_set, (2.0, 0.0))
    assert status2 == "false"
