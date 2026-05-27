import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.expression_parser import parse_expression
from core.set_parser import parse_set_2d
from math_modules.vector_mapping_images import compute_preimage_grid, compute_image_points
from ui.components import input_with_history, save_to_history_button

def render() -> None:
    st.header("Odwzorowania Wektorowe: Obraz i Przeciwobraz")
    st.write("Wizualizacja przeciwobrazu Φ^{-1}(B) oraz obrazu Φ(C).")
    
    col1, col2 = st.columns(2)
    with col1:
        phi1_str = input_with_history("Φ_1(x, y)", "functions_2d", "vec_phi1", default_val="x")
        save_to_history_button("functions_2d", phi1_str, "Φ_1")
    with col2:
        phi2_str = input_with_history("Φ_2(x, y)", "functions_2d", "vec_phi2", default_val="y")
        save_to_history_button("functions_2d", phi2_str, "Φ_2")
        
    st.subheader("Zbiory")
    col3, col4 = st.columns(2)
    with col3:
        c_str = input_with_history("Zbiór C ⊆ R² (do obrazu)", "sets_r2", "vec_c", default_val="(x^2+y^2-1)^3 - x^2*y^3 < 0")
        save_to_history_button("sets_r2", c_str, "Zbiór C")
    with col4:
        b_str = input_with_history("Zbiór B ⊆ R² (do przeciwobrazu)", "sets_r2", "vec_b", default_val="(x^2+y^2-1)^3 - x^2*y^3 < 0")
        save_to_history_button("sets_r2", b_str, "Zbiór B")
        
    st.subheader("Ustawienia Widoku Źródłowego (x, y)")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        a = st.number_input("x min", value=-2.0, key="va")
    with col6:
        b = st.number_input("x max", value=2.0, key="vb")
    with col7:
        c = st.number_input("y min", value=-2.0, key="vc")
    with col8:
        d = st.number_input("y max", value=2.0, key="vd")
        
    if st.button("Oblicz i Rysuj", type="primary"):
        phi1_res = parse_expression(phi1_str)
        phi2_res = parse_expression(phi2_str)
        c_set = parse_set_2d(c_str)
        b_set = parse_set_2d(b_str)
        
        if not phi1_res.is_valid or not phi2_res.is_valid:
            st.error("Błąd w składni funkcji.")
            return
            
        source_bounds = ((float(a), float(b)), (float(c), float(d)))
        
        plot_col1, plot_col2 = st.columns(2)
        
        if c_set:
            u_list, v_list = compute_image_points(phi1_res.expr, phi2_res.expr, c_set, source_bounds, resolution=180)
            with plot_col1:
                st.write("### Obraz Φ(C)")
                fig_img = go.Figure(data=go.Scattergl(
                    x=u_list, y=v_list, 
                    mode='markers', 
                    marker=dict(color='blue', size=4, symbol='square'),
                    hoverinfo='skip'
                ))
                fig_img.update_layout(template="plotly_white", xaxis_title="u", yaxis_title="v", height=400)
                st.plotly_chart(fig_img, use_container_width=True)
        else:
            with plot_col1:
                st.error("Błąd w składni zbioru C lub puste wejście.")
                
        if b_set:
            X, Y, Z_bool = compute_preimage_grid(phi1_res.expr, phi2_res.expr, b_set, source_bounds, resolution=150)
            with plot_col2:
                st.write("### Przeciwobraz Φ^{-1}(B)")
                fig_pre = go.Figure()
                fig_pre.add_trace(go.Heatmap(
                    z=Z_bool.astype(int),
                    x=X[0,:],
                    y=Y[:,0],
                    colorscale=[[0, 'white'], [1, 'lightgreen']],
                    showscale=False,
                    hoverinfo='skip'
                ))
                fig_pre.update_layout(template="plotly_white", xaxis_title="x", yaxis_title="y", height=400)
                st.plotly_chart(fig_pre, use_container_width=True)
        else:
            with plot_col2:
                st.error("Błąd w składni zbioru B lub puste wejście.")
