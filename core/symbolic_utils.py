import sympy
from typing import Any, Dict, Set

def extract_variables(expr: Any) -> Set[sympy.Symbol]:
    try:
        return expr.free_symbols
    except Exception:
        return set()

def symbolic_eq(expr1: Any, expr2: Any) -> bool:
    try:
        if expr1 == expr2:
            return True
        diff = sympy.simplify(expr1 - expr2)
        return diff == 0
    except Exception:
        return False

def symbolic_eval(expr: Any, subs: Dict[sympy.Symbol, Any]) -> Any:
    try:
        return expr.subs(subs)
    except Exception:
        return None

def symbolic_derivative(expr: Any, var: sympy.Symbol) -> Any:
    try:
        return sympy.diff(expr, var)
    except Exception:
        return None
