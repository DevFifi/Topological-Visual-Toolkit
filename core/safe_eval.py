import sympy
import numpy as np
from typing import Any, Callable

def create_numpy_func_1d(expr: Any, var: sympy.Symbol) -> Callable[[np.ndarray], np.ndarray]:
    try:
        func = sympy.lambdify(var, expr, modules=["numpy", "scipy"])
        def safe_func(x_vals: np.ndarray) -> np.ndarray:
            try:
                res = func(x_vals)
                if np.isscalar(res):
                    return np.full_like(x_vals, res, dtype=float)
                return np.asarray(res, dtype=float)
            except Exception:
                return np.full_like(x_vals, np.nan, dtype=float)
        return safe_func
    except Exception:
        def err_func(x_vals: np.ndarray) -> np.ndarray:
            return np.full_like(x_vals, np.nan, dtype=float)
        return err_func

def create_numpy_func_2d(expr: Any, var1: sympy.Symbol, var2: sympy.Symbol) -> Callable[[np.ndarray, np.ndarray], np.ndarray]:
    try:
        func = sympy.lambdify((var1, var2), expr, modules=["numpy", "scipy"])
        def safe_func(x_vals: np.ndarray, y_vals: np.ndarray) -> np.ndarray:
            try:
                res = func(x_vals, y_vals)
                if np.isscalar(res):
                    return np.full_like(x_vals, res, dtype=float)
                return np.asarray(res, dtype=float)
            except Exception:
                return np.full_like(x_vals, np.nan, dtype=float)
        return safe_func
    except Exception:
        def err_func(x_vals: np.ndarray, y_vals: np.ndarray) -> np.ndarray:
            return np.full_like(x_vals, np.nan, dtype=float)
        return err_func
