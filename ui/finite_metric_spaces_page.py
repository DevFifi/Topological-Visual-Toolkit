from typing import Any, List, Optional, Tuple

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


def _resize_points_text(text: str, target_dim: int) -> Tuple[str, bool]:
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
    add_or_update_history_entry("points", e_str.strip(), "Zbiór E")
    if f_str.strip():
        add_or_update_history_entry("points", f_str.strip(), "Zbiór F")
    if metric == "custom" and custom_formula.strip():
        add_or_update_history_entry("custom_metrics", custom_formula.strip(), "Metryka własna")
    if metric == "Minkowski" and custom_formula.strip():
        add_or_update_history_entry("metrics", custom_formula.strip(), "Parametr Minkowskiego")


def render() -> None:
    st.header("Skończone przestrzenie metryczne")
    st.caption("Macierz odległości, średnica skończonego zbioru oraz odległość między dwoma zbiorami.")

    if "metric_dim" not in st.session_state:
        st.session_state.metric_dim = 2

    old_dim = st.session_state.metric_dim
    col1, col2 = st.columns(2)
    with col1:
        new_dim = st.number_input("Wymiar n", min_value=1, max_value=20, value=old_dim, step=1, key="metric_dim_input")
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
            "custom_metrics",
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
        custom_formula = math_input("Parametr p", "metrics", "minkowski_p", default_val="2", preview=True, preview_prefix_latex="p = ")
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
    e_str = input_with_history("Punkty zbioru E", "points", "points_e", default_val=e_default, multiline=True)
    parsed_e_preview, e_preview_valid = _parse_points(e_str, dim)
    if e_preview_valid and parsed_e_preview:
        st.caption("Podgląd E")
        st.latex(r"E = \left\{" + ", ".join(latex_point(p) for p in parsed_e_preview[:8]) + (r", \ldots" if len(parsed_e_preview) > 8 else "") + r"\right\}")

    st.subheader("Zbiór F")
    f_str = input_with_history("Punkty zbioru F (opcjonalnie)", "points", "points_f", multiline=True)
    parsed_f_preview, f_preview_valid = _parse_points(f_str, dim) if f_str.strip() else ([], True)
    if f_preview_valid and parsed_f_preview:
        st.caption("Podgląd F")
        st.latex(r"F = \left\{" + ", ".join(latex_point(p) for p in parsed_f_preview[:8]) + (r", \ldots" if len(parsed_f_preview) > 8 else "") + r"\right\}")

    if st.button("Oblicz", type="primary"):
        E, e_valid = _parse_points(e_str, dim)
        F, f_valid = _parse_points(f_str, dim) if f_str.strip() else ([], True)

        if not e_valid or not E:
            st.error(f"Zbiór E musi być niepusty, a każdy punkt musi mieć dokładnie {dim} współrzędnych.")
            return
        if f_str.strip() and (not f_valid or not F):
            st.error(f"Zbiór F jest niepoprawny. Każdy punkt musi mieć dokładnie {dim} współrzędnych.")
            return

        formula, status = _get_distance_formula(metric, custom_formula, dim)
        if status == "error":
            if metric_internal == "Minkowski":
                st.error("Niepoprawny parametr metryki Minkowskiego. Wymagane p > 0.")
            else:
                st.error("Niepoprawny wzór metryki.")
            return

        _save_valid_inputs(metric, custom_formula, e_str, f_str)

        st.write("### Macierz odległości D(e_i, e_j)")
        headers = [format_point(p) for p in E]
        headers_latex = [latex_point(p) for p in E]
        if len(E) > 20:
            st.warning("Zbiór ma więcej niż 20 punktów, więc macierz nie jest wyświetlana w całości.")
        else:
            render_distance_matrix_html(headers, compute_distance_matrix(E, metric, custom_formula), headers_latex=headers_latex)

        st.write("### Średnica diam(E)")
        diam_dv, diam_pair = compute_diam(E, metric, custom_formula)
        if diam_pair[0] >= 0:
            diam_dv.notes.append(f"Para realizująca: {headers[diam_pair[0]]} i {headers[diam_pair[1]]}")
        render_dual_value(diam_dv)

        if F:
            st.write("### Macierz odległości E × F")
            f_headers = [format_point(p) for p in F]
            f_headers_latex = [latex_point(p) for p in F]
            if len(E) * len(F) > 400:
                st.warning("Macierz E × F jest zbyt duża do wygodnego wyświetlenia.")
            else:
                matrix_ef = [[compute_distance(p1, p2, formula, metric) for p2 in F] for p1 in E]
                render_distance_matrix_html(
                    f_headers,
                    matrix_ef,
                    row_headers=headers,
                    headers_latex=f_headers_latex,
                    row_headers_latex=headers_latex,
                )

            st.write("### Odległość dist(E, F)")
            dist_dv, dist_pair = compute_dist_sets(E, F, metric, custom_formula)
            if dist_pair[0] >= 0:
                dist_dv.notes.append(f"Para realizująca: {headers[dist_pair[0]]} ∈ E oraz {f_headers[dist_pair[1]]} ∈ F")
            render_dual_value(dist_dv)
