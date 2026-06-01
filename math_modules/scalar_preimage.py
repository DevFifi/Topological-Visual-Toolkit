import sympy
import numpy as np
from typing import Any, Tuple
from core.set_parser import ParsedSet
from core.exact_numeric import DualValue
from core.formatting import latex_exact, simplify_exact
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
        if not np.isfinite(numeric_val):
            raise ValueError
        
        simplified_exact = simplify_exact(exact_val)
        dv = DualValue(
            exact=str(simplified_exact),
            exact_latex=latex_exact(simplified_exact),
            numeric=str(numeric_val),
            status="exact_and_numeric",
            precision_digits=precision
        )
        
        sym_check = A_set.contains_symbolic(exact_val)
        if sym_check == sympy.true or sym_check is True:
            return "true" if sym_check else "false", dv
        if sym_check == sympy.false or sym_check is False:
            return "false", dv
            
        return A_set.classify_numeric(numeric_val), dv
        
    except Exception:
        f_num = create_numpy_func_2d(f_expr, x, y)
        try:
            px_num = float(sympy.sympify(px).evalf())
            py_num = float(sympy.sympify(py).evalf())
        except Exception:
            return "unknown", DualValue(status="error", notes=["Punkt nie ma skończonych współrzędnych rzeczywistych."])
        numeric_val = f_num(np.array([px_num], dtype=float), np.array([py_num], dtype=float))[0]
        if not np.isfinite(numeric_val):
            return "unknown", DualValue(status="error", notes=["Wartość funkcji w punkcie nie jest skończona."])
        
        dv = DualValue(
            numeric=str(numeric_val),
            status="numeric",
            precision_digits=precision
        )
        
        return A_set.classify_numeric(numeric_val), dv
