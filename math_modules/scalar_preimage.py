import sympy
import numpy as np
from typing import Any, Tuple, Optional
from core.set_parser import ParsedSet
from core.exact_numeric import DualValue
from core.safe_eval import create_numpy_func_2d

def compute_scalar_preimage_membership(
    f_expr: Any,
    A_set: ParsedSet,
    point: Tuple[float, float],
    precision: int = 50
) -> Tuple[str, DualValue]:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    px, py = point
    
    try:
        exact_val = f_expr.subs({x: sympy.sympify(px), y: sympy.sympify(py)})
        numeric_val = float(exact_val.evalf())
        
        dv = DualValue(
            exact=str(sympy.simplify(exact_val)),
            numeric=str(numeric_val),
            status="exact_and_numeric",
            precision_digits=precision
        )
        
        sym_check = A_set.contains_symbolic(exact_val)
        if sym_check in [True, False]:
            return "true" if sym_check else "false", dv
            
        num_check = A_set.contains_numeric(numeric_val)
        return "true" if num_check else "false", dv
        
    except Exception:
        f_num = create_numpy_func_2d(f_expr, x, y)
        numeric_val = f_num(np.array([px]), np.array([py]))[0]
        
        dv = DualValue(
            numeric=str(numeric_val),
            status="numeric",
            precision_digits=precision
        )
        
        num_check = A_set.contains_numeric(numeric_val)
        return "true" if num_check else "false", dv
