import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.expression_parser import parse_expression
from math_modules.supremum_rectangle import compute_supremum_rectangle
from ui.components import input_with_history, save_to_history_button, render_dual_value

def render() -> None:
    st.header("Odległość Supremum na Prostokącie")
    st.write("Obliczanie odległości d∞(f, g) na prostokącie P = [a, b] × [c, d].")
    
    col1, col2 = st.columns(2)
    with col1:
        f_str = input_with_history("Funkcja f(x, y)", "functions_2d", "sup_rect_f", default_val="x^2 + y^2")
        save_to_history_button("functions_2d", f_str, "f(x, y)")
    with col2:
        g_str = input_with_history("Funkcja g(x, y)", "functions_2d", "sup_rect_g", default_val="0")
        save_to_history_button("functions_2d", g_str, "g(x, y)")
        
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        a = st.number_input("a (min x)", value=-1.0)
    with col4:
        b = st.number_input("b (max x)", value=1.0)
    with col5:
        c = st.number_input("c (min y)", value=-1.0)
    with col6:
        d = st.number_input("d (max y)", value=1.0)
        
    precision = st.slider("Precyzja wyświetlania", min_value=5, max_value=50, value=20)
    
    if st.button("Oblicz", type="primary"):
        f_res = parse_expression(f_str)
        g_res = parse_expression(g_str)
        
        if not f_res.is_valid or not g_res.is_valid:
            st.error("Błąd w składni funkcji.")
            return
            
        dv, maximizers, f_num, g_num, h_num = compute_supremum_rectangle(
            f_res.expr, g_res.expr, (float(a), float(b)), (float(c), float(d)), precision=precision
        )
        
        render_dual_value(dv, "Odległość d∞(f, g)")
        
        st.write("### Wizualizacja (Mapa Ciepła |f - g|)")
        x_vals = np.linspace(a, b, 100)
        y_vals = np.linspace(c, d, 100)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = h_num(X.flatten(), Y.flatten()).reshape(X.shape)
        
        fig = go.Figure(data=go.Contour(z=Z, x=x_vals, y=y_vals, colorscale="Viridis", contours=dict(showlabels=True)))
        
        for pt in maximizers:
            fig.add_trace(go.Scatter(
                x=[pt[0]], y=[pt[1]], mode='markers', marker=dict(color='red', size=12, symbol='x'),
                name=f'Maksimum ({pt[0]:.2f}, {pt[1]:.2f})'
            ))
            
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
