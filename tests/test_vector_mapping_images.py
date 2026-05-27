import sympy
from core.set_parser import parse_set_2d
from math_modules.vector_mapping_images import compute_image_points

def test_vector_mapping():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    c_set = parse_set_2d("[-1, 1]x[-1, 1]")
    u, v = compute_image_points(x, y, c_set, ((-1.0, 1.0), (-1.0, 1.0)), 10)
    assert len(u) > 0
    assert min(u) >= -1.0
    assert max(u) <= 1.0
