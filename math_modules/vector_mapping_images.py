from typing import Any, List, Tuple

import numpy as np
import sympy

from core.safe_eval import create_numpy_func_2d
from core.set_parser import ParsedSet, Relation2D


def sample_vector_mapping(
    phi1_expr: Any,
    phi2_expr: Any,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 50,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)

    phi1_num = create_numpy_func_2d(phi1_expr, x, y)
    phi2_num = create_numpy_func_2d(phi2_expr, x, y)

    x_vals = np.linspace(source_bounds[0][0], source_bounds[0][1], resolution)
    y_vals = np.linspace(source_bounds[1][0], source_bounds[1][1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)

    U = phi1_num(X, Y)
    V = phi2_num(X, Y)

    return X, Y, U, V


def set_mask(
    parsed_set: ParsedSet,
    x_values: np.ndarray,
    y_values: np.ndarray,
    tolerance: float = 1e-9,
) -> np.ndarray:
    try:
        return parsed_set.contains_arrays(x_values, y_values, tolerance=tolerance)
    except Exception:
        result = np.zeros_like(x_values, dtype=bool)
        rows, cols = result.shape
        for i in range(rows):
            for j in range(cols):
                result[i, j] = parsed_set.classify_numeric((x_values[i, j], y_values[i, j]), tolerance) == "true"
        return result


def sample_set_grid(
    parsed_set: ParsedSet,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 250,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_vals = np.linspace(source_bounds[0][0], source_bounds[0][1], resolution)
    y_vals = np.linspace(source_bounds[1][0], source_bounds[1][1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    width = max(abs(source_bounds[0][1] - source_bounds[0][0]), abs(source_bounds[1][1] - source_bounds[1][0]))
    tolerance = max(1e-9, width / max(1, resolution) * 0.5)
    return X, Y, set_mask(parsed_set, X, Y, tolerance=tolerance)


def sample_relation_grid(
    relation: Relation2D,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 450,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    u = sympy.Symbol("u", real=True)
    v = sympy.Symbol("v", real=True)
    diff_expr = relation.lhs - relation.rhs
    func = sympy.lambdify((x, y, u, v), diff_expr, modules=["numpy", "scipy"])

    x_vals = np.linspace(source_bounds[0][0], source_bounds[0][1], resolution)
    y_vals = np.linspace(source_bounds[1][0], source_bounds[1][1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    try:
        with np.errstate(divide="ignore", invalid="ignore", over="ignore", under="ignore"):
            Z = np.asarray(func(X, Y, X, Y), dtype=float)
        if Z.shape != X.shape:
            Z = np.broadcast_to(Z, X.shape).astype(float)
    except Exception:
        Z = np.full_like(X, np.nan, dtype=float)
    return X, Y, np.where(np.isfinite(Z), Z, np.nan)


def compute_preimage_relation_grid(
    phi1_expr: Any,
    phi2_expr: Any,
    relation: Relation2D,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 420,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    u = sympy.Symbol("u", real=True)
    v = sympy.Symbol("v", real=True)
    diff_expr = (relation.lhs - relation.rhs).subs(
        [(u, phi1_expr), (v, phi2_expr), (x, phi1_expr), (y, phi2_expr)],
        simultaneous=True,
    )
    func = create_numpy_func_2d(diff_expr, x, y)

    x_vals = np.linspace(source_bounds[0][0], source_bounds[0][1], resolution)
    y_vals = np.linspace(source_bounds[1][0], source_bounds[1][1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    return X, Y, func(X, Y)


def compute_preimage_grid(
    phi1_expr: Any,
    phi2_expr: Any,
    target_set: ParsedSet,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 150,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    X, Y, U, V = sample_vector_mapping(phi1_expr, phi2_expr, source_bounds, resolution)
    finite = np.isfinite(U) & np.isfinite(V)
    width = max(abs(source_bounds[0][1] - source_bounds[0][0]), abs(source_bounds[1][1] - source_bounds[1][0]))
    tolerance = max(1e-9, width / max(1, resolution) * 0.5)
    Z = set_mask(target_set, U, V, tolerance=tolerance)
    return X, Y, Z & finite


def compute_image_points(
    phi1_expr: Any,
    phi2_expr: Any,
    source_set: ParsedSet,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 100,
) -> Tuple[List[float], List[float]]:
    X, Y, U, V = sample_vector_mapping(phi1_expr, phi2_expr, source_bounds, resolution)
    width = max(abs(source_bounds[0][1] - source_bounds[0][0]), abs(source_bounds[1][1] - source_bounds[1][0]))
    tolerance = max(1e-9, width / max(1, resolution) * 0.5)
    mask = set_mask(source_set, X, Y, tolerance=tolerance) & np.isfinite(U) & np.isfinite(V)
    return U[mask].astype(float).tolist(), V[mask].astype(float).tolist()
