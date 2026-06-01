from typing import Any, List, Tuple

import numpy as np
import sympy

from core.exact_numeric import DualValue
from core.formatting import latex_exact, simplify_exact
from core.optimization import find_maximum_1d
from core.safe_eval import create_numpy_func_1d


def compute_supremum_interval(
    f_expr: Any,
    g_expr: Any,
    a: float,
    b: float,
    precision: int = 50,
    resolution: int = 3000,
) -> Tuple[DualValue, List[float], Any, Any, Any]:
    x = sympy.Symbol("x", real=True)
    f_num = create_numpy_func_1d(f_expr, x)
    g_num = create_numpy_func_1d(g_expr, x)

    def h_num(vals: np.ndarray) -> np.ndarray:
        return np.abs(f_num(vals) - g_num(vals))

    if not np.isfinite(a) or not np.isfinite(b) or a > b:
        return (
            DualValue(status="error", notes=["Przedział musi mieć skończone końce i spełniać a <= b."]),
            [],
            f_num,
            g_num,
            h_num,
        )

    diff_expr = sympy.simplify(f_expr - g_expr)
    h_sq = sympy.simplify(diff_expr ** 2)
    h_abs = sympy.Abs(diff_expr)

    best_x, best_y = find_maximum_1d(h_num, a, b, resolution)
    if not np.isfinite(best_y):
        return (
            DualValue(status="error", notes=["Nie znaleziono skończonych wartości funkcji na podanym przedziale."]),
            [],
            f_num,
            g_num,
            h_num,
        )

    exact_val = None
    best_x_list = [best_x]
    status = "numeric"
    method = "Numerycznie: siatka + lokalne doszukiwanie maksimów"

    try:
        candidates = [sympy.sympify(a), sympy.sympify(b)]
        if sympy.count_ops(h_sq) <= 120:
            deriv = sympy.diff(h_sq, x)
            roots = sympy.solve(deriv, x)
            for root in roots:
                try:
                    root_f = float(root.evalf())
                    if a <= root_f <= b:
                        candidates.append(root)
                except Exception:
                    continue

        max_exact = None
        max_float = -np.inf
        exact_points = []
        for candidate in candidates:
            try:
                val = sympy.simplify(h_abs.subs(x, candidate))
                val_f = float(val.evalf())
                if not np.isfinite(val_f):
                    continue
                if val_f > max_float + 10 ** (-min(8, precision // 2)):
                    max_float = val_f
                    max_exact = val
                    exact_points = [candidate]
                elif abs(val_f - max_float) <= 1e-8:
                    exact_points.append(candidate)
            except Exception:
                continue

        if max_exact is not None and abs(max_float - best_y) <= max(1e-6, abs(best_y) * 1e-6):
            exact_val = simplify_exact(max_exact)
            best_y = max_float
            best_x_list = [float(point.evalf()) for point in exact_points]
            status = "exact_and_numeric"
            method = "Dokładnie: punkty krytyczne i końce przedziału"
    except Exception:
        pass

    dv = DualValue(
        exact=str(exact_val) if exact_val is not None else None,
        exact_latex=latex_exact(exact_val) if exact_val is not None else None,
        numeric=str(best_y),
        status=status,
        method=method,
        precision_digits=precision,
    )
    if status == "numeric":
        dv.notes.append("Wynik jest przybliżeniem numerycznym; gęstość siatki wpływa na dokładność.")

    return dv, best_x_list, f_num, g_num, h_num
