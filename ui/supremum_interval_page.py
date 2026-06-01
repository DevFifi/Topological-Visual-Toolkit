import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core.expression_parser import parse_expression
from core.history import add_or_update_history_entry
from math_modules.supremum_interval import compute_supremum_interval
from ui.components import math_input, render_dual_value


def render() -> None:
    st.header("Odległość supremum na przedziale")
    st.caption("Dla funkcji ciągłych f,g : [a,b] -> R liczymy d∞(f,g)=sup |f(x)-g(x)|.")

    col1, col2 = st.columns(2)
    with col1:
        f_str = math_input("Funkcja f(x)", "supremum_interval_functions", "sup_int_f", default_val="x^2", preview_prefix_latex="f(x) = ")
    with col2:
        g_str = math_input("Funkcja g(x)", "supremum_interval_functions", "sup_int_g", default_val="x", preview_prefix_latex="g(x) = ")

    col3, col4, col5 = st.columns([1, 1, 1])
    with col3:
        a = st.number_input("Początek przedziału a", value=0.0)
    with col4:
        b = st.number_input("Koniec przedziału b", value=1.0)
    with col5:
        precision = st.slider("Cyfry wyświetlania", min_value=5, max_value=50, value=20)

    if st.button("Oblicz", type="primary"):
        if a > b:
            st.error("Przedział musi spełniać a <= b.")
            return

        f_res = parse_expression(f_str)
        g_res = parse_expression(g_str)
        if not f_res.is_valid:
            st.error(f"Niepoprawna funkcja f: {f_res.error}")
            return
        if not g_res.is_valid:
            st.error(f"Niepoprawna funkcja g: {g_res.error}")
            return

        add_or_update_history_entry("supremum_interval_functions", f_str.strip())
        add_or_update_history_entry("supremum_interval_functions", g_str.strip())

        dv, maximizers, f_num, g_num, h_num = compute_supremum_interval(
            f_res.expr,
            g_res.expr,
            float(a),
            float(b),
            precision=precision,
        )

        render_dual_value(dv, "Odległość d∞(f, g)")
        if dv.status == "error":
            return

        st.write("### Wykres")
        x_vals = np.linspace(a, b, 600)
        y_f = f_num(x_vals)
        y_g = g_num(x_vals)
        y_h = h_num(x_vals)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_f, mode="lines", name="f(x)", line=dict(color="#1f5f9f")))
        fig.add_trace(go.Scatter(x=x_vals, y=y_g, mode="lines", name="g(x)", line=dict(color="#b93a32")))
        fig.add_trace(go.Scatter(x=x_vals, y=y_h, mode="lines", name="|f(x)-g(x)|", line=dict(color="#2f7d46", dash="dash")))

        if dv.numeric:
            dist_val = float(dv.numeric)
            fig.add_hline(y=dist_val, line_dash="dot", line_color="#cc7a00", annotation_text="d∞")

        for mx in maximizers:
            my = h_num(np.array([mx], dtype=float))[0]
            if np.isfinite(my):
                fig.add_trace(
                    go.Scatter(
                        x=[mx],
                        y=[my],
                        mode="markers",
                        marker=dict(color="#cc7a00", size=10, symbol="star"),
                        name=f"maksimum x≈{mx:.4g}",
                    )
                )

        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20), xaxis_title="x")
        st.plotly_chart(fig, use_container_width=True)
