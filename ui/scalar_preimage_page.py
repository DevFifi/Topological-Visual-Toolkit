import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.expression_parser import parse_expression
from core.set_parser import parse_set_1d
from math_modules.scalar_preimage import compute_scalar_preimage_membership
from ui.components import input_with_history, save_to_history_button, render_dual_value
from core.safe_eval import create_numpy_func_2d
import sympy

def render() -> None:
    st.header("Przeciwobraz Funkcji Skalarnej")
    st.write("Wizualizacja przeciwobrazu f^{-1}(A) oraz sprawdzanie przynależności punktu.")
    
    col1, col2 = st.columns(2)
    with col1:
        f_str = input_with_history("Funkcja f(x, y)", "functions_2d", "preimg_f", default_val="(x^2+y^2-1)^3 - x^2*y^3")
        save_to_history_button("functions_2d", f_str, "f(x, y)")
    with col2:
        a_str = input_with_history("Zbiór A ⊆ R (np. [0, 1])", "sets_r", "preimg_a", default_val="(-oo, 0)")
        save_to_history_button("sets_r", a_str, "Zbiór A")
        
    st.subheader("Sprawdzenie punktu (x0, y0)")
    col3, col4 = st.columns(2)
    with col3:
        x0_str = st.text_input("x0", value="0.5")
    with col4:
        y0_str = st.text_input("y0", value="0.5")
        
    st.subheader("Ustawienia Widoku")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        a = st.number_input("x min", value=-2.0)
    with col6:
        b = st.number_input("x max", value=2.0)
    with col7:
        c = st.number_input("y min", value=-2.0)
    with col8:
        d = st.number_input("y max", value=2.0)
        
    if st.button("Oblicz i Rysuj", type="primary"):
        f_res = parse_expression(f_str)
        a_set = parse_set_1d(a_str)
        
        if not f_res.is_valid:
            st.error("Błąd w składni funkcji.")
            return
        if not a_set:
            st.error("Błąd w składni zbioru A.")
            return
            
        try:
            x0 = float(parse_expression(x0_str).expr.evalf())
            y0 = float(parse_expression(y0_str).expr.evalf())
        except Exception:
            st.error("Błąd w składni punktu.")
            return
            
        mem_status, dv = compute_scalar_preimage_membership(f_res.expr, a_set, (x0, y0))
        
        st.write("### Przynależność punktu")
        st.write(f"Czy ({x0}, {y0}) ∈ f^{{-1}}({a_str})?")
        if mem_status == "true":
            st.success("TAK")
        elif mem_status == "false":
            st.error("NIE")
        else:
            st.warning("NIEPEWNE (blisko brzegu)")
            
        render_dual_value(dv, "Wartość f(x0, y0)")
        
        st.write("### Wizualizacja przeciwobrazu")
        x_vals = np.linspace(a, b, 200)
        y_vals = np.linspace(c, d, 200)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        x_sym = sympy.Symbol("x", real=True)
        y_sym = sympy.Symbol("y", real=True)
        f_num = create_numpy_func_2d(f_res.expr, x_sym, y_sym)
        
        Z_val = f_num(X, Y)
        Z_bool = np.zeros_like(Z_val, dtype=bool)
        
        for i in range(Z_val.shape[0]):
            for j in range(Z_val.shape[1]):
                Z_bool[i, j] = a_set.contains_numeric(Z_val[i, j])
                
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=Z_bool.astype(int),
            x=x_vals,
            y=y_vals,
            colorscale=[[0, 'white'], [1, 'lightblue']],
            showscale=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=[x0], y=[y0], mode='markers',
            marker=dict(color='red' if mem_status == "false" else 'green', size=12, symbol='star'),
            name='Badany punkt'
        ))
        
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20), xaxis_title="x", yaxis_title="y")
        st.plotly_chart(fig, use_container_width=True)
