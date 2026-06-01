import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core.expression_parser import parse_expression
from core.history import add_or_update_history_entry
from math_modules.supremum_rectangle import compute_supremum_rectangle
from ui.components import math_input, render_dual_value


def render() -> None:
    st.header("Odległość supremum na prostokącie")
    st.caption("Dla funkcji ciągłych f,g : P -> R liczymy przybliżenie d∞(f,g)=sup |f(x,y)-g(x,y)|.")

    col1, col2 = st.columns(2)
    with col1:
        f_str = math_input("Funkcja f(x, y)", "functions_2d", "sup_rect_f", default_val="x^2 + y^2", preview_prefix_latex="f(x,y) = ")
    with col2:
        g_str = math_input("Funkcja g(x, y)", "functions_2d", "sup_rect_g", default_val="0", preview_prefix_latex="g(x,y) = ")

    col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1])
    with col3:
        a = st.number_input("x min", value=-1.0)
    with col4:
        b = st.number_input("x max", value=1.0)
    with col5:
        c = st.number_input("y min", value=-1.0)
    with col6:
        d = st.number_input("y max", value=1.0)
    with col7:
        precision = st.slider("Cyfry", min_value=5, max_value=50, value=20)

    if st.button("Oblicz", type="primary"):
        if a > b or c > d:
            st.error("Prostokąt musi spełniać x min <= x max oraz y min <= y max.")
            return

        f_res = parse_expression(f_str)
        g_res = parse_expression(g_str)
        if not f_res.is_valid:
            st.error(f"Niepoprawna funkcja f: {f_res.error}")
            return
        if not g_res.is_valid:
            st.error(f"Niepoprawna funkcja g: {g_res.error}")
            return

        add_or_update_history_entry("functions_2d", f_str.strip(), "f(x,y)")
        add_or_update_history_entry("functions_2d", g_str.strip(), "g(x,y)")

        dv, maximizers, f_num, g_num, h_num = compute_supremum_rectangle(
            f_res.expr,
            g_res.expr,
            (float(a), float(b)),
            (float(c), float(d)),
            precision=precision,
        )

        render_dual_value(dv, "Odległość d∞(f, g)")
        if dv.status == "error":
            return

        st.write("### Mapa wartości |f-g|")
        x_vals = np.linspace(a, b, 140)
        y_vals = np.linspace(c, d, 140)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = h_num(X.flatten(), Y.flatten()).reshape(X.shape)

        fig = go.Figure(data=go.Contour(z=Z, x=x_vals, y=y_vals, colorscale="Viridis", contours=dict(showlabels=True)))
        for pt in maximizers:
            fig.add_trace(
                go.Scatter(
                    x=[pt[0]],
                    y=[pt[1]],
                    mode="markers",
                    marker=dict(color="#b93a32", size=12, symbol="x"),
                    name=f"maksimum ({pt[0]:.3g}, {pt[1]:.3g})",
                )
            )

        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20), xaxis_title="x", yaxis_title="y")
        st.plotly_chart(fig, use_container_width=True)
