from typing import Any, Tuple

import sympy


def _sympify_if_possible(expr: Any) -> Any:
    if expr is None:
        return None
    if isinstance(expr, str):
        try:
            return sympy.sympify(expr)
        except Exception:
            return expr
    return expr


def _expand_roots(expr: Any) -> Any:
    if not isinstance(expr, sympy.Basic):
        return expr

    if (
        isinstance(expr, sympy.Pow)
        and getattr(expr.exp, "is_Rational", False)
        and expr.exp.q > 1
    ):
        base = sympy.expand(expr.base)
        return sympy.Pow(base, expr.exp)

    def is_root(node: Any) -> bool:
        return (
            isinstance(node, sympy.Pow)
            and getattr(node.exp, "is_Rational", False)
            and node.exp.q > 1
        )

    def expand_root(node: Any) -> Any:
        base = sympy.expand(node.base)
        return sympy.Pow(base, node.exp)

    return expr.replace(is_root, expand_root)


def _expanded_root_variant(expr: Any) -> Any:
    if (
        isinstance(expr, sympy.Pow)
        and getattr(expr.exp, "is_Rational", False)
        and expr.exp.q > 1
    ):
        return sympy.Pow(sympy.expand(expr.base), expr.exp)
    return _expand_roots(expr)


def simplify_exact(expr: Any, max_ops: int = 220) -> Any:
    try:
        value = _sympify_if_possible(expr)
        if not isinstance(value, sympy.Basic):
            return value
        if sympy.count_ops(value) > max_ops:
            return sympy.simplify(value)

        candidates = [value]
        for transform in (
            sympy.simplify,
            sympy.radsimp,
            sympy.sqrtdenest,
            _expand_roots,
            _expanded_root_variant,
            lambda e: _expanded_root_variant(sympy.simplify(e)),
            lambda e: sympy.expand(sympy.simplify(e)),
            lambda e: sympy.factor(sympy.expand(sympy.simplify(e))),
        ):
            try:
                candidate = transform(value)
                if isinstance(candidate, sympy.Basic):
                    candidates.append(candidate)
            except Exception:
                continue

        def score(candidate: Any) -> tuple[int, int, int]:
            text = sympy.sstr(candidate)
            squared_parentheses_penalty = text.count(")**2") * 30
            return len(text) + squared_parentheses_penalty, len(text), int(sympy.count_ops(candidate))

        return min(candidates, key=score)
    except Exception:
        return expr


def format_exact(expr: Any) -> str:
    try:
        if expr is None:
            return ""
        value = simplify_exact(expr)
        if value == sympy.E:
            return "e"
        text = sympy.sstr(value) if isinstance(value, sympy.Basic) else str(value)
        return text.replace("E", "e")
    except Exception:
        return str(expr).replace("E", "e")


def latex_exact(expr: Any) -> str:
    try:
        if expr is None:
            return ""
        value = simplify_exact(expr)
        return sympy.latex(value)
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


def latex_point(pt: Tuple[Any, ...]) -> str:
    return r"\left(" + ", ".join(latex_exact(c) for c in pt) + r"\right)"
