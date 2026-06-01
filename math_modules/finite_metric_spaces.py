import re
from typing import Any, List, Optional, Tuple

import numpy as np
import sympy

from core.exact_numeric import DualValue
from core.expression_parser import normalize_expression_input, parse_expression
from core.formatting import latex_exact, simplify_exact


METRIC_DISPLAY_NAMES = {
    "Euclidean": "Euklidesowa",
    "Manhattan": "Manhattan",
    "Chebyshev": "Czebyszewa",
    "Discrete": "Dyskretna",
    "Hamming": "Hamminga",
    "Minkowski": "Minkowskiego",
    "custom": "Własna",
}

POLISH_TO_INTERNAL = {
    "Euklidesowa": "Euclidean",
    "Manhattan": "Manhattan",
    "Czebyszewa": "Chebyshev",
    "Dyskretna": "Discrete",
    "Hamminga": "Hamming",
    "Minkowskiego": "Minkowski",
    "Własna": "custom",
}


def normalize_metric_name(metric_name: str) -> str:
    return POLISH_TO_INTERNAL.get(metric_name, metric_name)


def metric_display_name(metric_name: str) -> str:
    return METRIC_DISPLAY_NAMES.get(normalize_metric_name(metric_name), metric_name)


def metric_symbol_latex(metric_name: str, custom_formula: str = "") -> str:
    metric = normalize_metric_name(metric_name)
    if metric == "Euclidean":
        return "d_{2}"
    if metric == "Manhattan":
        return "d_{1}"
    if metric == "Chebyshev":
        return "d_{\\infty}"
    if metric == "Discrete":
        return "\\delta"
    if metric == "Hamming":
        return "d_{H}"
    if metric == "Minkowski":
        p_res = parse_expression(custom_formula or "p")
        p_latex = sympy.latex(p_res.expr) if p_res.is_valid else "p"
        return f"d_{{{p_latex}}}"
    if metric == "custom":
        return "\\varphi"
    return "d"


def _replace_placeholders(expr: str, index: int) -> str:
    expr = re.sub(r"\bxi\b", f"x{index}", expr)
    expr = re.sub(r"\byi\b", f"y{index}", expr)
    return expr


def expand_sum_macro(formula_str: str, dim: int) -> str:
    if "SUM(" not in formula_str:
        return formula_str

    result = []
    i = 0
    while i < len(formula_str):
        if formula_str.startswith("SUM(", i):
            start = i + 4
            depth = 1
            j = start
            while j < len(formula_str) and depth > 0:
                if formula_str[j] == "(":
                    depth += 1
                elif formula_str[j] == ")":
                    depth -= 1
                j += 1
            if depth == 0:
                inner = formula_str[start:j - 1]
                terms = [_replace_placeholders(inner, k) for k in range(1, dim + 1)]
                result.append("(" + " + ".join(f"({term})" for term in terms) + ")")
                i = j
                continue
        result.append(formula_str[i])
        i += 1
    return "".join(result)


def _get_distance_formula(metric_name: str, custom_formula: str, dim: int) -> Tuple[Optional[Any], str]:
    metric = normalize_metric_name(metric_name)
    if dim <= 0:
        return None, "error"

    if metric == "custom":
        if not custom_formula.strip():
            return None, "error"
        formula_text = expand_sum_macro(normalize_expression_input(custom_formula), dim)
        formula_text = _replace_placeholders(formula_text, 1)
        res = parse_expression(formula_text)
        return (res.expr, "exact_and_numeric") if res.is_valid else (None, "error")

    x_vars = [sympy.Symbol(f"x{i + 1}", real=True) for i in range(dim)]
    y_vars = [sympy.Symbol(f"y{i + 1}", real=True) for i in range(dim)]

    if metric == "Euclidean":
        return sympy.sqrt(sum((x - y) ** 2 for x, y in zip(x_vars, y_vars))), "exact_and_numeric"
    if metric == "Manhattan":
        return sum(sympy.Abs(x - y) for x, y in zip(x_vars, y_vars)), "exact_and_numeric"
    if metric == "Chebyshev":
        return sympy.Max(*[sympy.Abs(x - y) for x, y in zip(x_vars, y_vars)]), "exact_and_numeric"
    if metric == "Discrete":
        return sympy.Piecewise(
            (0, sympy.And(*[sympy.Eq(x, y) for x, y in zip(x_vars, y_vars)])),
            (1, True),
        ), "exact_and_numeric"
    if metric == "Hamming":
        return sum(sympy.Piecewise((0, sympy.Eq(x, y)), (1, True)) for x, y in zip(x_vars, y_vars)), "exact_and_numeric"
    if metric == "Minkowski":
        p_res = parse_expression(custom_formula)
        if not p_res.is_valid:
            return None, "error"
        try:
            p_numeric = float(p_res.expr.evalf())
        except Exception:
            return None, "error"
        if not np.isfinite(p_numeric) or p_numeric <= 0:
            return None, "error"
        base_sum = sum(sympy.Abs(x - y) ** p_res.expr for x, y in zip(x_vars, y_vars))
        if p_numeric >= 1:
            return base_sum ** (1 / p_res.expr), "exact_and_numeric"
        return base_sum, "exact_and_numeric"

    return None, "error"


def metric_formula_latex(metric_name: str, custom_formula: str, dim: int) -> Optional[str]:
    formula, status = _get_distance_formula(metric_name, custom_formula, dim)
    if status == "error" or formula is None:
        return None
    return f"{metric_symbol_latex(metric_name, custom_formula)}(x,y) = {sympy.latex(formula)}"


def compute_distance(p1: Tuple[Any, ...], p2: Tuple[Any, ...], formula: Any, metric_name: str) -> DualValue:
    metric = normalize_metric_name(metric_name)
    if len(p1) != len(p2):
        return DualValue(status="error", notes=["Punkty mają różne wymiary."])
    if formula is None:
        return DualValue(status="error", notes=["Niepoprawna metryka albo jej parametr."])

    if metric == "Discrete":
        try:
            is_same = all(sympy.simplify(c1 - c2) == 0 for c1, c2 in zip(p1, p2))
            val = 0 if is_same else 1
            return DualValue(exact=str(val), exact_latex=str(val), numeric=str(val), status="exact_and_numeric")
        except Exception:
            return DualValue(status="error", notes=["Nie udało się porównać punktów."])

    subs = {}
    for i, (c1, c2) in enumerate(zip(p1, p2), start=1):
        subs[sympy.Symbol(f"x{i}", real=True)] = c1
        subs[sympy.Symbol(f"y{i}", real=True)] = c2

    try:
        exact_val = simplify_exact(formula.subs(subs))
        numeric_val = float(exact_val.evalf())
        if not np.isfinite(numeric_val):
            return DualValue(status="error", notes=["Wynik nie jest skończoną liczbą rzeczywistą."])
        return DualValue(
            exact=str(exact_val),
            exact_latex=latex_exact(exact_val),
            numeric=str(numeric_val),
            status="exact_and_numeric",
        )
    except Exception:
        return DualValue(status="error", notes=["Nie udało się obliczyć odległości."])


def _same_dimension(points: List[Tuple[Any, ...]]) -> bool:
    return bool(points) and all(len(p) == len(points[0]) for p in points)


def compute_distance_matrix(points: List[Tuple[Any, ...]], metric_name: str, custom_formula: str = "") -> List[List[DualValue]]:
    metric = normalize_metric_name(metric_name)
    if not _same_dimension(points):
        return []

    dim = len(points[0])
    formula, status = _get_distance_formula(metric, custom_formula, dim)
    if status == "error":
        return [[DualValue(status="error", notes=["Niepoprawna metryka."]) for _ in points] for _ in points]

    n = len(points)
    matrix = [[DualValue() for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = DualValue(exact="0", exact_latex="0", numeric="0.0", status="exact_and_numeric")
            elif i < j:
                dv = compute_distance(points[i], points[j], formula, metric)
                matrix[i][j] = dv
                matrix[j][i] = dv

    return matrix


def _points_to_float_array(points: List[Tuple[Any, ...]]) -> Optional[np.ndarray]:
    try:
        arr = np.asarray(
            [[float(sympy.N(coord)) for coord in point] for point in points],
            dtype=float,
        )
        if arr.ndim != 2 or not np.all(np.isfinite(arr)):
            return None
        return arr
    except Exception:
        return None


def _minkowski_p_value(custom_formula: str) -> Optional[float]:
    p_res = parse_expression(custom_formula or "2")
    if not p_res.is_valid:
        return None
    try:
        p_val = float(p_res.expr.evalf())
    except Exception:
        return None
    return p_val if np.isfinite(p_val) and p_val > 0 else None


def _numeric_distance_block(
    a_block: np.ndarray,
    b_block: np.ndarray,
    metric: str,
    custom_formula: str,
) -> Optional[np.ndarray]:
    diff = np.abs(a_block[:, None, :] - b_block[None, :, :])
    tol = 1e-12

    if metric == "Discrete":
        return np.where(np.all(diff <= tol, axis=2), 0.0, 1.0)
    if metric == "Hamming":
        return np.sum(diff > tol, axis=2).astype(float)
    if metric == "Manhattan":
        return np.sum(diff, axis=2)
    if metric == "Euclidean":
        return np.sqrt(np.sum(diff * diff, axis=2))
    if metric == "Chebyshev":
        return np.max(diff, axis=2)
    if metric == "Minkowski":
        p_val = _minkowski_p_value(custom_formula)
        if p_val is None:
            return None
        summed = np.sum(diff ** p_val, axis=2)
        return summed ** (1.0 / p_val) if p_val >= 1 else summed

    return None


def _numeric_pairwise_extreme(
    left: List[Tuple[Any, ...]],
    right: List[Tuple[Any, ...]],
    metric_name: str,
    custom_formula: str,
    *,
    find_minimum: bool,
    block_size: int = 160,
) -> Tuple[DualValue, Tuple[int, int]]:
    metric = normalize_metric_name(metric_name)
    left_arr = _points_to_float_array(left)
    right_arr = _points_to_float_array(right)
    if left_arr is None or right_arr is None:
        return DualValue(status="error", notes=["Duzy zbior zawiera wspolrzedne, ktorych nie da sie bezpiecznie policzyc numerycznie."]), (-1, -1)
    if left_arr.shape[1] != right_arr.shape[1]:
        return DualValue(status="error", notes=["Zbiory maja rozne wymiary punktow."]), (-1, -1)

    best_value = np.inf if find_minimum else -np.inf
    best_pair = (-1, -1)
    for i0 in range(0, left_arr.shape[0], block_size):
        a_block = left_arr[i0:i0 + block_size]
        for j0 in range(0, right_arr.shape[0], block_size):
            b_block = right_arr[j0:j0 + block_size]
            distances = _numeric_distance_block(a_block, b_block, metric, custom_formula)
            if distances is None:
                return DualValue(status="error", notes=["Dla duzych zbiorow szybka sciezka obsluguje metryki standardowe, bez metryki wlasnej."]), (-1, -1)
            finite = np.isfinite(distances)
            if not finite.any():
                continue
            masked = np.where(finite, distances, np.inf if find_minimum else -np.inf)
            local_flat = int(np.argmin(masked) if find_minimum else np.argmax(masked))
            local_value = float(masked.ravel()[local_flat])
            improves = local_value < best_value if find_minimum else local_value > best_value
            if improves:
                local_i, local_j = np.unravel_index(local_flat, masked.shape)
                best_value = local_value
                best_pair = (i0 + int(local_i), j0 + int(local_j))

    if best_pair == (-1, -1) or not np.isfinite(best_value):
        return DualValue(status="error", notes=["Nie znaleziono skonczonej odleglosci."]), (-1, -1)

    action = "minimum" if find_minimum else "maksimum"
    return DualValue(
        numeric=f"{best_value:.15g}",
        status="numeric",
        method=f"Numeryczne {action} blokami dla {len(left)} x {len(right)} par w R^{left_arr.shape[1]}.",
    ), best_pair


def _should_use_numeric_pairwise(points_count: int, other_count: int, dim: int, metric: str) -> bool:
    if metric == "custom":
        return False
    pair_count = points_count * other_count
    return dim > 20 or pair_count > 8000


def compute_diam(points: List[Tuple[Any, ...]], metric_name: str, custom_formula: str = "") -> Tuple[DualValue, Tuple[int, int]]:
    metric = normalize_metric_name(metric_name)
    if _same_dimension(points) and _should_use_numeric_pairwise(len(points), len(points), len(points[0]), metric):
        return _numeric_pairwise_extreme(points, points, metric, custom_formula, find_minimum=False)

    matrix = compute_distance_matrix(points, metric, custom_formula)
    if not matrix:
        return DualValue(status="error", notes=["Zbiór jest pusty albo punkty mają różne wymiary."]), (-1, -1)

    max_val = -np.inf
    best_pair = (0, 0)
    best_dv = DualValue(exact="0", exact_latex="0", numeric="0.0", status="exact_and_numeric")

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dv = matrix[i][j]
            try:
                val = float(dv.numeric) if dv.numeric is not None else np.nan
            except Exception:
                val = np.nan
            if np.isfinite(val) and val > max_val:
                max_val = val
                best_pair = (i, j)
                best_dv = dv

    return best_dv, best_pair


def compute_dist_sets(
    E: List[Tuple[Any, ...]],
    F: List[Tuple[Any, ...]],
    metric_name: str,
    custom_formula: str = "",
) -> Tuple[DualValue, Tuple[int, int]]:
    metric = normalize_metric_name(metric_name)
    if not _same_dimension(E) or not _same_dimension(F):
        return DualValue(status="error", notes=["Zbiory są puste albo mają niespójne wymiary."]), (-1, -1)
    if len(E[0]) != len(F[0]):
        return DualValue(status="error", notes=["Zbiory E i F mają różne wymiary punktów."]), (-1, -1)

    dim = len(E[0])
    if _should_use_numeric_pairwise(len(E), len(F), dim, metric):
        return _numeric_pairwise_extreme(E, F, metric, custom_formula, find_minimum=True)

    formula, status = _get_distance_formula(metric, custom_formula, dim)
    if status == "error":
        return DualValue(status="error", notes=["Niepoprawna metryka."]), (-1, -1)

    min_val = np.inf
    best_pair = (-1, -1)
    best_dv = DualValue(status="error", notes=["Nie znaleziono poprawnej odległości."])

    for i, p1 in enumerate(E):
        for j, p2 in enumerate(F):
            dv = compute_distance(p1, p2, formula, metric)
            try:
                val = float(dv.numeric) if dv.numeric is not None else np.nan
            except Exception:
                val = np.nan
            if np.isfinite(val) and val < min_val:
                min_val = val
                best_pair = (i, j)
                best_dv = dv

    return best_dv, best_pair
