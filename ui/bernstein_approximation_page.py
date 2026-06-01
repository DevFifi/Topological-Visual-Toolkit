import numpy as np
import plotly.graph_objects as go
import streamlit as st
import sympy

from core.expression_parser import parse_expression
from core.history import add_or_update_history_entry
from core.safe_eval import create_numpy_func_1d
from math_modules.bernstein_approximation import bernstein_partial_latex, compute_bernstein_error, compute_bernstein_polynomial
from ui.components import math_input, render_dual_value


def _animation_degrees(target_n: int, max_frames: int) -> list[int]:
    target_n = int(target_n)
    max_frames = max(1, int(max_frames))
    if target_n <= max_frames:
        return list(range(1, target_n + 1))

    values = np.linspace(1, target_n, max_frames)
    degrees = sorted({max(1, min(target_n, int(round(value)))) for value in values})
    if degrees[0] != 1:
        degrees.insert(0, 1)
    if degrees[-1] != target_n:
        degrees.append(target_n)
    return degrees


def render() -> None:
    st.header("Aproksymacja Bernsteina")
    st.caption("Porównanie funkcji f : [0,1] -> R z wielomianem Bernsteina B_n(f).")

    f_str = math_input("Funkcja f(x)", "bernstein_functions", "bernstein_f", default_val="x^2", preview_prefix_latex="f(x) = ")

    col1, col2, col3 = st.columns(3)
    with col1:
        n = st.number_input("Stopień n", min_value=1, value=10, step=1)
    with col2:
        precision = st.slider("Cyfry wyświetlania błędu", min_value=5, max_value=50, value=20)

    with col3:
        max_animation_frames = st.slider(
            "Maks. klatek animacji",
            min_value=50,
            max_value=600,
            value=240,
            step=10,
            help="Dla n większego od tej wartości animacja pokazuje stopnie równomiernie rozłożone od 1 do n.",
        )

    if st.button("Oblicz i rysuj", type="primary"):
        f_res = parse_expression(f_str)
        if not f_res.is_valid:
            st.error(f"Niepoprawna funkcja: {f_res.error}")
            return

        add_or_update_history_entry("bernstein_functions", f_str.strip())
        exact_b_n, b_num = compute_bernstein_polynomial(f_res.expr, int(n))

        st.write("### Wielomian Bernsteina")
        if exact_b_n is not None:
            st.latex(f"B_{{{int(n)}}}(f)(x) = " + sympy.latex(exact_b_n))
        else:
            st.info("Postać symboliczna jest zbyt duża; wykres i błąd liczone są numerycznie.")
            st.latex(f"B_{{{int(n)}}}(f)(x) = " + bernstein_partial_latex(f_res.expr, int(n)))
            if int(n) > 5000:
                st.warning("Bardzo duże n może wyraźnie wydłużyć obliczenia, bo dla ogólnej funkcji trzeba uwzględnić wartości f(k/n).")

        err_dv = compute_bernstein_error(f_res.expr, exact_b_n, b_num, int(n), precision)
        render_dual_value(err_dv, f"Błąd d∞(f, B_{int(n)}(f))")
        if err_dv.status == "error":
            return

        st.write("### Wykres")
        x_vals = np.linspace(0.0, 1.0, 700)
        x = sympy.Symbol("x", real=True)
        f_num = create_numpy_func_1d(f_res.expr, x)
        y_f = f_num(x_vals)
        y_b = b_num(x_vals)
        y_err = np.abs(y_f - y_b)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_f, mode="lines", name="f(x)", line=dict(color="#1f5f9f")))
        fig.add_trace(go.Scatter(x=x_vals, y=y_b, mode="lines", name=f"B_{int(n)}(f)(x)", line=dict(color="#b93a32")))
        fig.add_trace(go.Scatter(x=x_vals, y=y_err, mode="lines", name="|błąd|", line=dict(color="#2f7d46", dash="dot")))
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20), xaxis_title="x")
        st.plotly_chart(fig, use_container_width=True)

    if st.button("Animacja dla kolejnych n", type="secondary"):
        f_res = parse_expression(f_str)
        if not f_res.is_valid:
            st.error(f"Niepoprawna funkcja: {f_res.error}")
            return

        degrees = _animation_degrees(int(n), int(max_animation_frames))
        x_vals = np.linspace(0.0, 1.0, 350)
        x = sympy.Symbol("x", real=True)
        f_num = create_numpy_func_1d(f_res.expr, x)
        y_f = f_num(x_vals)
        valid = np.isfinite(y_f)
        if not np.any(valid):
            st.error("Funkcja nie ma skończonych wartości na [0,1].")
            return

        y_min, y_max = np.nanmin(y_f), np.nanmax(y_f)
        padding = (y_max - y_min) * 0.25 if y_max != y_min else 1.0

        frames = []
        progress = st.progress(0, text="Generowanie animacji...")
        total_frames = len(degrees)
        for frame_idx, degree in enumerate(degrees, start=1):
            _, b_num_i = compute_bernstein_polynomial(f_res.expr, degree)
            y_b_i = b_num_i(x_vals)
            frames.append(go.Frame(data=[go.Scatter(x=x_vals, y=y_b_i)], name=str(degree), traces=[1]))
            progress.progress(frame_idx / total_frames, text=f"Klatka {frame_idx}/{total_frames} (n = {degree})")
        progress.empty()

        fig_anim = go.Figure(
            data=[
                go.Scatter(x=x_vals, y=y_f, mode="lines", name="f(x)", line=dict(color="#1f5f9f")),
                go.Scatter(x=x_vals, y=frames[0].data[0].y, mode="lines", name="B_n(f)(x)", line=dict(color="#b93a32")),
            ],
            layout=go.Layout(
                template="plotly_white",
                title="Zmiana wielomianu Bernsteina przy wzroście n",
                yaxis=dict(range=[y_min - padding, y_max + padding]),
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        y=-0.15,
                        x=0.05,
                        xanchor="right",
                        yanchor="top",
                        buttons=[
                            dict(
                                label="Odtwarzaj",
                                method="animate",
                                args=[None, {"frame": {"duration": 250, "redraw": False}, "fromcurrent": True}],
                            ),
                            dict(
                                label="Pauza",
                                method="animate",
                                args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                            ),
                        ],
                    )
                ],
                sliders=[
                    dict(
                        active=0,
                        currentvalue=dict(prefix="n = "),
                        steps=[
                            dict(
                                method="animate",
                                args=[[str(degree)], dict(mode="immediate", frame=dict(duration=250, redraw=False))],
                                label=str(degree),
                            )
                            for degree in degrees
                        ],
                    )
                ],
            ),
            frames=frames,
        )

        st.plotly_chart(fig_anim, use_container_width=True)
        if int(n) > len(degrees):
            step_hint = max(1, int(round(int(n) / max(1, len(degrees) - 1))))
            st.caption(
                f"Animacja pokazuje {len(degrees)} klatek od n=1 do n={int(n)}; "
                f"dla dużego n dobrano stopnie co około {step_hint}, z zachowaniem ostatniej klatki."
            )
