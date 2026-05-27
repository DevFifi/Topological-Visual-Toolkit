import sympy
import numpy as np
from typing import Tuple, List, Any
from core.exact_numeric import DualValue
from core.optimization import find_maximum_1d
from core.safe_eval import create_numpy_func_1d

def compute_supremum_interval(
    f_expr: Any,
    g_expr: Any,
    a: float,
    b: float,
    precision: int = 50,
    resolution: int = 2000
) -> Tuple[DualValue, List[float], Any, Any, Any]:
    x = sympy.Symbol("x", real=True)
    
    diff_expr = f_expr - g_expr
    h_sq = sympy.simplify(diff_expr**2)
    h_abs = sympy.Abs(diff_expr)
    
    f_num = create_numpy_func_1d(f_expr, x)
    g_num = create_numpy_func_1d(g_expr, x)
    
    def h_num(vals: np.ndarray) -> np.ndarray:
        return np.abs(f_num(vals) - g_num(vals))
        
    best_x, best_y = find_maximum_1d(h_num, a, b, resolution)
    
    exact_val = None
    status = "numeric"
    method = "Aproksymacja numeryczna (próbkowanie + scipy.optimize)"
    
    try:
        deriv = sympy.diff(h_sq, x)
        roots = sympy.solve(deriv, x)
        
        candidates = [sympy.sympify(a), sympy.sympify(b)]
        for r in roots:
            try:
                rf = float(r.evalf())
                if a <= rf <= b:
                    candidates.append(r)
            except Exception:
                pass
                
        max_exact = None
        max_float = -1.0
        best_exact_x = []
        
        for cand in candidates:
            try:
                val = h_abs.subs(x, cand)
                val_f = float(val.evalf())
                if val_f > max_float + 1e-9:
                    max_float = val_f
                    max_exact = val
                    best_exact_x = [cand]
                elif abs(val_f - max_float) <= 1e-9:
                    best_exact_x.append(cand)
            except Exception:
                pass
                
        if max_exact is not None and abs(max_float - best_y) < 1e-3:
            exact_val = sympy.simplify(max_exact)
            status = "exact_and_numeric"
            method = "Dokładne metody symboliczne (pochodna) + ewaluacja"
            best_y = max_float
            best_x_list = [float(cx.evalf()) for cx in best_exact_x]
        else:
            best_x_list = [best_x]
            
    except Exception:
        best_x_list = [best_x]
        
    dv = DualValue(
        exact=str(exact_val) if exact_val is not None else None,
        numeric=str(best_y),
        status=status,
        method=method,
        precision_digits=precision
    )
    
    return dv, best_x_list, f_num, g_num, h_num
