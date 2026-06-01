import sympy
import numpy as np

from core.set_parser import parse_set_1d
from math_modules.scalar_preimage import compute_scalar_preimage_membership
from ui.scalar_preimage_page import _mask_values_1d


def test_scalar_preimage_interval():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    f = x**2 + y**2
    a_set = parse_set_1d("[0, 1]")

    status1, _ = compute_scalar_preimage_membership(f, a_set, (0.0, 0.0))
    assert status1 == "true"

    status2, _ = compute_scalar_preimage_membership(f, a_set, (2.0, 0.0))
    assert status2 == "false"


def test_scalar_preimage_open_boundary():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    a_set = parse_set_1d("(0, 1)")
    status, _ = compute_scalar_preimage_membership(x**2 + y**2, a_set, (1.0, 0.0))
    assert status in {"boundary", "false"}


def test_scalar_preimage_finite_set_membership():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    a_set = parse_set_1d("{0, 2}")
    status_true, dv_true = compute_scalar_preimage_membership(x + y, a_set, (1.0, 1.0))
    status_false, _ = compute_scalar_preimage_membership(x + y, a_set, (1.0, 2.0))
    assert status_true == "true"
    assert float(dv_true.numeric) == 2.0
    assert status_false == "false"


def test_scalar_preimage_exact_latex_for_symbolic_value():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    a_set = parse_set_1d("[0, 10]")
    status, dv = compute_scalar_preimage_membership(sympy.exp(x) + y, a_set, (sympy.Integer(1), sympy.Integer(0)))
    assert status == "true"
    assert dv.exact_latex == "e"


def test_scalar_preimage_nonfinite_value_returns_unknown():
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    a_set = parse_set_1d("[0, 1]")
    status, dv = compute_scalar_preimage_membership(1 / (x - y), a_set, (0.0, 0.0))
    assert status == "unknown"
    assert dv.status == "error"


def test_mask_values_1d_for_interval_and_finite_set():
    values = np.array([[-0.1, 0.0, 0.5, 1.0, 1.1]])
    closed = parse_set_1d("[0, 1]")
    open_set = parse_set_1d("(0, 1)")
    finite = parse_set_1d("{0, 1}")
    assert _mask_values_1d(closed, values, 1e-9).tolist() == [[False, True, True, True, False]]
    assert _mask_values_1d(open_set, values, 1e-9).tolist() == [[False, False, True, False, False]]
    assert _mask_values_1d(finite, values, 1e-9).tolist() == [[False, True, False, True, False]]
