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

    if st.button("Animacja ewolucji (od 1 do n)", type="secondary"):
        f_res = parse_expression(f_str)
        if not f_res.is_valid:
            st.error("Błąd w składni funkcji.")
            return
            
        x_vals = np.linspace(0, 1, 300)
        x = sympy.Symbol("x", real=True)
        f_num = create_numpy_func_1d(f_res.expr, x)
        y_f = f_num(x_vals)
        
        y_min, y_max = np.nanmin(y_f), np.nanmax(y_f)
        padding = (y_max - y_min) * 0.3 if y_max != y_min else 1.0
        
        frames = []
        max_n = max(2, min(n, 100)) # Ograniczenie dla wydajności przeglądarki
        
        progress = st.progress(0, text="Generowanie klatek animacji...")
        for i in range(1, max_n + 1):
            _, b_num_i = compute_bernstein_polynomial(f_res.expr, i)
            y_b_i = b_num_i(x_vals)
            frames.append(go.Frame(data=[go.Scatter(x=x_vals, y=y_b_i)], name=str(i), traces=[1]))
            progress.progress(i / max_n, text=f"Generowanie klatki {i}/{max_n}...")
            
        progress.empty()

        fig_anim = go.Figure(
            data=[
                go.Scatter(x=x_vals, y=y_f, mode='lines', name='f(x)', line=dict(color='blue')),
                go.Scatter(x=x_vals, y=frames[0].data[0].y, mode='lines', name='B_n(f)(x)', line=dict(color='red'))
            ],
            layout=go.Layout(
                template="plotly_white",
                title="Ewolucja wielomianu Bernsteina",
                yaxis=dict(range=[y_min - padding, y_max + padding]),
                updatemenus=[dict(
                    type="buttons",
                    showactive=False,
                    y=-0.15,
                    x=0.05,
                    xanchor="right",
                    yanchor="top",
                    buttons=[
                        dict(label="Odtwarzaj",
                             method="animate",
                             args=[None, {"frame": {"duration": 250, "redraw": False},
                                          "fromcurrent": True, "transition": {"duration": 150}}]),
                        dict(label="Pauza",
                             method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": False},
                                            "mode": "immediate",
                                            "transition": {"duration": 0}}])
                    ]
                )],
                sliders=[dict(
                    active=0,
                    yanchor="top",
                    xanchor="left",
                    currentvalue=dict(font=dict(size=14), prefix="n = ", visible=True, xanchor="right"),
                    transition=dict(duration=150, easing="cubic-in-out"),
                    pad=dict(b=10, t=50),
                    len=0.9,
                    x=0.1,
                    y=-0.15,
                    steps=[dict(
                        method="animate",
                        args=[[str(i)], dict(mode="immediate", frame=dict(duration=250, redraw=False), transition=dict(duration=150))],
                        label=str(i)
                    ) for i in range(1, max_n + 1)]
                )]
            ),
            frames=frames
        )
        
        st.plotly_chart(fig_anim, use_container_width=True)
