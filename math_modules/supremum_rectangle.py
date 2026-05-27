import sympy
import numpy as np
from typing import Tuple, List, Any
from core.exact_numeric import DualValue
from core.optimization import find_maximum_2d
from core.safe_eval import create_numpy_func_2d

def compute_supremum_rectangle(
    f_expr: Any,
    g_expr: Any,
    x_bounds: Tuple[float, float],
    y_bounds: Tuple[float, float],
    precision: int = 50,
    resolution: int = 150
) -> Tuple[DualValue, List[Tuple[float, float]], Any, Any, Any]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    
    diff_expr = f_expr - g_expr
    
    f_num = create_numpy_func_2d(f_expr, x, y)
    g_num = create_numpy_func_2d(g_expr, x, y)
    
    def h_num(x_vals: np.ndarray, y_vals: np.ndarray) -> np.ndarray:
        return np.abs(f_num(x_vals, y_vals) - g_num(x_vals, y_vals))
        
    best_pt, best_val = find_maximum_2d(h_num, x_bounds, y_bounds, resolution)
    
    status = "numeric"
    method = "Aproksymacja numeryczna (siatka 2D + scipy.optimize na brzegach i wewnątrz)"
    
    dv = DualValue(
        exact=None,
        numeric=str(best_val),
        status=status,
        method=method,
        precision_digits=precision,
        notes=["Obliczenia dokładne na prostokącie są zazwyczaj skrajnie złożone; użyto aproksymacji."]
    )
    
    return dv, [best_pt], f_num, g_num, h_num
