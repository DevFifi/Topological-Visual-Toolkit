from typing import Callable, Tuple

import numpy as np
from scipy.optimize import minimize, minimize_scalar


def _finite_values(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return np.where(np.isfinite(arr), arr, np.nan)


def find_maximum_1d(
    func: Callable[[np.ndarray], np.ndarray],
    a: float,
    b: float,
    resolution: int = 1000,
    local_refinements: int = 16,
) -> Tuple[float, float]:
    if not np.isfinite(a) or not np.isfinite(b) or a > b:
        return float("nan"), float("nan")
    if a == b:
        val = _finite_values(func(np.array([a], dtype=float)))[0]
        return float(a), float(val)

    resolution = max(3, int(resolution))
    x_vals = np.linspace(a, b, resolution)
    y_vals = _finite_values(func(x_vals))
    valid = np.isfinite(y_vals)
    if not np.any(valid):
        return float("nan"), float("nan")

    valid_indices = np.flatnonzero(valid)
    best_idx = valid_indices[np.nanargmax(y_vals[valid])]
    best_x = float(x_vals[best_idx])
    best_y = float(y_vals[best_idx])

    candidate_indices = {int(best_idx), 0, resolution - 1}
    for idx in range(1, resolution - 1):
        if not valid[idx]:
            continue
        left = y_vals[idx - 1] if valid[idx - 1] else -np.inf
        right = y_vals[idx + 1] if valid[idx + 1] else -np.inf
        if y_vals[idx] >= left and y_vals[idx] >= right:
            candidate_indices.add(idx)

    ranked = sorted(candidate_indices, key=lambda i: y_vals[i] if valid[i] else -np.inf, reverse=True)
    ranked = ranked[:max(1, local_refinements)]

    def neg_func(x: float) -> float:
        val = _finite_values(func(np.array([x], dtype=float)))[0]
        return np.inf if not np.isfinite(val) else -float(val)

    for idx in ranked:
        lo = x_vals[max(0, idx - 1)]
        hi = x_vals[min(resolution - 1, idx + 1)]
        if lo == hi:
            continue
        try:
            res = minimize_scalar(neg_func, bounds=(float(lo), float(hi)), method="bounded")
            if res.success and np.isfinite(res.fun) and -res.fun > best_y:
                best_x = float(res.x)
                best_y = float(-res.fun)
        except Exception:
            continue

    return best_x, best_y


def find_maximum_2d(
    func: Callable[[np.ndarray, np.ndarray], np.ndarray],
    x_bounds: Tuple[float, float],
    y_bounds: Tuple[float, float],
    resolution: int = 100,
    local_refinements: int = 12,
) -> Tuple[Tuple[float, float], float]:
    xa, xb = x_bounds
    ya, yb = y_bounds
    if not all(np.isfinite(v) for v in (xa, xb, ya, yb)) or xa > xb or ya > yb:
        return (float("nan"), float("nan")), float("nan")

    resolution = max(3, int(resolution))
    x_linspace = np.linspace(xa, xb, resolution)
    y_linspace = np.linspace(ya, yb, resolution)
    X, Y = np.meshgrid(x_linspace, y_linspace)

    Z = _finite_values(func(X.flatten(), Y.flatten())).reshape(X.shape)
    valid = np.isfinite(Z)
    if not np.any(valid):
        return (float("nan"), float("nan")), float("nan")

    flat_valid = np.flatnonzero(valid.ravel())
    top_count = min(local_refinements, len(flat_valid))
    top_flat = flat_valid[np.argsort(Z.ravel()[flat_valid])[-top_count:]][::-1]

    best_flat = top_flat[0]
    best_row, best_col = np.unravel_index(best_flat, Z.shape)
    best_x = float(X[best_row, best_col])
    best_y = float(Y[best_row, best_col])
    best_z = float(Z[best_row, best_col])

    def neg_func(pt: np.ndarray) -> float:
        val = _finite_values(func(np.array([pt[0]], dtype=float), np.array([pt[1]], dtype=float)))[0]
        return np.inf if not np.isfinite(val) else -float(val)

    starts = [(best_x, best_y)]
    for flat_idx in top_flat:
        row, col = np.unravel_index(flat_idx, Z.shape)
        starts.append((float(X[row, col]), float(Y[row, col])))
    starts.extend([(xa, ya), (xa, yb), (xb, ya), (xb, yb)])

    for start in starts:
        try:
            res = minimize(
                neg_func,
                np.array(start, dtype=float),
                bounds=[(xa, xb), (ya, yb)],
                method="L-BFGS-B",
            )
            if res.success and np.isfinite(res.fun) and -res.fun > best_z:
                best_x = float(res.x[0])
                best_y = float(res.x[1])
                best_z = float(-res.fun)
        except Exception:
            continue

    return (best_x, best_y), best_z
