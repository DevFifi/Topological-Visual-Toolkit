import re
from typing import Any, List, Optional

import sympy

from core.expression_parser import parse_expression

TOLERANCE = 1e-9


def normalize_set_input(text: str) -> str:
    normalized = (
        str(text)
        .strip()
        .replace("\\leq", "<=")
        .replace("\\le", "<=")
        .replace("≤", "<=")
        .replace("\\geq", ">=")
        .replace("\\ge", ">=")
        .replace("≥", ">=")
        .replace("\\ne", "!=")
        .replace("≠", "!=")
        .replace("\\(", "")
        .replace("\\)", "")
        .replace("\\land", " AND ")
        .replace("\\wedge", " AND ")
        .replace("\\cap", " AND ")
        .replace("∧", " AND ")
        .replace("∩", " AND ")
        .replace("&&", " AND ")
        .replace("\\lor", " OR ")
        .replace("\\vee", " OR ")
        .replace("\\cup", " OR ")
        .replace("∨", " OR ")
        .replace("∪", " OR ")
        .replace("||", " OR ")
    )
    normalized = re.sub(r"\band\b", " AND ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bor\b", " OR ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\boraz\b", " AND ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\blub\b", " OR ", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def split_top_level(text: str, separator: str = ",") -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())

    for ch in text:
        if ch in pairs:
            stack.append(pairs[ch])
            current.append(ch)
        elif ch in closing:
            if stack and ch == stack[-1]:
                stack.pop()
            current.append(ch)
        elif ch == separator and not stack:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


class ParsedSet:
    def contains_symbolic(self, point: Any) -> Any:
        return False

    def contains_numeric(self, point: Any) -> bool:
        return False

    def classify_numeric(self, point: Any, tolerance: float = TOLERANCE) -> str:
        return "true" if self.contains_numeric(point) else "false"

    def contains_arrays(self, x_values: Any, y_values: Any, tolerance: float = TOLERANCE):
        import numpy as np

        result = np.zeros_like(x_values, dtype=bool)
        rows, cols = result.shape
        for i in range(rows):
            for j in range(cols):
                result[i, j] = self.classify_numeric((x_values[i, j], y_values[i, j]), tolerance) == "true"
        return result


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
        return self.classify_numeric(point) == "true"

    def classify_numeric(self, point: Any, tolerance: float = TOLERANCE) -> str:
        try:
            p_val = float(point)
            a_val = float(self.a)
            b_val = float(self.b)

            if abs(p_val - a_val) <= tolerance and not self.left_closed:
                return "boundary"
            if abs(p_val - b_val) <= tolerance and not self.right_closed:
                return "boundary"

            left_ok = p_val >= a_val - tolerance if self.left_closed else p_val > a_val + tolerance
            right_ok = p_val <= b_val + tolerance if self.right_closed else p_val < b_val - tolerance
            return "true" if left_ok and right_ok else "false"
        except Exception:
            return "false"

    def to_latex(self) -> str:
        left = "[" if self.left_closed else "("
        right = "]" if self.right_closed else ")"
        return f"{left}{sympy.latex(self.a)}, {sympy.latex(self.b)}{right}"


class FiniteSet1D(ParsedSet):
    def __init__(self, elements: List[Any]):
        self.elements = elements

    def contains_symbolic(self, point: Any) -> Any:
        try:
            if not self.elements:
                return sympy.false
            return sympy.Or(*[sympy.Eq(point, e) for e in self.elements])
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        try:
            p_val = float(point)
            return any(abs(p_val - float(e)) <= TOLERANCE for e in self.elements)
        except Exception:
            return False

    def to_latex(self) -> str:
        return r"\left\{" + ", ".join(sympy.latex(e) for e in self.elements) + r"\right\}"


class FinitePointSet(ParsedSet):
    def __init__(self, points: List[tuple[Any, ...]]):
        self.points = points
        self.dim = len(points[0]) if points else 0

    def contains_symbolic(self, point: Any) -> Any:
        try:
            if not self.points:
                return sympy.false
            return sympy.Or(
                *[
                    sympy.And(*[sympy.Eq(coord, target) for coord, target in zip(point, stored)])
                    for stored in self.points
                    if len(stored) == len(point)
                ]
            )
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        return self.classify_numeric(point) == "true"

    def classify_numeric(self, point: Any, tolerance: float = TOLERANCE) -> str:
        try:
            coords = tuple(float(coord) for coord in point)
            for stored in self.points:
                if len(stored) != len(coords):
                    continue
                stored_vals = tuple(float(coord.evalf()) for coord in stored)
                if all(abs(a - b) <= tolerance for a, b in zip(coords, stored_vals)):
                    return "true"
            return "false"
        except Exception:
            return "false"

    def contains_arrays(self, x_values: Any, y_values: Any, tolerance: float = TOLERANCE):
        import numpy as np

        result = np.zeros_like(x_values, dtype=bool)
        for point in self.points:
            if len(point) != 2:
                continue
            px = float(point[0].evalf())
            py = float(point[1].evalf())
            result |= (np.abs(x_values - px) <= tolerance) & (np.abs(y_values - py) <= tolerance)
        return np.asarray(result, dtype=bool)

    def to_latex(self) -> str:
        point_latex = [
            r"\left(" + ", ".join(sympy.latex(coord) for coord in point) + r"\right)"
            for point in self.points
        ]
        return r"\left\{" + ", ".join(point_latex) + r"\right\}"


class CompositeSet(ParsedSet):
    def __init__(self, left: ParsedSet, right: ParsedSet, operator: str):
        self.left = left
        self.right = right
        self.operator = operator

    def contains_symbolic(self, point: Any) -> Any:
        try:
            if self.operator == "union":
                return sympy.Or(self.left.contains_symbolic(point), self.right.contains_symbolic(point))
            return sympy.And(self.left.contains_symbolic(point), self.right.contains_symbolic(point))
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        return self.classify_numeric(point) == "true"

    def classify_numeric(self, point: Any, tolerance: float = TOLERANCE) -> str:
        left = self.left.classify_numeric(point, tolerance)
        right = self.right.classify_numeric(point, tolerance)
        if self.operator == "union":
            if "true" in {left, right}:
                return "true"
            if "boundary" in {left, right}:
                return "boundary"
            return "false"
        if "false" in {left, right}:
            return "false"
        if "boundary" in {left, right}:
            return "boundary"
        return "true"

    def contains_arrays(self, x_values: Any, y_values: Any, tolerance: float = TOLERANCE):
        left = self.left.contains_arrays(x_values, y_values, tolerance)
        right = self.right.contains_arrays(x_values, y_values, tolerance)
        return left | right if self.operator == "union" else left & right

    def to_latex(self) -> str:
        op = r"\cup" if self.operator == "union" else r"\cap"
        left = self.left.to_latex() if hasattr(self.left, "to_latex") else "?"
        right = self.right.to_latex() if hasattr(self.right, "to_latex") else "?"
        return r"\left(" + left + rf"\right) {op} \left(" + right + r"\right)"


class Rectangle2D(ParsedSet):
    def __init__(self, x_interval: Interval1D, y_interval: Interval1D):
        self.x_interval = x_interval
        self.y_interval = y_interval

    def contains_symbolic(self, point: Any) -> Any:
        try:
            px, py = point
            return sympy.And(
                self.x_interval.contains_symbolic(px),
                self.y_interval.contains_symbolic(py),
            )
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        try:
            px, py = point
            return self.x_interval.contains_numeric(px) and self.y_interval.contains_numeric(py)
        except Exception:
            return False

    def to_latex(self) -> str:
        return f"{self.x_interval.to_latex()} \\times {self.y_interval.to_latex()}"

    def contains_arrays(self, x_values: Any, y_values: Any, tolerance: float = TOLERANCE):
        import numpy as np

        xa = float(self.x_interval.a.evalf())
        xb = float(self.x_interval.b.evalf())
        ya = float(self.y_interval.a.evalf())
        yb = float(self.y_interval.b.evalf())
        x_left = x_values >= xa - tolerance if self.x_interval.left_closed else x_values > xa + tolerance
        x_right = x_values <= xb + tolerance if self.x_interval.right_closed else x_values < xb - tolerance
        y_left = y_values >= ya - tolerance if self.y_interval.left_closed else y_values > ya + tolerance
        y_right = y_values <= yb + tolerance if self.y_interval.right_closed else y_values < yb - tolerance
        return np.asarray(x_left & x_right & y_left & y_right, dtype=bool)


class Relation2D(ParsedSet):
    def __init__(self, lhs: Any, rhs: Any, operator: str):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def _relation(self, lhs: Any, rhs: Any) -> Any:
        if self.operator == "<":
            return sympy.Lt(lhs, rhs)
        if self.operator == "<=":
            return sympy.Le(lhs, rhs)
        if self.operator == ">":
            return sympy.Gt(lhs, rhs)
        if self.operator == ">=":
            return sympy.Ge(lhs, rhs)
        if self.operator == "!=":
            return sympy.Ne(lhs, rhs)
        return sympy.Eq(lhs, rhs)

    def contains_symbolic(self, point: Any) -> Any:
        try:
            px, py = point
            x_sym = sympy.Symbol("x", real=True)
            y_sym = sympy.Symbol("y", real=True)
            u_sym = sympy.Symbol("u", real=True)
            v_sym = sympy.Symbol("v", real=True)
            subs = {x_sym: px, y_sym: py, u_sym: px, v_sym: py}
            return self._relation(self.lhs.subs(subs), self.rhs.subs(subs))
        except Exception:
            return False

    def contains_numeric(self, point: Any) -> bool:
        return self.classify_numeric(point) == "true"

    def classify_numeric(self, point: Any, tolerance: float = TOLERANCE) -> str:
        try:
            px, py = float(point[0]), float(point[1])
            x_sym = sympy.Symbol("x", real=True)
            y_sym = sympy.Symbol("y", real=True)
            u_sym = sympy.Symbol("u", real=True)
            v_sym = sympy.Symbol("v", real=True)
            subs = {x_sym: px, y_sym: py, u_sym: px, v_sym: py}
            diff = float((self.lhs - self.rhs).subs(subs).evalf())

            if self.operator == "<":
                return "boundary" if abs(diff) <= tolerance else ("true" if diff < 0 else "false")
            if self.operator == "<=":
                return "true" if diff <= tolerance else "false"
            if self.operator == ">":
                return "boundary" if abs(diff) <= tolerance else ("true" if diff > 0 else "false")
            if self.operator == ">=":
                return "true" if diff >= -tolerance else "false"
            if self.operator == "!=":
                return "false" if abs(diff) <= tolerance else "true"
            return "true" if abs(diff) <= tolerance else "false"
        except Exception:
            return "false"

    def to_latex(self) -> str:
        op_map = {
            "<": "<",
            "<=": r"\le",
            ">": ">",
            ">=": r"\ge",
            "!=": r"\ne",
            "==": "=",
            "=": "=",
        }
        return f"{sympy.latex(self.lhs)} {op_map.get(self.operator, self.operator)} {sympy.latex(self.rhs)}"

    def contains_arrays(self, x_values: Any, y_values: Any, tolerance: float = TOLERANCE):
        import numpy as np

        x_sym = sympy.Symbol("x", real=True)
        y_sym = sympy.Symbol("y", real=True)
        u_sym = sympy.Symbol("u", real=True)
        v_sym = sympy.Symbol("v", real=True)
        diff_expr = self.lhs - self.rhs
        func = sympy.lambdify((x_sym, y_sym, u_sym, v_sym), diff_expr, modules=["numpy", "scipy"])
        try:
            with np.errstate(divide="ignore", invalid="ignore", over="ignore", under="ignore"):
                diff = np.asarray(func(x_values, y_values, x_values, y_values), dtype=float)
            if diff.shape != np.asarray(x_values).shape:
                diff = np.broadcast_to(diff, np.asarray(x_values).shape).astype(float)
        except Exception:
            return super().contains_arrays(x_values, y_values, tolerance)

        finite = np.isfinite(diff)
        if self.operator == "<":
            mask = diff < 0
        elif self.operator == "<=":
            mask = diff <= tolerance
        elif self.operator == ">":
            mask = diff > 0
        elif self.operator == ">=":
            mask = diff >= -tolerance
        elif self.operator == "!=":
            mask = np.abs(diff) > tolerance
        else:
            mask = np.abs(diff) <= tolerance
        return np.asarray(mask & finite, dtype=bool)


Inequality2D = Relation2D


def _strip_enclosing_parentheses(s: str) -> str:
    current = s.strip()
    changed = True
    while changed and len(current) >= 2 and current[0] == "(" and current[-1] == ")":
        changed = False
        depth = 0
        encloses_all = True
        for idx, ch in enumerate(current):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and idx != len(current) - 1:
                    encloses_all = False
                    break
            if depth < 0:
                encloses_all = False
                break
        if encloses_all and depth == 0:
            current = current[1:-1].strip()
            changed = True
    return current


def _split_top_level_token(s: str, token: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in pairs:
            stack.append(pairs[ch])
            current.append(ch)
            i += 1
            continue
        if ch in closing:
            if stack and ch == stack[-1]:
                stack.pop()
            current.append(ch)
            i += 1
            continue
        if not stack and s.startswith(token, i):
            parts.append("".join(current).strip())
            current = []
            i += len(token)
            continue
        current.append(ch)
        i += 1

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _parse_logical_set(s: str, atom_parser) -> Optional[ParsedSet]:
    stripped = _strip_enclosing_parentheses(s)
    for token, operator in ((" OR ", "union"), (" AND ", "intersection")):
        parts = _split_top_level_token(stripped, token)
        if len(parts) > 1:
            parsed_parts = [_parse_logical_set(part, atom_parser) for part in parts]
            if any(part is None for part in parsed_parts):
                return None
            result = parsed_parts[0]
            for part in parsed_parts[1:]:
                result = CompositeSet(result, part, operator)
            return result

    raw = s.strip()
    if len(raw) >= 2 and raw[0] in "([{" and raw[-1] in ")]}":
        direct = atom_parser(raw)
        if direct is not None:
            return direct
        if stripped != raw:
            direct = atom_parser(stripped)
            if direct is not None:
                return direct

    comma_parts = split_top_level(stripped)
    if len(comma_parts) > 1:
        parsed_parts = [_parse_logical_set(part, atom_parser) for part in comma_parts]
        if any(part is None for part in parsed_parts):
            return None
        result = parsed_parts[0]
        for part in parsed_parts[1:]:
            result = CompositeSet(result, part, "intersection")
        return result
    direct = atom_parser(raw)
    if direct is not None:
        return direct
    return atom_parser(stripped)


def _parse_set_1d_atom(s: str) -> Optional[ParsedSet]:
    s = s.strip()
    if len(s) >= 2 and s[0] in "[(" and s[-1] in "])":
        left_bracket, right_bracket = s[0], s[-1]
        parts = split_top_level(s[1:-1])
        if len(parts) != 2:
            return None
        a_str, b_str = parts
        res_a = parse_expression(a_str)
        res_b = parse_expression(b_str)
        if res_a.is_valid and res_b.is_valid:
            try:
                if float(res_a.expr.evalf()) > float(res_b.expr.evalf()):
                    return None
            except Exception:
                pass
            return Interval1D(
                res_a.expr,
                res_b.expr,
                left_closed=(left_bracket == "["),
                right_closed=(right_bracket == "]"),
            )
        return None

    finite_match = re.match(r"^\{\s*(.*)\s*\}$", s)
    if finite_match:
        inner = finite_match.group(1).strip()
        if not inner:
            return FiniteSet1D([])
        parts = split_top_level(inner)
        elements = []
        for part in parts:
            res = parse_expression(part)
            if not res.is_valid:
                return None
            elements.append(res.expr)
        return FiniteSet1D(elements)

    return None


def parse_set_1d(set_str: str) -> Optional[ParsedSet]:
    s = normalize_set_input(set_str)
    return _parse_logical_set(s, _parse_set_1d_atom)


def _split_rectangle_product(s: str) -> Optional[tuple[str, str]]:
    s = s.strip()
    if not s or s[0] not in "[(":
        return None

    expected = "]" if s[0] == "[" else ")"
    depth = 0
    first_end = -1
    for idx, ch in enumerate(s):
        if ch == s[0]:
            depth += 1
        elif ch == expected:
            depth -= 1
            if depth == 0:
                first_end = idx + 1
                break

    if first_end <= 0:
        return None

    rest = s[first_end:].strip()
    delimiter = next((d for d in ("\\times", "×", "x", "X") if rest.startswith(d)), None)
    if delimiter is None:
        return None

    second = rest[len(delimiter):].strip()
    return (s[:first_end], second) if second else None


def _find_relation_operator(s: str) -> Optional[tuple[int, str]]:
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    operators = ("<=", ">=", "==", "!=", "<", ">", "=")

    i = 0
    while i < len(s):
        ch = s[i]
        if ch in pairs:
            stack.append(pairs[ch])
            i += 1
            continue
        if ch in closing:
            if stack and ch == stack[-1]:
                stack.pop()
            i += 1
            continue
        if not stack:
            for op in operators:
                if s.startswith(op, i):
                    if op == "=" and (
                        (i > 0 and s[i - 1] in "<>!=")
                        or (i + 1 < len(s) and s[i + 1] == "=")
                    ):
                        continue
                    return i, op
        i += 1
    return None


def _find_relation_operators(s: str) -> List[tuple[int, str]]:
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    operators = ("<=", ">=", "==", "!=", "<", ">", "=")
    found: List[tuple[int, str]] = []

    i = 0
    while i < len(s):
        ch = s[i]
        if ch in pairs:
            stack.append(pairs[ch])
            i += 1
            continue
        if ch in closing:
            if stack and ch == stack[-1]:
                stack.pop()
            i += 1
            continue
        if not stack:
            matched = None
            for op in operators:
                if s.startswith(op, i):
                    if op == "=" and (
                        (i > 0 and s[i - 1] in "<>!=")
                        or (i + 1 < len(s) and s[i + 1] == "=")
                    ):
                        continue
                    matched = op
                    break
            if matched is not None:
                found.append((i, matched))
                i += len(matched)
                continue
        i += 1
    return found


def _parse_finite_point_set(s: str) -> Optional[FinitePointSet]:
    finite_match = re.match(r"^\{\s*(.*)\s*\}$", s)
    if not finite_match:
        return None

    inner = finite_match.group(1).strip()
    if not inner:
        return FinitePointSet([])

    points = []
    for item in split_top_level(inner):
        item = item.strip()
        if not ((item.startswith("(") and item.endswith(")")) or (item.startswith("[") and item.endswith("]"))):
            return None
        coords = []
        for coord_text in split_top_level(item[1:-1]):
            res = parse_expression(coord_text)
            if not res.is_valid:
                return None
            coords.append(res.expr)
        if not coords:
            return None
        points.append(tuple(coords))

    if points and any(len(point) != len(points[0]) for point in points):
        return None
    return FinitePointSet(points)


def _parse_chained_relation_2d(s: str) -> Optional[ParsedSet]:
    found = _find_relation_operators(s)
    if len(found) < 2:
        return None

    parts = []
    start = 0
    for pos, op in found:
        parts.append(s[start:pos].strip())
        start = pos + len(op)
    parts.append(s[start:].strip())
    if any(not part for part in parts):
        return None

    expressions = []
    for part in parts:
        res = parse_expression(part)
        if not res.is_valid:
            return None
        expressions.append(res.expr)

    result: Optional[ParsedSet] = None
    for idx, (_, op) in enumerate(found):
        relation = Relation2D(expressions[idx], expressions[idx + 1], "==" if op == "=" else op)
        result = relation if result is None else CompositeSet(result, relation, "intersection")
    return result


def _parse_relation_2d(s: str) -> Optional[ParsedSet]:
    found = _find_relation_operator(s)
    if found is None:
        return None

    pos, op = found
    lhs_str = s[:pos].strip()
    rhs_str = s[pos + len(op):].strip()
    if not lhs_str or not rhs_str:
        return None

    lhs = parse_expression(lhs_str)
    rhs = parse_expression(rhs_str)
    if lhs.is_valid and rhs.is_valid:
        return Relation2D(lhs.expr, rhs.expr, "==" if op == "=" else op)
    return None


def _parse_set_2d_atom(s: str) -> Optional[ParsedSet]:
    s = _strip_enclosing_parentheses(s)

    finite_points = _parse_finite_point_set(s)
    if finite_points is not None:
        return finite_points

    rect_match = _split_rectangle_product(s)
    if rect_match:
        x_set = parse_set_1d(rect_match[0])
        y_set = parse_set_1d(rect_match[1])
        if isinstance(x_set, Interval1D) and isinstance(y_set, Interval1D):
            return Rectangle2D(x_set, y_set)

    chained = _parse_chained_relation_2d(s)
    if chained is not None:
        return chained

    return _parse_relation_2d(s)


def parse_set_2d(set_str: str) -> Optional[ParsedSet]:
    s = normalize_set_input(set_str)
    return _parse_logical_set(s, _parse_set_2d_atom)


def set_latex(parsed_set: ParsedSet, name: str = "A") -> str:
    if hasattr(parsed_set, "to_latex"):
        return f"{name} = {parsed_set.to_latex()}"
    return name
