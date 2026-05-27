import mpmath
import sympy
from typing import Any, Optional

def set_mpmath_dps(digits: int) -> None:
    mpmath.mp.dps = digits

def to_mpmath(expr: Any) -> Any:
    try:
        if isinstance(expr, (int, float)):
            return mpmath.mpf(expr)
        
        evaluated = expr.evalf(mpmath.mp.dps)
        if hasattr(evaluated, 'is_real') and evaluated.is_real:
            return mpmath.mpf(str(evaluated))
        return None
    except Exception:
        return None

def high_precision_numeric_compare(expr1: Any, expr2: Any, tolerance: float = 1e-12) -> int:
    try:
        v1 = to_mpmath(expr1)
        v2 = to_mpmath(expr2)
        if v1 is None or v2 is None:
            v1_f = float(expr1.evalf())
            v2_f = float(expr2.evalf())
            diff = v1_f - v2_f
        else:
            diff = float(v1 - v2)
            
        if abs(diff) < tolerance:
            return 0
        return 1 if diff > 0 else -1
    except Exception:
        return 0

def numerical_eq(expr1: Any, expr2: Any, tolerance: float = 1e-12) -> bool:
    return high_precision_numeric_compare(expr1, expr2, tolerance) == 0

def float_eval(expr: Any, subs: dict) -> Optional[float]:
    try:
        val = expr.subs(subs).evalf()
        return float(val)
    except Exception:
        return None
