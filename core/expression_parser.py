import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from typing import Any, Dict, Optional, Tuple

class ExpressionResult:
    def __init__(self, expr: Any, error: Optional[str] = None):
        self.expr = expr
        self.error = error
        
    @property
    def is_valid(self) -> bool:
        return self.error is None

def _create_namespace() -> Dict[str, Any]:
    ns: Dict[str, Any] = {
        "pi": sympy.pi,
        "E": sympy.E,
        "sqrt": sympy.sqrt,
        "Abs": sympy.Abs,
        "sin": sympy.sin,
        "cos": sympy.cos,
        "tan": sympy.tan,
        "exp": sympy.exp,
        "log": sympy.log,
        "Min": sympy.Min,
        "Max": sympy.Max,
        "Piecewise": sympy.Piecewise,
        "x": sympy.Symbol("x", real=True),
        "y": sympy.Symbol("y", real=True),
        "u": sympy.Symbol("u", real=True),
        "v": sympy.Symbol("v", real=True),
    }
    
    for i in range(1, 21):
        ns[f"x{i}"] = sympy.Symbol(f"x{i}", real=True)
        ns[f"y{i}"] = sympy.Symbol(f"y{i}", real=True)
        ns[f"dx{i}"] = sympy.Symbol(f"dx{i}", real=True)
        
    return ns

def parse_expression(expr_str: str) -> ExpressionResult:
    if not expr_str or not str(expr_str).strip():
        return ExpressionResult(None, "Expression is empty")
        
    try:
        ns = _create_namespace()
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        expr = parse_expr(
            str(expr_str),
            local_dict=ns,
            transformations=transformations,
            evaluate=True
        )
        return ExpressionResult(expr)
    except Exception as e:
        return ExpressionResult(None, f"Parse error: {str(e)}")

def simplify_expression(expr: Any) -> Any:
    try:
        return sympy.simplify(expr)
    except Exception:
        return expr
