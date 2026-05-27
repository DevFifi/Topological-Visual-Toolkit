import re
import sympy
from typing import Any, Dict, List, Optional, Tuple, Union
from core.expression_parser import parse_expression

class ParsedSet:
    def contains_symbolic(self, point: Any) -> Any:
        return False
        
    def contains_numeric(self, point: Any) -> bool:
        return False

class Interval1D(ParsedSet):
    def __init__(self, a: Any, b: Any, left_closed: bool, right_closed: bool):
        self.a = a
        self.b = b
        self.left_closed = left_closed
        self.right_closed = right_closed

    def contains_symbolic(self, point: Any) -> Any:
        try:
            left_cond = point >= self.a if self.left_closed else point > self.a
            right_cond = point <= self.b if self.right_closed else point < self.b
            return sympy.And(left_cond, right_cond)
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        try:
            p_val = float(point)
            a_val = float(self.a)
            b_val = float(self.b)
            left_ok = p_val >= a_val if self.left_closed else p_val > a_val
            right_ok = p_val <= b_val if self.right_closed else p_val < b_val
            return left_ok and right_ok
        except Exception:
            return False

class FiniteSet1D(ParsedSet):
    def __init__(self, elements: List[Any]):
        self.elements = elements

    def contains_symbolic(self, point: Any) -> Any:
        try:
            return sympy.Or(*[sympy.Eq(point, e) for e in self.elements])
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        try:
            p_val = float(point)
            return any(abs(p_val - float(e)) < 1e-12 for e in self.elements)
        except Exception:
            return False

class Rectangle2D(ParsedSet):
    def __init__(self, x_interval: Interval1D, y_interval: Interval1D):
        self.x_interval = x_interval
        self.y_interval = y_interval

    def contains_symbolic(self, point: Any) -> Any:
        try:
            px, py = point
            return sympy.And(
                self.x_interval.contains_symbolic(px),
                self.y_interval.contains_symbolic(py)
            )
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        try:
            px, py = point
            return self.x_interval.contains_numeric(px) and self.y_interval.contains_numeric(py)
        except Exception:
            return False

class Inequality2D(ParsedSet):
    def __init__(self, expr: Any):
        self.expr = expr

    def contains_symbolic(self, point: Any) -> Any:
        try:
            px, py = point
            subbed = self.expr.subs({"x": px, "y": py, "u": px, "v": py})
            return subbed
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        try:
            px, py = float(point[0]), float(point[1])
            subbed = self.expr.subs({"x": px, "y": py, "u": px, "v": py})
            return bool(subbed)
        except Exception:
            return False

def parse_set_1d(set_str: str) -> Optional[ParsedSet]:
    s = set_str.strip()
    
    interval_match = re.match(r"^([\[\(])\s*(.+?)\s*,\s*(.+?)\s*([\]\)])$", s)
    if interval_match:
        left_bracket, a_str, b_str, right_bracket = interval_match.groups()
        res_a = parse_expression(a_str)
        res_b = parse_expression(b_str)
        if res_a.is_valid and res_b.is_valid:
            return Interval1D(
                res_a.expr, res_b.expr,
                left_closed=(left_bracket == "["),
                right_closed=(right_bracket == "]")
            )
            
    finite_match = re.match(r"^\{\s*(.+)\s*\}$", s)
    if finite_match:
        parts = finite_match.group(1).split(",")
        elements = []
        for p in parts:
            res = parse_expression(p)
            if res.is_valid:
                elements.append(res.expr)
        if elements:
            return FiniteSet1D(elements)
            
    return None

def parse_set_2d(set_str: str) -> Optional[ParsedSet]:
    s = set_str.strip()
    
    rect_match = re.split(r"\s*[xX×]\s*", s)
    if len(rect_match) == 2:
        x_set = parse_set_1d(rect_match[0])
        y_set = parse_set_1d(rect_match[1])
        if isinstance(x_set, Interval1D) and isinstance(y_set, Interval1D):
            return Rectangle2D(x_set, y_set)
            
    if "<" in s or ">" in s or "=" in s:
        res = parse_expression(s)
        if res.is_valid:
            return Inequality2D(res.expr)
            
    return None
