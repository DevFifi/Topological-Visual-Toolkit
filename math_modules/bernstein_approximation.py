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
    if n <= 15:  # Zmniejszamy próg, by nie obciążać SymPy dla trygonometrii
        try:
            terms = []
            for k in range(n + 1):
                binom = sympy.binomial(n, k)
                val = f_expr.subs(x, sympy.Rational(k, n))
                if not val.is_Rational and not val.is_Integer:
                    val = val.evalf(5) # przybliżamy, by sympy nie wisiało na sin(1/15)
                term = binom * (x**k) * ((1 - x)**(n - k)) * val
                terms.append(term)
            exact_b_n = sympy.expand(sum(terms))
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
    f_num = create_numpy_func_1d(f_expr, x)
    
    # Zadanie mówi "w rozsądnym przybliżeniu - odległość Czebyszewa"
    # Szukamy supremum numerycznie na gęstej siatce (jest to optymalne i szybkie)
    grid_size = 5000 + n * 50
    x_vals = np.linspace(0.0, 1.0, grid_size)
    
    y_f = f_num(x_vals)
    y_b = b_num(x_vals)
    err = np.abs(y_f - y_b)
    
    valid = ~np.isnan(err)
    if not np.any(valid):
        max_err = float('nan')
    else:
        max_err = np.max(err[valid])
        
    return DualValue(
        numeric=str(max_err),
        status="numeric",
        method=f"Aproksymacja numeryczna siatką ({grid_size} pkt)"
    )
