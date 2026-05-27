import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.expression_parser import parse_expression
from math_modules.supremum_interval import compute_supremum_interval
from ui.components import input_with_history, save_to_history_button, render_dual_value

def render() -> None:
    st.header("Odległość Supremum na Przedziale")
    st.write("Obliczanie odległości d∞(f, g) na przedziale domkniętym [a, b].")
    
    col1, col2 = st.columns(2)
    with col1:
        f_str = input_with_history("Funkcja f(x)", "functions_1d", "sup_int_f", default_val="x^2")
        save_to_history_button("functions_1d", f_str, "f(x)")
    with col2:
        g_str = input_with_history("Funkcja g(x)", "functions_1d", "sup_int_g", default_val="x")
        save_to_history_button("functions_1d", g_str, "g(x)")
        
    col3, col4 = st.columns(2)
    with col3:
        a = st.number_input("Początek przedziału a", value=0.0)
    with col4:
        b = st.number_input("Koniec przedziału b", value=1.0)
        
    precision = st.slider("Precyzja wyświetlania", min_value=5, max_value=50, value=20)
    
    if st.button("Oblicz", type="primary"):
        f_res = parse_expression(f_str)
        g_res = parse_expression(g_str)
        
        if not f_res.is_valid or not g_res.is_valid:
            st.error("Błąd w składni funkcji.")
            return
            
        dv, maximizers, f_num, g_num, h_num = compute_supremum_interval(
            f_res.expr, g_res.expr, float(a), float(b), precision=precision
        )
        
        render_dual_value(dv, "Odległość d∞(f, g)")
        
        st.write("### Wizualizacja")
        x_vals = np.linspace(a, b, 500)
        y_f = f_num(x_vals)
        y_g = g_num(x_vals)
        y_h = h_num(x_vals)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_f, mode='lines', name='f(x)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=x_vals, y=y_g, mode='lines', name='g(x)', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=x_vals, y=y_h, mode='lines', name='|f(x) - g(x)|', line=dict(color='green', dash='dash')))
        
        if dv.numeric:
            dist_val = float(dv.numeric)
            fig.add_hline(y=dist_val, line_dash="dot", line_color="orange", annotation_text="d∞")
            
        for mx in maximizers:
            my = h_num(np.array([mx]))[0]
            fig.add_trace(go.Scatter(
                x=[mx], y=[my], mode='markers', marker=dict(color='orange', size=10, symbol='star'),
                name=f'Maksimum x≈{mx:.4f}'
            ))
            
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
