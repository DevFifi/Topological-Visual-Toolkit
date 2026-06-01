from typing import Any, Callable, Tuple

import numpy as np
import scipy.special as sp
import sympy

from core.exact_numeric import DualValue
from core.optimization import find_maximum_1d
from core.safe_eval import create_numpy_func_1d


def compute_bernstein_polynomial(f_expr: Any, n: int) -> Tuple[Any, Callable]:
    x = sympy.Symbol("x", real=True)
    n = int(n)
    if n < 1:
        raise ValueError("Stopień n musi być dodatni.")

    exact_b_n = None
    if n <= 12:
        try:
            terms = []
            for k in range(n + 1):
                value = f_expr.subs(x, sympy.Rational(k, n))
                terms.append(sympy.binomial(n, k) * (x ** k) * ((1 - x) ** (n - k)) * value)
            candidate = sympy.expand(sum(terms))
            if sympy.count_ops(candidate) <= 350:
                exact_b_n = candidate
        except Exception:
            exact_b_n = None

    f_num = create_numpy_func_1d(f_expr, x)
    sample_values = np.array([f_num(np.array([k / n], dtype=float))[0] for k in range(n + 1)], dtype=float)

    def b_num(x_vals: np.ndarray) -> np.ndarray:
        vals = np.asarray(x_vals, dtype=float)
        result = np.zeros_like(vals, dtype=float)
        inside = (vals >= 0.0) & (vals <= 1.0)
        result[~inside] = np.nan
        if not np.any(inside):
            return result

        x_inside = vals[inside]
        accum = np.zeros_like(x_inside, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore", under="ignore"):
            log_x = np.log(x_inside)
            log_1_minus_x = np.log1p(-x_inside)
            for k, f_val in enumerate(sample_values):
                if not np.isfinite(f_val):
                    continue
                log_basis = (
                    sp.gammaln(n + 1)
                    - sp.gammaln(k + 1)
                    - sp.gammaln(n - k + 1)
                    + k * log_x
                    + (n - k) * log_1_minus_x
                )
                basis = np.exp(log_basis)
                basis = np.where(x_inside == 0.0, 1.0 if k == 0 else 0.0, basis)
                basis = np.where(x_inside == 1.0, 1.0 if k == n else 0.0, basis)
                accum += basis * f_val
        result[inside] = np.where(np.isfinite(accum), accum, np.nan)
        return result

    return exact_b_n, b_num


def compute_bernstein_error(
    f_expr: Any,
    exact_b_n: Any,
    b_num: Callable,
    n: int,
    precision: int = 50,
) -> DualValue:
    x = sympy.Symbol("x", real=True)
    f_num = create_numpy_func_1d(f_expr, x)

    def err_num(vals: np.ndarray) -> np.ndarray:
        return np.abs(f_num(vals) - b_num(vals))

    resolution = min(20000, max(3000, 800 + int(n) * 60))
    best_x, max_err = find_maximum_1d(err_num, 0.0, 1.0, resolution)
    if not np.isfinite(max_err):
        return DualValue(status="error", notes=["Nie udało się policzyć błędu na [0, 1]."])

    return DualValue(
        numeric=str(max_err),
        status="numeric",
        method=f"Numeryczne maksimum błędu na [0, 1] (siatka {resolution} pkt + doszukiwanie)",
        precision_digits=precision,
        notes=[f"Największy znaleziony błąd występuje w pobliżu x = {best_x:.6g}."],
    )
