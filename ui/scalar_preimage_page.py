import numpy as np
import plotly.graph_objects as go
import streamlit as st
import sympy

from core.expression_parser import parse_expression
from core.formatting import latex_point
from core.history import add_or_update_history_entry
from core.safe_eval import create_numpy_func_2d
from core.set_parser import FiniteSet1D, Interval1D, parse_set_1d, set_latex
from math_modules.scalar_preimage import compute_scalar_preimage_membership
from ui.components import input_with_history, math_input, render_dual_value


def _mask_values_1d(parsed_set, values: np.ndarray, tolerance: float) -> np.ndarray:
    if isinstance(parsed_set, Interval1D):
        a_val = float(parsed_set.a.evalf())
        b_val = float(parsed_set.b.evalf())
        left = values >= a_val - tolerance if parsed_set.left_closed else values > a_val + tolerance
        right = values <= b_val + tolerance if parsed_set.right_closed else values < b_val - tolerance
        return np.asarray(left & right & np.isfinite(values), dtype=bool)
    if isinstance(parsed_set, FiniteSet1D):
        mask = np.zeros_like(values, dtype=bool)
        for elem in parsed_set.elements:
            try:
                mask |= np.abs(values - float(elem.evalf())) <= tolerance
            except Exception:
                continue
        return mask & np.isfinite(values)

    result = np.zeros_like(values, dtype=bool)
    rows, cols = values.shape
    for i in range(rows):
        for j in range(cols):
            if np.isfinite(values[i, j]):
                result[i, j] = parsed_set.contains_numeric(values[i, j])
    return result


def render() -> None:
    st.header("Przeciwobraz funkcji skalarnej")
    st.caption("Dla f : R² -> R sprawdzamy punkt i rysujemy przybliżenie f⁻¹(A) w wybranym oknie.")

    col1, col2 = st.columns(2)
    with col1:
        f_str = math_input("Funkcja f(x, y)", "functions_2d", "preimg_f", default_val="x^2 + y^2", preview_prefix_latex="f(x,y) = ")
    with col2:
        a_str = input_with_history("Zbiór A ⊆ R, np. [0, 1], (-oo, 0), {0, 1}", "sets_r", "preimg_a", default_val="[0, 1]")
        a_preview = parse_set_1d(a_str)
        if a_preview:
            st.caption("Podgląd zbioru")
            st.latex(set_latex(a_preview, "A"))

    st.subheader("Badany punkt")
    col3, col4 = st.columns(2)
    with col3:
        x0_str = math_input("x0", "points", "preimg_x0", default_val="0.5", preview=True, preview_prefix_latex="x_0 = ")
    with col4:
        y0_str = math_input("y0", "points", "preimg_y0", default_val="0.5", preview=True, preview_prefix_latex="y_0 = ")

    st.subheader("Okno rysunku")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        a = st.number_input("x min", value=-2.0)
    with col6:
        b = st.number_input("x max", value=2.0)
    with col7:
        c = st.number_input("y min", value=-2.0)
    with col8:
        d = st.number_input("y max", value=2.0)

    if st.button("Oblicz i rysuj", type="primary"):
        if a > b or c > d:
            st.error("Okno musi spełniać x min <= x max oraz y min <= y max.")
            return

        f_res = parse_expression(f_str)
        a_set = parse_set_1d(a_str)
        if not f_res.is_valid:
            st.error(f"Niepoprawna funkcja: {f_res.error}")
            return
        if not a_set:
            st.error("Niepoprawny zbiór A. Obsługiwane są przedziały i zbiory skończone w R.")
            return

        x0_res = parse_expression(x0_str)
        y0_res = parse_expression(y0_str)
        if not x0_res.is_valid or not y0_res.is_valid:
            st.error("Współrzędne punktu muszą być poprawnymi liczbami.")
            return
        try:
            x0 = float(x0_res.expr.evalf())
            y0 = float(y0_res.expr.evalf())
            if not np.isfinite(x0) or not np.isfinite(y0):
                raise ValueError
        except Exception:
            st.error("Współrzędne punktu muszą być liczbami rzeczywistymi.")
            return

        add_or_update_history_entry("functions_2d", f_str.strip(), "f(x,y)")
        add_or_update_history_entry("sets_r", a_str.strip(), "Zbiór A")
        add_or_update_history_entry("points", f"({x0_str.strip()}, {y0_str.strip()})", "Punkt")

        mem_status, dv = compute_scalar_preimage_membership(f_res.expr, a_set, (x0_res.expr, y0_res.expr))

        st.write("### Przynależność punktu")
        st.latex(latex_point((x0_res.expr, y0_res.expr)) + r" \in f^{-1}(A)?")
        if mem_status == "true":
            st.success("Tak")
        elif mem_status == "false":
            st.error("Nie")
        elif mem_status == "boundary":
            st.warning("Punkt leży numerycznie na brzegu zbioru.")
        else:
            st.warning("Nie udało się rozstrzygnąć.")

        render_dual_value(dv, "Wartość f(x0, y0)")

        st.write("### Przybliżenie przeciwobrazu")
        resolution = 420
        x_vals = np.linspace(a, b, resolution)
        y_vals = np.linspace(c, d, resolution)
        X, Y = np.meshgrid(x_vals, y_vals)

        x_sym = sympy.Symbol("x", real=True)
        y_sym = sympy.Symbol("y", real=True)
        f_num = create_numpy_func_2d(f_res.expr, x_sym, y_sym)
        Z_val = f_num(X, Y)
        tolerance = max(1e-9, max(abs(b - a), abs(d - c)) / resolution * 0.5)
        Z_bool = _mask_values_1d(a_set, Z_val, tolerance)

        finite_levels = []
        if isinstance(a_set, FiniteSet1D):
            for elem in a_set.elements:
                try:
                    finite_levels.append(float(elem.evalf()))
                except Exception:
                    pass

        if not np.any(Z_bool) and not finite_levels:
            st.info("W wybranym oknie i rozdzielczości nie znaleziono punktów przeciwobrazu.")

        fig = go.Figure()
        fig.add_trace(
            go.Contour(
                z=Z_bool.astype(float),
                x=x_vals,
                y=y_vals,
                contours=dict(start=0.5, end=1.5, size=1, coloring="fill", showlines=False),
                colorscale=[[0, "rgba(255,255,255,0)"], [1, "#9ed0e6"]],
                showscale=False,
                hoverinfo="skip",
                line_smoothing=0.85,
                name="f⁻¹(A)",
            )
        )
        if isinstance(a_set, Interval1D):
            for level in (float(a_set.a.evalf()), float(a_set.b.evalf())):
                if np.isfinite(level):
                    fig.add_trace(
                        go.Contour(
                            z=Z_val,
                            x=x_vals,
                            y=y_vals,
                            contours=dict(start=level, end=level, size=1, coloring="lines"),
                            line=dict(color="#1f5f9f", width=1.5),
                            showscale=False,
                            hoverinfo="skip",
                            name=f"f={level:g}",
                        )
                    )
        for level in finite_levels:
            fig.add_trace(
                go.Contour(
                    z=Z_val,
                    x=x_vals,
                    y=y_vals,
                    contours=dict(start=level, end=level, size=1, coloring="lines"),
                    line=dict(color="#1f5f9f", width=2),
                    showscale=False,
                    name=f"f(x,y)={level:g}",
                    hoverinfo="skip",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=[x0],
                y=[y0],
                mode="markers",
                marker=dict(color="#2f7d46" if mem_status == "true" else "#b93a32", size=12, symbol="star"),
                name="badany punkt",
            )
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="x",
            yaxis_title="y",
            height=560,
        )
        fig.update_xaxes(constrain="domain")
        fig.update_yaxes(scaleanchor="x", scaleratio=1, constrain="domain")
        st.plotly_chart(fig, use_container_width=True)
