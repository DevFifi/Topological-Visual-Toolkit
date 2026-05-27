import sympy
import numpy as np
from typing import Any, Tuple, List
from core.set_parser import ParsedSet
from core.safe_eval import create_numpy_func_2d

def sample_vector_mapping(
    phi1_expr: Any,
    phi2_expr: Any,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 50
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

def compute_preimage_grid(
    phi1_expr: Any,
    phi2_expr: Any,
    target_set: ParsedSet,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 150
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    X, Y, U, V = sample_vector_mapping(phi1_expr, phi2_expr, source_bounds, resolution)
    
    Z = np.zeros_like(X, dtype=bool)
    rows, cols = X.shape
    for i in range(rows):
        for j in range(cols):
            Z[i, j] = target_set.contains_numeric((U[i, j], V[i, j]))
            
    return X, Y, Z

def compute_image_points(
    phi1_expr: Any,
    phi2_expr: Any,
    source_set: ParsedSet,
    source_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    resolution: int = 100
) -> Tuple[List[float], List[float]]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    
    phi1_num = create_numpy_func_2d(phi1_expr, x, y)
    phi2_num = create_numpy_func_2d(phi2_expr, x, y)
    
    x_vals = np.linspace(source_bounds[0][0], source_bounds[0][1], resolution)
    y_vals = np.linspace(source_bounds[1][0], source_bounds[1][1], resolution)
    
    u_list = []
    v_list = []
    
    for px in x_vals:
        for py in y_vals:
            if source_set.contains_numeric((px, py)):
                u = phi1_num(np.array([px]), np.array([py]))[0]
                v = phi2_num(np.array([px]), np.array([py]))[0]
                if not np.isnan(u) and not np.isnan(v):
                    u_list.append(float(u))
                    v_list.append(float(v))
                    
    return u_list, v_list
