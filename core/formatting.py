from typing import Any, Tuple
from core.exact_numeric import DualValue

def format_exact(expr: Any) -> str:
    try:
        if expr is None:
            return ""
        return str(expr)
    except Exception:
        return str(expr)

def format_numeric(val: Any, precision: int = 6) -> str:
    try:
        if val is None:
            return ""
        f_val = float(val)
        return f"{f_val:.{precision}g}"
    except Exception:
        return str(val)

def format_interval(interval: Tuple[Any, Any], precision: int = 6) -> str:
    try:
        a = format_numeric(interval[0], precision)
        b = format_numeric(interval[1], precision)
        return f"[{a}, {b}]"
    except Exception:
        return str(interval)

def format_point(pt: Tuple[Any, ...]) -> str:
    return "(" + ", ".join(format_exact(c) for c in pt) + ")"
