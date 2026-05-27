import streamlit as st
import ast
from core.expression_parser import parse_expression
from math_modules.finite_metric_spaces import compute_diam, compute_dist_sets, compute_distance_matrix
from ui.components import input_with_history, save_to_history_button, render_dual_value, render_distance_matrix_html
from core.formatting import format_point

def _parse_points(text: str) -> list:
    points = []
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            for p in parsed:
                res_p = []
                for c in p:
                    res_c = parse_expression(str(c))
                    if res_c.is_valid:
                        res_p.append(res_c.expr)
                if len(res_p) == len(p):
                    points.append(tuple(res_p))
            return points
        except Exception:
            pass
            
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("(") and line.endswith(")"):
            parts = line[1:-1].split(",")
            res_p = []
            for p in parts:
                res_c = parse_expression(p.strip())
                if res_c.is_valid:
                    res_p.append(res_c.expr)
            if len(res_p) == len(parts):
                points.append(tuple(res_p))
    return points

def render() -> None:
    st.header("Skończone Przestrzenie Metryczne")
    st.write("Obliczanie macierzy odległości, średnicy zbioru oraz odległości między zbiorami.")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            dim = st.number_input("Wymiar n", min_value=1, value=2, step=1)
        with col2:
            metric = st.selectbox(
                "Metryka",
                ["Euclidean", "Manhattan", "Chebyshev", "Discrete", "custom"]
            )
            
    custom_formula = ""
    if metric == "custom":
        custom_formula = input_with_history("Wzór metryki (użyj x1, y1, ...)", "custom_metrics", "custom_metric")
        save_to_history_button("custom_metrics", custom_formula, "Wzór metryki")
        
    st.subheader("Zbiór E")
    e_str = input_with_history("Punkty (format: [(0,0), ...] lub linia po linii)", "points", "points_e", default_val="[(0,0), (1,1)]")
    save_to_history_button("points", e_str, "Zbiór E")
    
    st.subheader("Zbiór F (opcjonalny do dist(E,F))")
    f_str = input_with_history("Punkty zbioru F", "points", "points_f")
    if f_str:
        save_to_history_button("points", f_str, "Zbiór F")
        
    if st.button("Oblicz", type="primary"):
        E = _parse_points(e_str)
        F = _parse_points(f_str) if f_str else []
        
        if not E:
            st.error("Nie udało się poprawnie sparsować zbioru E.")
            return
            
        st.write("### Macierz odległości D(p_i, p_j)")
        headers = [format_point(p) for p in E]
        
        if len(E) > 20:
            st.warning("Zbiór zawiera więcej niż 20 punktów, wyłączono renderowanie pełnej macierzy dla czytelności.")
        else:
            matrix = compute_distance_matrix(E, metric, custom_formula)
            render_distance_matrix_html(headers, matrix)
            
        st.write("### Średnica diam(E)")
        diam_dv, diam_pair = compute_diam(E, metric, custom_formula)
        diam_dv.notes.append(f"Zrealizowana przez parę: {headers[diam_pair[0]]} i {headers[diam_pair[1]]}")
        render_dual_value(diam_dv)
        
        if F:
            st.write("### Odległość dist(E, F)")
            f_headers = [format_point(p) for p in F]
            dist_dv, dist_pair = compute_dist_sets(E, F, metric, custom_formula)
            dist_dv.notes.append(f"Zrealizowana przez: {headers[dist_pair[0]]} ∈ E oraz {f_headers[dist_pair[1]]} ∈ F")
            render_dual_value(dist_dv)
