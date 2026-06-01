import re
from typing import Any, List, Optional, Tuple

import numpy as np
import streamlit as st

from core.expression_parser import parse_expression
from core.formatting import format_point, latex_point
from core.history import add_or_update_history_entry
from core.set_parser import split_top_level
from math_modules.finite_metric_spaces import (
    METRIC_DISPLAY_NAMES,
    _get_distance_formula,
    compute_diam,
    compute_dist_sets,
    compute_distance,
    compute_distance_matrix,
    metric_formula_latex,
    normalize_metric_name,
)
from math_modules.metric_set_inputs import (
    compute_metric_set_diam,
    compute_metric_set_dist,
    metric_set_from_points,
    parse_metric_set,
)
from math_modules.metric_validation import validate_metric_heuristically
from ui.components import input_with_history, math_input, render_distance_matrix_html, render_dual_value


def _parse_single_point(text: str, dim: int, strict: bool) -> Tuple[Optional[Tuple[Any, ...]], bool]:
    item = text.strip()
    if not item:
        return None, False

    if (item.startswith("(") and item.endswith(")")) or (item.startswith("[") and item.endswith("]")):
        parts = split_top_level(item[1:-1])
    elif dim == 1:
        parts = [item]
    else:
        return None, False

    coords = []
    for part in parts:
        res = parse_expression(part)
        if not res.is_valid:
            return None, False
        coords.append(res.expr)

    if strict and len(coords) != dim:
        return None, False
    return tuple(coords), True


def _parse_point_any_dim(text: str) -> Tuple[Optional[Tuple[Any, ...]], bool]:
    item = text.strip()
    if not item:
        return None, False
    if (item.startswith("(") and item.endswith(")")) or (item.startswith("[") and item.endswith("]")):
        parts = split_top_level(item[1:-1])
    else:
        parts = [item]

    coords = []
    for part in parts:
        res = parse_expression(part)
        if not res.is_valid:
            return None, False
        coords.append(res.expr)
    return tuple(coords), True


def _parse_points_any_dim(text: str) -> Tuple[List[Tuple[Any, ...]], bool]:
    cleaned = text.strip()
    if not cleaned:
        return [], True

    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1].strip()
        items = split_top_level(inner) if inner else []
    else:
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if len(lines) == 1:
            loose_items = split_top_level(lines[0])
            items = loose_items if len(loose_items) > 1 else lines
        else:
            items = lines

    points: List[Tuple[Any, ...]] = []
    all_valid = True
    for item in items:
        point, valid = _parse_point_any_dim(item)
        if point is not None and valid:
            points.append(point)
        else:
            all_valid = False
    return points, all_valid


def _parse_generator_args(args_text: str) -> dict:
    result = {}
    for item in split_top_level(args_text):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        result[key.strip().lower()] = value.strip()
    return result


def _parse_generated_points(text: str, dim: int) -> Optional[Tuple[List[Tuple[Any, ...]], bool]]:
    match = re.match(r"^\s*(random|basis|line)\s*\((.*)\)\s*$", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    kind = match.group(1).lower()
    args = _parse_generator_args(match.group(2))
    try:
        requested_dim = int(args.get("dim", dim))
        if requested_dim != dim or requested_dim < 1 or requested_dim > 200:
            return [], False

        if kind == "basis":
            points = [tuple(0 for _ in range(dim))]
            for idx in range(dim):
                coords = [0 for _ in range(dim)]
                coords[idx] = 1
                points.append(tuple(coords))
            return points, True

        count = int(args.get("count", "100"))
        if count < 1 or count > 5000:
            return [], False

        if kind == "line":
            denom = max(1, count - 1)
            points = []
            for row in range(count):
                t = row / denom
                points.append(tuple(float(((axis + 1) * t) % 1.0) for axis in range(dim)))
            return points, True

        seed = int(args.get("seed", "1"))
        scale = float(args.get("scale", "1"))
        rng = np.random.default_rng(seed)
        values = rng.uniform(-scale, scale, size=(count, dim))
        return [tuple(float(value) for value in row) for row in values], True
    except Exception:
        return [], False


def _resize_generator_text(text: str, target_dim: int) -> Optional[str]:
    match = re.match(r"^\s*(random|basis|line)\s*\((.*)\)\s*$", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    args = _parse_generator_args(match.group(2))
    args["dim"] = str(target_dim)
    ordered_keys = ["count", "dim", "seed", "scale"]
    parts = [f"{key}={args.pop(key)}" for key in ordered_keys if key in args]
    parts.extend(f"{key}={value}" for key, value in sorted(args.items()))
    return f"{match.group(1).lower()}(" + ", ".join(parts) + ")"


def _resize_points_text(text: str, target_dim: int) -> Tuple[str, bool]:
    generator_text = _resize_generator_text(text, target_dim)
    if generator_text is not None:
        return generator_text, True

    points, all_valid = _parse_points_any_dim(text)
    if not all_valid:
        return text, False

    resized = []
    for point in points:
        values = list(point[:target_dim])
        if len(values) < target_dim:
            values.extend([0] * (target_dim - len(values)))
        resized.append(format_point(tuple(values)))
    return "\n".join(resized), all_valid


def _apply_dimension_change(target_dim: int) -> bool:
    all_valid = True
    for key_name in ("points_e_input", "points_f_input"):
        if key_name in st.session_state and str(st.session_state[key_name]).strip():
            resized, valid = _resize_points_text(st.session_state[key_name], target_dim)
            st.session_state[key_name] = resized
            all_valid = all_valid and valid
    st.session_state.metric_dim = target_dim
    return all_valid


def _default_points_text(dim: int) -> str:
    if dim == 1:
        return "[1, 2]"
    zero = "(" + ", ".join(["0"] * dim) + ")"
    one = "(" + ", ".join(["1"] * dim) + ")"
    return f"[{zero}, {one}]"


def _metric_options_order() -> List[str]:
    return [
        METRIC_DISPLAY_NAMES["Discrete"],
        METRIC_DISPLAY_NAMES["Hamming"],
        METRIC_DISPLAY_NAMES["Manhattan"],
        METRIC_DISPLAY_NAMES["Euclidean"],
        METRIC_DISPLAY_NAMES["Minkowski"],
        METRIC_DISPLAY_NAMES["Chebyshev"],
        METRIC_DISPLAY_NAMES["custom"],
    ]


def _parse_points(text: str, dim: int, strict: bool = True) -> Tuple[list, bool]:
    cleaned = text.strip()
    if not cleaned:
        return [], True

    generated = _parse_generated_points(cleaned, dim)
    if generated is not None:
        return generated

    items = []
    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1].strip()
        if inner:
            items = split_top_level(inner)
    else:
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if len(lines) == 1:
            loose_items = split_top_level(lines[0])
            items = loose_items if len(loose_items) > 1 else lines
        else:
            items = lines

    points = []
    all_valid = True
    for item in items:
        point, valid = _parse_single_point(item, dim, strict)
        if valid and point is not None:
            points.append(point)
        else:
            all_valid = False
    return points, all_valid


def _save_valid_inputs(metric: str, custom_formula: str, e_str: str, f_str: str) -> None:
    metric = normalize_metric_name(metric)
    add_or_update_history_entry("metric_points", e_str.strip(), "E")
    if f_str.strip():
        add_or_update_history_entry("metric_points", f_str.strip(), "F")
    if metric == "custom" and custom_formula.strip():
        add_or_update_history_entry("metric_custom_metrics", custom_formula.strip())
    if metric == "Minkowski" and custom_formula.strip():
        add_or_update_history_entry("metric_params", custom_formula.strip())


def render() -> None:
    st.header("Skończone przestrzenie metryczne")
    st.caption("Macierz odległości, średnica skończonego zbioru oraz odległość między dwoma zbiorami.")

    if "metric_dim" not in st.session_state:
        st.session_state.metric_dim = 2

    old_dim = st.session_state.metric_dim
    col1, col2 = st.columns(2)
    with col1:
        new_dim = st.number_input("Wymiar n", min_value=1, max_value=200, value=old_dim, step=1, key="metric_dim_input")
        dim = old_dim
        if new_dim != old_dim:
            if new_dim < old_dim:
                st.warning(f"Zmniejszenie wymiaru do {new_dim} obetnie nadmiarowe współrzędne punktów.")
                st.info(f"Do potwierdzenia obliczenia nadal używają wymiaru n = {old_dim}.")
                if st.button("Potwierdzam zmianę wymiaru"):
                    valid_resize = _apply_dimension_change(int(new_dim))
                    if not valid_resize:
                        st.warning("Niektóre niepoprawne wpisy pominięto przy zmianie wymiaru.")
                    st.rerun()
            else:
                valid_resize = _apply_dimension_change(int(new_dim))
                if not valid_resize:
                    st.warning("Niektóre niepoprawne wpisy pominięto przy zmianie wymiaru.")
                st.rerun()
    with col2:
        metric_options = _metric_options_order()
        metric = st.selectbox(
            "Metryka",
            metric_options,
            index=metric_options.index(METRIC_DISPLAY_NAMES["Euclidean"]),
            key="metric_selectbox_pl",
        )
        # st.caption(r"Kolejność: $\delta$, $d_H$, $d_1$, $d_2$, $d_p$, $d_\infty$, $\varphi$.")

    custom_formula = ""
    metric_internal = normalize_metric_name(metric)
    if metric_internal == "custom":
        st.subheader("Wzór metryki własnej")
        st.caption("Użyj zmiennych x1...xn, y1...yn albo skrótu SUM(...), np. SUM(|xi-yi|).")
        custom_formula = math_input(
            "φ(x,y) =",
            "metric_custom_metrics",
            "custom_metric",
            default_val="SUM(|xi-yi|)",
            preview=False,
            help_text="Przykłady: SUM(|xi-yi|), sqrt(SUM((xi-yi)^2)), Max(|x1-y1|, |x2-y2|).",
        )
        if custom_formula.strip():
            formula, status = _get_distance_formula("custom", custom_formula, dim)
            if status == "error":
                st.error("Nie można sparsować wzoru metryki.")
            else:
                is_valid, msg = validate_metric_heuristically(formula, "custom", dim)
                (st.success if is_valid else st.warning)(msg)
    elif metric_internal == "Minkowski":
        custom_formula = math_input("Parametr p", "metric_params", "minkowski_p", default_val="2", preview=True, preview_prefix_latex="p = ")
        p_res = parse_expression(custom_formula)
        if p_res.is_valid:
            try:
                p_val = float(p_res.expr.evalf())
                if p_val <= 0:
                    st.error("Parametr p musi być dodatni.")
                elif p_val < 1:
                    st.info("Dla 0 < p < 1 używana jest definicja z wykładu: suma |xi-yi|^p bez pierwiastka.")
            except Exception:
                st.error("Parametr p musi być liczbą rzeczywistą.")
        else:
            st.error("Parametr p musi być liczbą.")

    formula_preview = metric_formula_latex(metric, custom_formula, dim)
    if formula_preview:
        st.caption("Wzór używany w obliczeniach")
        st.latex(formula_preview)

    st.subheader("Zbiór E")
    e_default = _default_points_text(dim)
    e_str = input_with_history("Punkty zbioru E", "metric_points", "points_e", default_val=e_default, multiline=True)
    parsed_e_preview, e_preview_valid = _parse_points(e_str, dim)
    if e_preview_valid and parsed_e_preview:
        st.caption(f"Rozpoznano {len(parsed_e_preview)} punktów w R^{dim}.")
        st.caption("Podgląd E")
        st.latex(r"E = \left\{" + ", ".join(latex_point(p) for p in parsed_e_preview[:8]) + (r", \ldots" if len(parsed_e_preview) > 8 else "") + r"\right\}")
    elif e_str.strip():
        e_set_preview = parse_metric_set(e_str, dim)
        if e_set_preview:
            st.caption(f"Rozpoznano zapis zbiorowy E w R^{dim}: {len(e_set_preview.boxes)} składnik(ów) pudełkowych.")

    st.subheader("Zbiór F")
    f_str = input_with_history("Punkty zbioru F (opcjonalnie)", "metric_points", "points_f", multiline=True)
    parsed_f_preview, f_preview_valid = _parse_points(f_str, dim) if f_str.strip() else ([], True)
    if f_preview_valid and parsed_f_preview:
        st.caption(f"Rozpoznano {len(parsed_f_preview)} punktów w R^{dim}.")
        st.caption("Podgląd F")
        st.latex(r"F = \left\{" + ", ".join(latex_point(p) for p in parsed_f_preview[:8]) + (r", \ldots" if len(parsed_f_preview) > 8 else "") + r"\right\}")
    elif f_str.strip():
        f_set_preview = parse_metric_set(f_str, dim)
        if f_set_preview:
            st.caption(f"Rozpoznano zapis zbiorowy F w R^{dim}: {len(f_set_preview.boxes)} składnik(ów) pudełkowych.")

    if st.button("Oblicz", type="primary"):
        E, e_valid = _parse_points(e_str, dim)
        F, f_valid = _parse_points(f_str, dim) if f_str.strip() else ([], True)
        E_set = None if (e_valid and E) else parse_metric_set(e_str, dim)
        F_set = None if (f_valid and F) else (parse_metric_set(f_str, dim) if f_str.strip() else None)

        if (not e_valid or not E) and E_set is None:
            st.error(f"Zbiór E musi być niepusty: podaj punkty w R^{dim} albo zapis pudełkowy/przedziałowy zgodny z wymiarem.")
            return
        if f_str.strip() and (not f_valid or not F) and F_set is None:
            st.error(f"Zbiór F jest niepoprawny: podaj punkty w R^{dim} albo zapis pudełkowy/przedziałowy zgodny z wymiarem.")
            return
        if metric_internal == "custom" and (E_set is not None or F_set is not None):
            st.error("Zapis przedziałowy/pudełkowy działa dla metryk standardowych. Dla metryki własnej podaj skończoną listę punktów.")
            return

        formula, status = _get_distance_formula(metric, custom_formula, dim)
        if status == "error":
            if metric_internal == "Minkowski":
                st.error("Niepoprawny parametr metryki Minkowskiego. Wymagane p > 0.")
            else:
                st.error("Niepoprawny wzór metryki.")
            return

        _save_valid_inputs(metric, custom_formula, e_str, f_str)

        headers = [format_point(p) for p in E] if E_set is None else []
        headers_latex = [latex_point(p) for p in E] if E_set is None else []
        if E_set is None:
            st.write("### Macierz odległości D(e_i, e_j)")
            if len(E) > 20:
                st.warning("Zbiór ma więcej niż 20 punktów, więc macierz nie jest wyświetlana w całości.")
            else:
                render_distance_matrix_html(headers, compute_distance_matrix(E, metric, custom_formula), headers_latex=headers_latex)
        else:
            st.info("Dla zapisu przedziałowego/pudełkowego macierz punktowa nie jest wyświetlana, bo zbiór nie musi być skończony.")

        st.write("### Średnica diam(E)")
        if E_set is None:
            diam_dv, diam_pair = compute_diam(E, metric, custom_formula)
        else:
            diam_dv, diam_pair = compute_metric_set_diam(E_set, metric, custom_formula)
        render_dual_value(diam_dv)
        if E_set is None and diam_pair[0] >= 0:
            st.caption("Para realizująca")
            st.latex(
                r"e_i = "
                + latex_point(E[diam_pair[0]])
                + r",\quad e_j = "
                + latex_point(E[diam_pair[1]])
            )

        if F or F_set is not None:
            f_headers = [format_point(p) for p in F] if F_set is None else []
            if E_set is None and F_set is None:
                st.write("### Macierz odległości E x F")
                f_headers_latex = [latex_point(p) for p in F]
                if len(E) * len(F) > 400:
                    st.warning("Macierz E x F jest zbyt duża do wygodnego wyświetlenia.")
                else:
                    matrix_ef = [[compute_distance(p1, p2, formula, metric) for p2 in F] for p1 in E]
                    render_distance_matrix_html(
                        f_headers,
                        matrix_ef,
                        row_headers=headers,
                        headers_latex=f_headers_latex,
                        row_headers_latex=headers_latex,
                    )
            else:
                st.info("Dla zapisu przedziałowego/pudełkowego macierz E x F nie jest wyświetlana.")

            st.write("### Odległość dist(E, F)")
            if E_set is None and F_set is None:
                dist_dv, dist_pair = compute_dist_sets(E, F, metric, custom_formula)
            else:
                left_set = E_set or metric_set_from_points(E)
                right_set = F_set or metric_set_from_points(F)
                if left_set is None or right_set is None:
                    st.error("Nie udało się zbudować zbiorów do obliczenia dist(E,F).")
                    return
                dist_dv, dist_pair = compute_metric_set_dist(left_set, right_set, metric, custom_formula)
            render_dual_value(dist_dv)
            if E_set is None and F_set is None and dist_pair[0] >= 0:
                st.caption("Para realizująca")
                st.latex(
                    r"e = "
                    + latex_point(E[dist_pair[0]])
                    + r" \in E,\quad f = "
                    + latex_point(F[dist_pair[1]])
                    + r" \in F"
                )
        return
