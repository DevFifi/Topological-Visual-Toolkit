import sympy
import numpy as np
import scipy.special as sp
from typing import Tuple, Any, Callable
from core.exact_numeric import DualValue
from math_modules.supremum_interval import compute_supremum_interval
from core.safe_eval import create_numpy_func_1d

def compute_bernstein_polynomial(f_expr: Any, n: int) -> Tuple[Any, Callable]:
    x = sympy.Symbol("x", real=True)
    
    # Exact symbolic computation for small n
    exact_b_n = None
    if n <= 30:
        try:
            terms = []
            for k in range(n + 1):
                binom = sympy.binomial(n, k)
                term = binom * (x**k) * ((1 - x)**(n - k)) * f_expr.subs(x, sympy.Rational(k, n))
                terms.append(term)
            exact_b_n = sum(terms)
        except Exception:
            pass
            
    f_num = create_numpy_func_1d(f_expr, x)
    
    # Stable numerical evaluation for any n
    def b_num(x_vals: np.ndarray) -> np.ndarray:
        x_vals = np.asarray(x_vals, dtype=float)
        result = np.zeros_like(x_vals)
        for k in range(n + 1):
            f_val = f_num(np.array([k / n]))[0]
            if np.isnan(f_val):
                continue
            binom = sp.comb(n, k)
            result += binom * (x_vals**k) * ((1.0 - x_vals)**(n - k)) * f_val
        return result
        
    return exact_b_n, b_num

def compute_bernstein_error(f_expr: Any, exact_b_n: Any, b_num: Callable, n: int, precision: int = 50) -> DualValue:
    x = sympy.Symbol("x", real=True)
    
    # Fallback expression for numerical evaluation if exact is too big
    if exact_b_n is not None:
        g_expr = exact_b_n
    else:
        g_expr = sympy.Symbol("B_n(x)") # Placeholder
        
    dv, _, _, _, _ = compute_supremum_interval(f_expr, g_expr, 0.0, 1.0, precision=precision)
    
    # If the interval computation used the placeholder and failed, compute manually
    if dv.numeric is None or exact_b_n is None:
        f_num = create_numpy_func_1d(f_expr, x)
        x_vals = np.linspace(0.0, 1.0, 2000)
        err = np.abs(f_num(x_vals) - b_num(x_vals))
        max_err = np.nanmax(err)
        dv = DualValue(
            numeric=str(max_err),
            status="numeric",
            method="Aproksymacja numeryczna błędu (siatka z 2000 punktów)"
        )
        
    return dv
