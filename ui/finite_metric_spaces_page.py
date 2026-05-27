import streamlit as st
import ast
from typing import List, Optional
from core.expression_parser import parse_expression
from math_modules.finite_metric_spaces import compute_diam, compute_dist_sets, compute_distance_matrix, _get_distance_formula, compute_distance
from ui.components import input_with_history, save_to_history_button, render_dual_value, render_distance_matrix_html
from core.formatting import format_point

def _parse_points(text: str, dim: int) -> list:
    points = []
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            if not isinstance(parsed, list):
                parsed = [parsed]
            for p in parsed:
                if isinstance(p, (int, float)):
                    p = (p,)
                elif not isinstance(p, (tuple, list)):
                    continue
                res_p = []
                for c in p:
                    res_c = parse_expression(str(c))
                    if res_c.is_valid:
                        res_p.append(res_c.expr)
                if len(res_p) >= dim:
                    points.append(tuple(res_p[:dim]))
            if points:
                return points
        except Exception:
            pass
            
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if dim == 1 and not (line.startswith("(") and line.endswith(")")):
            res_c = parse_expression(line)
            if res_c.is_valid:
                points.append((res_c.expr,))
            continue
        if line.startswith("(") and line.endswith(")"):
            parts = line[1:-1].split(",")
            res_p = []
            for p in parts:
                res_c = parse_expression(p.strip())
                if res_c.is_valid:
                    res_p.append(res_c.expr)
            if len(res_p) >= dim:
                points.append(tuple(res_p[:dim]))
    return points

def render() -> None:
    st.header("Skończone Przestrzenie Metryczne")
    st.write("Obliczanie macierzy odległości, średnicy zbioru oraz odległości między zbiorami.")
    
    if "metric_dim" not in st.session_state:
        st.session_state.metric_dim = 2
        
    old_dim = st.session_state.metric_dim
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            new_dim = st.number_input("Wymiar n", min_value=1, value=old_dim, step=1)
            dim = old_dim
            if new_dim != old_dim:
                if new_dim < old_dim:
                    st.warning(f"Zmiana wymiaru z {old_dim} na {new_dim} obetnie punkty w zbiorach. Zatwierdź zmianę.")
                    if st.button("Zatwierdź zmianę wymiaru"):
                        if "points_e_input" in st.session_state:
                            parsed_e = _parse_points(st.session_state["points_e_input"], old_dim)
                            if parsed_e:
                                st.session_state["points_e_input"] = "\n".join(format_point(tuple(p[:new_dim])) for p in parsed_e)
                        if "points_f_input" in st.session_state and st.session_state["points_f_input"]:
                            parsed_f = _parse_points(st.session_state["points_f_input"], old_dim)
                            if parsed_f:
                                st.session_state["points_f_input"] = "\n".join(format_point(tuple(p[:new_dim])) for p in parsed_f)
                                
                        st.session_state.metric_dim = new_dim
                        dim = new_dim
                else:
                    st.session_state.metric_dim = new_dim
                    dim = new_dim
        
        with col2:
            metric = st.selectbox(
                "Metryka",
                ["Euclidean", "Manhattan", "Chebyshev", "Discrete", "Minkowski", "custom"]
            )
            
    custom_formula = ""
    if metric == "custom":
        st.write(f"Wzór metryki [ x = (x1, ..., x{dim}), y = (y1, ..., y{dim}) ]")
        st.write("Skrót: `SUM(expr)` zostanie rozwinięty jako suma po `xi` oraz `yi` od i=1 do n.")
        colA, colB = st.columns([1, 10])
        with colA:
            st.markdown("<div style='margin-top: 30px; font-size: 18px;'><b>d(x,y) =</b></div>", unsafe_allow_html=True)
        with colB:
            custom_formula = input_with_history("Wzór metryki (np. SUM((xi-yi)^2))", "custom_metrics", "custom_metric")
            
        if custom_formula:
            f, st_status = _get_distance_formula("custom", custom_formula, dim)
            if st_status == "error":
                st.error("Błąd parsowania wzoru metryki.")
            else:
                from math_modules.metric_validation import validate_metric_heuristically
                is_valid, msg = validate_metric_heuristically(f, "custom", dim)
                if is_valid:
                    st.success(msg)
                else:
                    st.error(msg)
            save_to_history_button("custom_metrics", custom_formula, "Wzór metryki")
    elif metric == "Minkowski":
        custom_formula = st.text_input("Parametr p", value="2")
        try:
            val = float(custom_formula)
            if val <= 0:
                st.error("Parametr p musi być większy od 0.")
        except Exception:
            st.error("Parametr p musi być liczbą.")
            
    st.subheader("Zbiór E")
    e_str = input_with_history("Punkty zbioru E", "points", "points_e", default_val="[(0,0), (1,1)]" if dim==2 else "[1, 2]", multiline=True)
    save_to_history_button("points", e_str, "Zbiór E")
    
    st.subheader("Zbiór F (opcjonalny do dist(E,F))")
    f_str = input_with_history("Punkty zbioru F", "points", "points_f", multiline=True)
    if f_str:
        save_to_history_button("points", f_str, "Zbiór F")
        
    if st.button("Oblicz", type="primary"):
        E = _parse_points(e_str, dim)
        F = _parse_points(f_str, dim) if f_str else []
        
        if not E:
            st.error("Nie udało się poprawnie sparsować zbioru E. Upewnij się, że ma wymiar zgodny z 'n'.")
            return
            
        st.write("### Macierz odległości D(e_i, e_j)")
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
            st.write("### Macierz odległości E x F")
            f_headers = [format_point(p) for p in F]
            if len(E) * len(F) > 400:
                st.warning("Macierz E x F jest zbyt duża do wyświetlenia.")
            else:
                formula, _ = _get_distance_formula(metric, custom_formula, dim)
                matrix_ef = []
                for p1 in E:
                    row = []
                    for p2 in F:
                        row.append(compute_distance(p1, p2, formula, metric))
                    matrix_ef.append(row)
                render_distance_matrix_html(f_headers, matrix_ef, row_headers=headers)
                
            st.write("### Odległość dist(E, F)")
            dist_dv, dist_pair = compute_dist_sets(E, F, metric, custom_formula)
            dist_dv.notes.append(f"Zrealizowana przez: {headers[dist_pair[0]]} ∈ E oraz {f_headers[dist_pair[1]]} ∈ F")
            render_dual_value(dist_dv)
