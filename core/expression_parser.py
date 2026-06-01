import re
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from typing import Any, Dict, Optional

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
        "e": sympy.E,
        "sqrt": sympy.sqrt,
        "Abs": sympy.Abs,
        "sin": sympy.sin,
        "cos": sympy.cos,
        "tan": sympy.tan,
        "exp": sympy.exp,
        "log": sympy.log,
        "Abs": sympy.Abs,
        "Min": sympy.Min,
        "Max": sympy.Max,
        "Sum": sympy.Sum,
        "root": sympy.root,
        "oo": sympy.oo,
        "i": sympy.Symbol("i", integer=True),
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

def _read_braced_group(text: str, start: int) -> Optional[tuple[str, int]]:
    if start >= len(text) or text[start] != "{":
        return None

    depth = 0
    for pos in range(start, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:pos], pos + 1
    return None

def _replace_latex_frac(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        if text.startswith("\\frac", i):
            pos = i + len("\\frac")
            while pos < len(text) and text[pos].isspace():
                pos += 1
            numerator = _read_braced_group(text, pos)
            if numerator is None:
                result.append(text[i])
                i += 1
                continue
            pos = numerator[1]
            while pos < len(text) and text[pos].isspace():
                pos += 1
            denominator = _read_braced_group(text, pos)
            if denominator is None:
                result.append(text[i])
                i += 1
                continue
            num = normalize_expression_input(numerator[0])
            den = normalize_expression_input(denominator[0])
            result.append(f"(({num})/({den}))")
            i = denominator[1]
        else:
            result.append(text[i])
            i += 1
    return "".join(result)

def _replace_latex_sqrt(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        if text.startswith("\\sqrt", i):
            pos = i + len("\\sqrt")
            while pos < len(text) and text[pos].isspace():
                pos += 1
            radicand = _read_braced_group(text, pos)
            if radicand is None:
                result.append(text[i])
                i += 1
                continue
            inner = normalize_expression_input(radicand[0])
            result.append(f"sqrt({inner})")
            i = radicand[1]
        else:
            result.append(text[i])
            i += 1
    return "".join(result)

def _replace_abs_bars(text: str) -> str:
    previous = None
    current = text
    pattern = re.compile(r"\|([^|]+)\|")
    while previous != current:
        previous = current
        current = pattern.sub(r"Abs(\1)", current)
    return current

def normalize_expression_input(expr_str: str) -> str:
    """Accept a small, practical subset of LaTeX-like notation used in forms."""
    s = str(expr_str).strip()
    if not s:
        return s

    replacements = {
        "\u2212": "-",
        "\u00b7": "*",
        "\u00d7": "*",
        "\u221a": "sqrt",
        "\u03c0": "pi",
        "\\pi": "pi",
        "\\cdot": "*",
        "\\times": "*",
        "\\left": "",
        "\\right": "",
        "\\,": "",
        "\\ ": "",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)

    s = _replace_latex_frac(s)
    s = _replace_latex_sqrt(s)

    latex_functions = {
        "\\sin": "sin",
        "\\cos": "cos",
        "\\tan": "tan",
        "\\exp": "exp",
        "\\log": "log",
        "\\ln": "log",
        "\\min": "Min",
        "\\max": "Max",
    }
    for old, new in latex_functions.items():
        s = s.replace(old, new)

    s = s.replace("{", "(").replace("}", ")")
    s = _replace_abs_bars(s)
    s = re.sub(r"\s+", " ", s)
    return s

def parse_expression(expr_str: str) -> ExpressionResult:
    if not expr_str or not str(expr_str).strip():
        return ExpressionResult(None, "Puste wyrażenie")
        
    try:
        normalized = normalize_expression_input(expr_str)
        ns = _create_namespace()
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        expr = parse_expr(
            normalized,
            local_dict=ns,
            transformations=transformations,
            evaluate=True
        )
        return ExpressionResult(expr)
    except Exception as e:
        return ExpressionResult(None, f"Błąd parsowania: {str(e)}")

def simplify_expression(expr: Any) -> Any:
    try:
        return sympy.simplify(expr)
    except Exception:
        return expr
