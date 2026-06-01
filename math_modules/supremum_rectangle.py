from typing import Any, List, Tuple

import numpy as np
import sympy

from core.exact_numeric import DualValue
from core.optimization import find_maximum_1d, find_maximum_2d
from core.safe_eval import create_numpy_func_2d


def compute_supremum_rectangle(
    f_expr: Any,
    g_expr: Any,
    x_bounds: Tuple[float, float],
    y_bounds: Tuple[float, float],
    precision: int = 50,
    resolution: int = 150,
) -> Tuple[DualValue, List[Tuple[float, float]], Any, Any, Any]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)

    f_num = create_numpy_func_2d(f_expr, x, y)
    g_num = create_numpy_func_2d(g_expr, x, y)

    def h_num(x_vals: np.ndarray, y_vals: np.ndarray) -> np.ndarray:
        return np.abs(f_num(x_vals, y_vals) - g_num(x_vals, y_vals))

    xa, xb = x_bounds
    ya, yb = y_bounds
    if not all(np.isfinite(v) for v in (xa, xb, ya, yb)) or xa > xb or ya > yb:
        return (
            DualValue(status="error", notes=["Prostokąt musi mieć skończone granice oraz a <= b i c <= d."]),
            [],
            f_num,
            g_num,
            h_num,
        )

    best_pt, best_val = find_maximum_2d(h_num, x_bounds, y_bounds, resolution)
    candidates: List[Tuple[Tuple[float, float], float]] = []
    if np.isfinite(best_val):
        candidates.append((best_pt, best_val))

    def add_edge_max(edge_func, point_builder, lo: float, hi: float) -> None:
        edge_x, edge_val = find_maximum_1d(edge_func, lo, hi, max(300, resolution * 4))
        if np.isfinite(edge_val):
            candidates.append((point_builder(edge_x), edge_val))

    add_edge_max(lambda vals: h_num(np.full_like(vals, xa), vals), lambda t: (xa, t), ya, yb)
    add_edge_max(lambda vals: h_num(np.full_like(vals, xb), vals), lambda t: (xb, t), ya, yb)
    add_edge_max(lambda vals: h_num(vals, np.full_like(vals, ya)), lambda t: (t, ya), xa, xb)
    add_edge_max(lambda vals: h_num(vals, np.full_like(vals, yb)), lambda t: (t, yb), xa, xb)

    for pt in ((xa, ya), (xa, yb), (xb, ya), (xb, yb)):
        val = h_num(np.array([pt[0]], dtype=float), np.array([pt[1]], dtype=float))[0]
        if np.isfinite(val):
            candidates.append((pt, float(val)))

    if not candidates:
        return (
            DualValue(status="error", notes=["Nie znaleziono skończonych wartości funkcji na prostokącie."]),
            [],
            f_num,
            g_num,
            h_num,
        )

    best_pt, best_val = max(candidates, key=lambda item: item[1])
    maximizers = [best_pt]
    for pt, val in candidates:
        if abs(val - best_val) <= max(1e-8, abs(best_val) * 1e-8):
            if all(np.hypot(pt[0] - seen[0], pt[1] - seen[1]) > 1e-5 for seen in maximizers):
                maximizers.append(pt)

    dv = DualValue(
        exact=None,
        numeric=str(best_val),
        status="numeric",
        method="Numerycznie: siatka 2D, wielostartowe doszukiwanie, brzegi i narożniki",
        precision_digits=precision,
        notes=["Na prostokącie wynik jest przybliżony; dokładność zależy od rozdzielczości i kształtu funkcji."],
    )

    return dv, maximizers, f_num, g_num, h_num
