import sympy
from typing import List, Tuple, Any, Optional
from core.exact_numeric import DualValue
from core.expression_parser import parse_expression

def expand_sum_macro(formula_str: str, dim: int) -> str:
    if "SUM(" not in formula_str:
        return formula_str
    res = ""
    i = 0
    while i < len(formula_str):
        if formula_str[i:].startswith("SUM("):
            start = i + 4
            paren_count = 1
            j = start
            while j < len(formula_str) and paren_count > 0:
                if formula_str[j] == '(': paren_count += 1
                elif formula_str[j] == ')': paren_count -= 1
                j += 1
            if paren_count == 0:
                inner_expr = formula_str[start:j-1]
                expanded = []
                for k in range(1, dim + 1):
                    term = inner_expr.replace("xi", f"x{k}").replace("yi", f"y{k}").replace("|", "Abs(")
                    term = term.replace("Abs(x", "Abs(x").replace(")", ")") # simplified absolute handling
                    expanded.append(f"({term})")
                res += "(" + " + ".join(expanded) + ")"
                i = j
                continue
        res += formula_str[i]
        i += 1
    return res

def _get_distance_formula(metric_name: str, custom_formula: str, dim: int) -> Tuple[Optional[Any], str]:
    if metric_name == "custom" and custom_formula:
        import re
        custom_formula = re.sub(r'\|([^|]+)\|', r'Abs(\1)', custom_formula)
        custom_formula = expand_sum_macro(custom_formula, dim)
        res = parse_expression(custom_formula)
        if res.is_valid:
            return res.expr, "exact_and_numeric"
        return None, "error"
        
    x_vars = [sympy.Symbol(f"x{i+1}", real=True) for i in range(dim)]
    y_vars = [sympy.Symbol(f"y{i+1}", real=True) for i in range(dim)]
    
    if metric_name == "Euclidean":
        return sympy.sqrt(sum((x - y)**2 for x, y in zip(x_vars, y_vars))), "exact_and_numeric"
    elif metric_name == "Manhattan":
        return sum(sympy.Abs(x - y) for x, y in zip(x_vars, y_vars)), "exact_and_numeric"
    elif metric_name == "Chebyshev":
        return sympy.Max(*[sympy.Abs(x - y) for x, y in zip(x_vars, y_vars)]), "exact_and_numeric"
    elif metric_name == "Discrete":
        return sympy.Piecewise((0, sympy.And(*[sympy.Eq(x, y) for x, y in zip(x_vars, y_vars)])), (1, True)), "exact_and_numeric"
    elif metric_name == "Hamming":
        return sum(sympy.Piecewise((0, sympy.Eq(x, y)), (1, True)) for x, y in zip(x_vars, y_vars)), "exact_and_numeric"
    elif metric_name == "Minkowski":
        try:
            p_val = float(custom_formula)
            if p_val < 1:
                return sum(sympy.Abs(x - y)**p_val for x, y in zip(x_vars, y_vars)), "exact_and_numeric"
            else:
                return (sum(sympy.Abs(x - y)**p_val for x, y in zip(x_vars, y_vars)))**(1/p_val), "exact_and_numeric"
        except Exception:
            return None, "error"
        
    return None, "error"

def compute_distance(p1: Tuple[Any, ...], p2: Tuple[Any, ...], formula: Any, metric_name: str) -> DualValue:
    if metric_name == "Discrete":
        try:
            is_same = all(sympy.simplify(c1 - c2) == 0 for c1, c2 in zip(p1, p2))
            val = 0 if is_same else 1
            return DualValue(exact=str(val), numeric=str(val), status="exact_and_numeric")
        except Exception:
            return DualValue(status="error", notes=["Błąd porównania punktów"])
            
    dim = len(p1)
    subs = {}
    for i in range(dim):
        subs[sympy.Symbol(f"x{i+1}", real=True)] = p1[i]
        subs[sympy.Symbol(f"y{i+1}", real=True)] = p2[i]
        
    try:
        exact_val = formula.subs(subs)
        numeric_val = exact_val.evalf()
        return DualValue(
            exact=str(sympy.simplify(exact_val)),
            numeric=str(float(numeric_val)),
            status="exact_and_numeric"
        )
    except Exception:
        return DualValue(status="error", notes=["Błąd obliczenia odległości"])

def compute_distance_matrix(points: List[Tuple[Any, ...]], metric_name: str, custom_formula: str = "") -> List[List[DualValue]]:
    if not points:
        return []
        
    dim = len(points[0])
    formula, _ = _get_distance_formula(metric_name, custom_formula, dim)
    
    n = len(points)
    matrix = [[DualValue() for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = DualValue(exact="0", numeric="0.0", status="exact_and_numeric")
            elif i < j:
                dv = compute_distance(points[i], points[j], formula, metric_name)
                matrix[i][j] = dv
                matrix[j][i] = dv
                
    return matrix

def compute_diam(points: List[Tuple[Any, ...]], metric_name: str, custom_formula: str = "") -> Tuple[DualValue, Tuple[int, int]]:
    matrix = compute_distance_matrix(points, metric_name, custom_formula)
    n = len(points)
    max_val = -1.0
    best_pair = (0, 0)
    best_dv = DualValue(exact="0", numeric="0.0", status="exact_and_numeric")
    
    for i in range(n):
        for j in range(i+1, n):
            dv = matrix[i][j]
            if dv.numeric:
                val = float(dv.numeric)
                if val > max_val:
                    max_val = val
                    best_pair = (i, j)
                    best_dv = dv
                    
    return best_dv, best_pair

def compute_dist_sets(E: List[Tuple[Any, ...]], F: List[Tuple[Any, ...]], metric_name: str, custom_formula: str = "") -> Tuple[DualValue, Tuple[int, int]]:
    if not E or not F:
        return DualValue(status="error"), (-1, -1)
        
    dim = len(E[0])
    formula, _ = _get_distance_formula(metric_name, custom_formula, dim)
    
    min_val = float('inf')
    best_pair = (0, 0)
    best_dv = DualValue(status="error")
    
    for i, p1 in enumerate(E):
        for j, p2 in enumerate(F):
            dv = compute_distance(p1, p2, formula, metric_name)
            if dv.numeric:
                val = float(dv.numeric)
                if val < min_val:
                    min_val = val
                    best_pair = (i, j)
                    best_dv = dv
                    
    return best_dv, best_pair
