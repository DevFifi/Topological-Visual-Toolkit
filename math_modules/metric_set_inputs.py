from dataclasses import dataclass
from itertools import product
from typing import Any, List, Optional, Tuple

import numpy as np
import sympy

from core.exact_numeric import DualValue
from core.set_parser import (
    CompositeSet,
    FinitePointSet,
    FiniteSet1D,
    Interval1D,
    Rectangle2D,
    normalize_set_input,
    parse_set_1d,
    parse_set_2d,
    split_top_level,
)
from math_modules.finite_metric_spaces import normalize_metric_name


@dataclass(frozen=True)
class CoordInterval:
    low: Any
    high: Any
    left_closed: bool = True
    right_closed: bool = True

    def low_float(self) -> float:
        return float(sympy.N(self.low))

    def high_float(self) -> float:
        return float(sympy.N(self.high))

    def is_point(self) -> bool:
        try:
            return abs(self.low_float() - self.high_float()) <= 1e-12 and self.left_closed and self.right_closed
        except Exception:
            return False

    def has_open_boundary(self) -> bool:
        return not self.left_closed or not self.right_closed


Box = Tuple[CoordInterval, ...]


@dataclass
class MetricSet:
    boxes: List[Box]
    dim: int
    source: str

    def has_open_boundary(self) -> bool:
        return any(interval.has_open_boundary() for box in self.boxes for interval in box)


def _strip_outer_parentheses(text: str) -> str:
    current = text.strip()
    while len(current) >= 2 and current[0] == "(" and current[-1] == ")":
        depth = 0
        ok = True
        for idx, ch in enumerate(current):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and idx != len(current) - 1:
                    ok = False
                    break
            if depth < 0:
                ok = False
                break
        if not ok or depth != 0:
            break
        current = current[1:-1].strip()
    return current


def _split_top_level_token(text: str, token: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    i = 0
    while i < len(text):
        ch = text[i]
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
        if not stack and text.startswith(token, i):
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


def _split_product_factors(text: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    i = 0
    while i < len(text):
        ch = text[i]
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
        if not stack and text.startswith("\\times", i):
            parts.append("".join(current).strip())
            current = []
            i += len("\\times")
            continue
        if not stack and ch in {"x", "X", "×"}:
            prev_idx = i - 1
            while prev_idx >= 0 and text[prev_idx].isspace():
                prev_idx -= 1
            next_idx = i + 1
            while next_idx < len(text) and text[next_idx].isspace():
                next_idx += 1
            prev_ch = text[prev_idx] if prev_idx >= 0 else ""
            next_ch = text[next_idx] if next_idx < len(text) else ""
            if ch == "×" or (prev_ch in "])}" and next_ch in "[({"):
                parts.append("".join(current).strip())
                current = []
                i += 1
                continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _coord_interval_from_interval(parsed: Interval1D) -> CoordInterval:
    return CoordInterval(parsed.a, parsed.b, parsed.left_closed, parsed.right_closed)


def _intersect_coord(a: CoordInterval, b: CoordInterval) -> Optional[CoordInterval]:
    a_low, a_high = a.low_float(), a.high_float()
    b_low, b_high = b.low_float(), b.high_float()

    if a_low > b_low + 1e-12:
        low, left_closed = a.low, a.left_closed
    elif b_low > a_low + 1e-12:
        low, left_closed = b.low, b.left_closed
    else:
        low, left_closed = a.low, a.left_closed and b.left_closed

    if a_high < b_high - 1e-12:
        high, right_closed = a.high, a.right_closed
    elif b_high < a_high - 1e-12:
        high, right_closed = b.high, b.right_closed
    else:
        high, right_closed = a.high, a.right_closed and b.right_closed

    low_f = float(sympy.N(low))
    high_f = float(sympy.N(high))
    if low_f > high_f + 1e-12:
        return None
    if abs(low_f - high_f) <= 1e-12 and not (left_closed and right_closed):
        return None
    return CoordInterval(low, high, left_closed, right_closed)


def _intersect_boxes(left: Box, right: Box) -> Optional[Box]:
    if len(left) != len(right):
        return None
    intervals = []
    for a, b in zip(left, right):
        intersection = _intersect_coord(a, b)
        if intersection is None:
            return None
        intervals.append(intersection)
    return tuple(intervals)


def _intersect_box_lists(left: List[Box], right: List[Box]) -> List[Box]:
    result = []
    for a in left:
        for b in right:
            intersection = _intersect_boxes(a, b)
            if intersection is not None:
                result.append(intersection)
    return result


def _boxes_from_1d_set(parsed: Any) -> Optional[List[Box]]:
    if isinstance(parsed, Interval1D):
        return [(CoordInterval(parsed.a, parsed.b, parsed.left_closed, parsed.right_closed),)]
    if isinstance(parsed, FiniteSet1D):
        return [(CoordInterval(element, element, True, True),) for element in parsed.elements]
    if isinstance(parsed, CompositeSet):
        left = _boxes_from_1d_set(parsed.left)
        right = _boxes_from_1d_set(parsed.right)
        if left is None or right is None:
            return None
        return left + right if parsed.operator == "union" else _intersect_box_lists(left, right)
    return None


def _boxes_from_2d_set(parsed: Any) -> Optional[List[Box]]:
    if isinstance(parsed, Rectangle2D):
        return [(
            _coord_interval_from_interval(parsed.x_interval),
            _coord_interval_from_interval(parsed.y_interval),
        )]
    if isinstance(parsed, FinitePointSet):
        return [
            tuple(CoordInterval(coord, coord, True, True) for coord in point)
            for point in parsed.points
            if len(point) == 2
        ]
    if isinstance(parsed, CompositeSet):
        left = _boxes_from_2d_set(parsed.left)
        right = _boxes_from_2d_set(parsed.right)
        if left is None or right is None:
            return None
        return left + right if parsed.operator == "union" else _intersect_box_lists(left, right)
    return None


def _parse_product_atom(text: str, dim: int) -> Optional[List[Box]]:
    factors = _split_product_factors(text)
    if len(factors) <= 1:
        return None
    if len(factors) != dim:
        return None

    factor_boxes: List[List[Box]] = []
    for factor in factors:
        parsed = parse_set_1d(factor)
        boxes = _boxes_from_1d_set(parsed) if parsed is not None else None
        if boxes is None:
            return None
        factor_boxes.append(boxes)

    result: List[Box] = []
    for combo in product(*factor_boxes):
        result.append(tuple(one_dim_box[0] for one_dim_box in combo))
    return result


def _parse_metric_set_boxes(text: str, dim: int) -> Optional[List[Box]]:
    stripped = _strip_outer_parentheses(normalize_set_input(text))
    for token, operator in ((" OR ", "union"), (" AND ", "intersection")):
        parts = _split_top_level_token(stripped, token)
        if len(parts) > 1:
            parsed_parts = [_parse_metric_set_boxes(part, dim) for part in parts]
            if any(part is None for part in parsed_parts):
                return None
            result = parsed_parts[0]
            for part in parsed_parts[1:]:
                result = result + part if operator == "union" else _intersect_box_lists(result, part)
            return result

    comma_parts = split_top_level(stripped)
    if len(comma_parts) > 1:
        parsed_parts = [_parse_metric_set_boxes(part, dim) for part in comma_parts]
        if any(part is None for part in parsed_parts):
            return None
        result = parsed_parts[0]
        for part in parsed_parts[1:]:
            result = _intersect_box_lists(result, part)
        return result

    product_boxes = _parse_product_atom(stripped, dim)
    if product_boxes is not None:
        return product_boxes

    if dim == 1:
        parsed_1d = parse_set_1d(stripped)
        return _boxes_from_1d_set(parsed_1d) if parsed_1d is not None else None

    if dim == 2:
        parsed_2d = parse_set_2d(stripped)
        return _boxes_from_2d_set(parsed_2d) if parsed_2d is not None else None

    return None


def parse_metric_set(text: str, dim: int) -> Optional[MetricSet]:
    boxes = _parse_metric_set_boxes(text, dim)
    if boxes is None or not boxes:
        return None
    if any(len(box) != dim for box in boxes):
        return None
    return MetricSet(boxes=boxes, dim=dim, source=text)


def metric_set_from_points(points: List[Tuple[Any, ...]]) -> Optional[MetricSet]:
    if not points:
        return None
    dim = len(points[0])
    if any(len(point) != dim for point in points):
        return None
    boxes = [
        tuple(CoordInterval(coord, coord, True, True) for coord in point)
        for point in points
    ]
    return MetricSet(boxes=boxes, dim=dim, source="punkty")


def _intervals_overlap_nonempty(a: CoordInterval, b: CoordInterval) -> bool:
    return _intersect_coord(a, b) is not None


def _box_intersection_nonempty(a: Box, b: Box) -> bool:
    return _intersect_boxes(a, b) is not None


def _closure_gap(a: CoordInterval, b: CoordInterval) -> float:
    a_low, a_high = a.low_float(), a.high_float()
    b_low, b_high = b.low_float(), b.high_float()
    return max(0.0, b_low - a_high, a_low - b_high)


def _range_delta(a: CoordInterval, b: CoordInterval) -> float:
    values = [
        abs(a.low_float() - b.low_float()),
        abs(a.low_float() - b.high_float()),
        abs(a.high_float() - b.low_float()),
        abs(a.high_float() - b.high_float()),
    ]
    return max(values)


def _metric_from_components(components: List[float], metric_name: str, custom_formula: str) -> Optional[float]:
    metric = normalize_metric_name(metric_name)
    arr = np.asarray(components, dtype=float)
    if metric == "Discrete":
        return 0.0 if np.all(arr <= 1e-12) else 1.0
    if metric == "Hamming":
        return float(np.sum(arr > 1e-12))
    if metric == "Manhattan":
        return float(np.sum(arr))
    if metric == "Euclidean":
        return float(np.sqrt(np.sum(arr * arr)))
    if metric == "Chebyshev":
        return float(np.max(arr)) if arr.size else 0.0
    if metric == "Minkowski":
        from math_modules.finite_metric_spaces import _minkowski_p_value

        p_val = _minkowski_p_value(custom_formula)
        if p_val is None:
            return None
        total = float(np.sum(arr ** p_val))
        return total ** (1.0 / p_val) if p_val >= 1 else total
    return None


def _box_distance(a: Box, b: Box, metric_name: str, custom_formula: str) -> Optional[float]:
    metric = normalize_metric_name(metric_name)
    if metric == "Discrete":
        return 0.0 if _box_intersection_nonempty(a, b) else 1.0
    if metric == "Hamming":
        return float(sum(0 if _intervals_overlap_nonempty(x, y) else 1 for x, y in zip(a, b)))
    return _metric_from_components([_closure_gap(x, y) for x, y in zip(a, b)], metric, custom_formula)


def _box_sup_distance(a: Box, b: Box, metric_name: str, custom_formula: str) -> Optional[float]:
    metric = normalize_metric_name(metric_name)
    if metric == "Discrete":
        all_points = all(interval.is_point() for interval in a + b)
        if all_points and _box_intersection_nonempty(a, b):
            return 0.0
        return 1.0
    if metric == "Hamming":
        components = [1.0 if _range_delta(x, y) > 1e-12 else 0.0 for x, y in zip(a, b)]
        return float(sum(components))
    return _metric_from_components([_range_delta(x, y) for x, y in zip(a, b)], metric, custom_formula)


def compute_metric_set_diam(metric_set: MetricSet, metric_name: str, custom_formula: str = "") -> Tuple[DualValue, Tuple[int, int]]:
    best_value = -np.inf
    best_pair = (-1, -1)
    for i, box_a in enumerate(metric_set.boxes):
        for j, box_b in enumerate(metric_set.boxes):
            value = _box_sup_distance(box_a, box_b, metric_name, custom_formula)
            if value is not None and np.isfinite(value) and value > best_value:
                best_value = value
                best_pair = (i, j)
    if best_pair == (-1, -1):
        return DualValue(status="error", notes=["Nie udało się policzyć średnicy zapisu zbiorowego."]), best_pair
    notes = ["Wynik dla zapisu zbiorowego jest liczony jako supremum średnicy."]
    if metric_set.has_open_boundary():
        notes.append("Zbiór ma otwarty brzeg, więc wartość może być tylko granicą, a nie odległością osiąganą przez punkty.")
    return DualValue(numeric=f"{best_value:.15g}", status="numeric", method="Numeryczne wzory dla pudełek/przedziałów.", notes=notes), best_pair


def compute_metric_set_dist(left: MetricSet, right: MetricSet, metric_name: str, custom_formula: str = "") -> Tuple[DualValue, Tuple[int, int]]:
    best_value = np.inf
    best_pair = (-1, -1)
    for i, box_a in enumerate(left.boxes):
        for j, box_b in enumerate(right.boxes):
            value = _box_distance(box_a, box_b, metric_name, custom_formula)
            if value is not None and np.isfinite(value) and value < best_value:
                best_value = value
                best_pair = (i, j)
    if best_pair == (-1, -1):
        return DualValue(status="error", notes=["Nie udało się policzyć odległości zapisu zbiorowego."]), best_pair
    notes = ["Wynik dla zapisu zbiorowego jest liczony jako infimum odległości."]
    if left.has_open_boundary() or right.has_open_boundary():
        notes.append("Dla otwartych brzegów infimum może nie być osiągane przez żadne dwa punkty.")
    return DualValue(numeric=f"{best_value:.15g}", status="numeric", method="Numeryczne wzory dla pudełek/przedziałów.", notes=notes), best_pair
