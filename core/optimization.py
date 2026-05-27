import numpy as np
from scipy.optimize import minimize_scalar, minimize
from typing import Callable, Tuple, Any

def find_maximum_1d(
    func: Callable[[np.ndarray], np.ndarray],
    a: float,
    b: float,
    resolution: int = 1000
) -> Tuple[float, float]:
    x_vals = np.linspace(a, b, resolution)
    y_vals = func(x_vals)
    max_idx = np.nanargmax(y_vals)
    best_x = x_vals[max_idx]
    best_y = y_vals[max_idx]
    
    def neg_func(x: float) -> float:
        val = func(np.array([x]))[0]
        if np.isnan(val):
            return np.inf
        return -val

    res = minimize_scalar(neg_func, bounds=(a, b), method='bounded')
    if res.success and -res.fun > best_y:
        best_x = res.x
        best_y = -res.fun
        
    return float(best_x), float(best_y)

def find_maximum_2d(
    func: Callable[[np.ndarray, np.ndarray], np.ndarray],
    x_bounds: Tuple[float, float],
    y_bounds: Tuple[float, float],
    resolution: int = 100
) -> Tuple[Tuple[float, float], float]:
    x_linspace = np.linspace(x_bounds[0], x_bounds[1], resolution)
    y_linspace = np.linspace(y_bounds[0], y_bounds[1], resolution)
    X, Y = np.meshgrid(x_linspace, y_linspace)
    
    Z = func(X.flatten(), Y.flatten())
    Z = Z.reshape(X.shape)
    
    max_idx = np.nanargmax(Z)
    flat_idx = np.unravel_index(max_idx, Z.shape)
    
    best_x = X[flat_idx]
    best_y = Y[flat_idx]
    best_z = Z[flat_idx]
    
    def neg_func(pt: np.ndarray) -> float:
        val = func(np.array([pt[0]]), np.array([pt[1]]))[0]
        if np.isnan(val):
            return np.inf
        return -val

    bounds = [x_bounds, y_bounds]
    res = minimize(neg_func, [best_x, best_y], bounds=bounds)
    
    if res.success and -res.fun > best_z:
        best_x = res.x[0]
        best_y = res.x[1]
        best_z = -res.fun
        
    return (float(best_x), float(best_y)), float(best_z)
