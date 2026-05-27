import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.expression_parser import parse_expression
from math_modules.bernstein_approximation import compute_bernstein_polynomial, compute_bernstein_error
from ui.components import input_with_history, save_to_history_button, render_dual_value
from core.safe_eval import create_numpy_func_1d
import sympy

def render() -> None:
    st.header("Aproksymacja Bernsteina")
    st.write("Wizualizacja aproksymacji funkcji f na [0, 1] przez wielomiany Bernsteina B_n(f).")
    
    f_str = input_with_history("Funkcja f(x)", "functions_1d", "bernstein_f", default_val="x^2")
    save_to_history_button("functions_1d", f_str, "f(x)")
    
    col1, col2 = st.columns(2)
    with col1:
        n = st.number_input("Stopień wielomianu n", min_value=1, value=10, step=1)
    with col2:
        precision = st.slider("Precyzja wyświetlania błędu", min_value=5, max_value=50, value=20)
        
    if st.button("Oblicz i Rysuj", type="primary"):
        f_res = parse_expression(f_str)
        if not f_res.is_valid:
            st.error("Błąd w składni funkcji.")
            return
            
        exact_b_n, b_num = compute_bernstein_polynomial(f_res.expr, n)
        
        st.write("### Wielomian Bernsteina")
        if exact_b_n is not None:
            st.latex(f"B_{{{n}}}(f)(x) = " + sympy.latex(exact_b_n))
        else:
            st.info("Dokładna postać symboliczna zbyt złożona, użyto metody numerycznej.")
            
        err_dv = compute_bernstein_error(f_res.expr, exact_b_n, b_num, n, precision)
        render_dual_value(err_dv, f"Błąd d∞(f, B_{n}(f))")
        
        st.write("### Wizualizacja")
        x_vals = np.linspace(0, 1, 500)
        x = sympy.Symbol("x", real=True)
        f_num = create_numpy_func_1d(f_res.expr, x)
        
        y_f = f_num(x_vals)
        y_b = b_num(x_vals)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_f, mode='lines', name='f(x)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=x_vals, y=y_b, mode='lines', name=f'B_{n}(f)(x)', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=x_vals, y=np.abs(y_f - y_b), mode='lines', name='|Błąd|', line=dict(color='green', dash='dot')))
        
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
