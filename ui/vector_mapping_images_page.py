import numpy as np
import plotly.graph_objects as go
import streamlit as st
import sympy

from core.expression_parser import parse_expression
from core.history import add_or_update_history_entry
from core.set_parser import CompositeSet, Relation2D, parse_set_2d, set_latex
from math_modules.vector_mapping_images import (
    compute_image_points,
    compute_preimage_grid,
    compute_preimage_relation_grid,
    sample_relation_grid,
    sample_set_grid,
)
from ui.components import input_with_history, math_input


def _is_identity_mapping(phi1_expr, phi2_expr) -> bool:
    x = sympy.Symbol("x", real=True)
    y = sympy.Symbol("y", real=True)
    try:
        return sympy.simplify(phi1_expr - x) == 0 and sympy.simplify(phi2_expr - y) == 0
    except Exception:
        return False


def _add_relation_region(
    fig: go.Figure,
    x_vals,
    y_vals,
    z_values,
    operator: str,
    color: str,
    name: str,
) -> bool:
    z = np.asarray(z_values, dtype=float)
    finite = z[np.isfinite(z)]
    if finite.size == 0:
        return False

    z_min = float(np.nanmin(finite))
    z_max = float(np.nanmax(finite))
    added = False

    if operator == "<":
        inside = z < 0
    elif operator == "<=":
        inside = z <= 0
    elif operator == ">":
        inside = z > 0
    elif operator == ">=":
        inside = z >= 0
    elif operator == "!=":
        inside = np.abs(z) > 1e-12
    else:
        inside = np.abs(z) <= 1e-12
    inside = inside & np.isfinite(z)

    if operator != "==" and np.any(inside):
        fig.add_trace(
            go.Contour(
                z=inside.astype(float),
                x=x_vals,
                y=y_vals,
                contours=dict(start=0.5, end=1.5, size=1, coloring="fill", showlines=False),
                colorscale=[[0, "rgba(255,255,255,0)"], [1, color]],
                opacity=0.52,
                showscale=False,
                hoverinfo="skip",
                name=name,
            )
        )
        added = True

    if z_min <= 0 <= z_max:
        _add_relation_boundary(fig, x_vals, y_vals, z, operator, color, f"brzeg {name}")
        added = True

    return added


def _add_relation_boundary(
    fig: go.Figure,
    x_vals,
    y_vals,
    z_values,
    operator: str,
    color: str,
    name: str,
) -> bool:
    z = np.asarray(z_values, dtype=float)
    finite = z[np.isfinite(z)]
    if finite.size == 0:
        return False
    if not (float(np.nanmin(finite)) <= 0 <= float(np.nanmax(finite))):
        return False

    fig.add_trace(
        go.Contour(
            z=z,
            x=x_vals,
            y=y_vals,
            contours=dict(start=0, end=0, size=1, coloring="lines"),
            colorscale=[[0, color], [1, color]],
            line=dict(color=color, width=2, dash="dash" if operator in {"<", ">", "!="} else "solid"),
            showscale=False,
            hoverinfo="skip",
            name=name,
        )
    )
    return True


def _clip_relation_grid_to_set(X, Y, Z, clip_set, resolution: int):
    if clip_set is None:
        return Z
    try:
        width = max(float(np.nanmax(X) - np.nanmin(X)), float(np.nanmax(Y) - np.nanmin(Y)))
        tolerance = max(1e-9, width / max(1, int(resolution)) * 0.25)
        clip_mask = clip_set.contains_arrays(X, Y, tolerance=tolerance)
        return np.where(clip_mask, Z, np.nan)
    except Exception:
        return Z


def _clip_preimage_relation_grid_to_set(phi1_expr, phi2_expr, clip_set, bounds, Z, resolution: int):
    if clip_set is None:
        return Z
    try:
        _, _, clip_mask = compute_preimage_grid(phi1_expr, phi2_expr, clip_set, bounds, resolution=resolution)
        return np.where(clip_mask, Z, np.nan)
    except Exception:
        return Z


def _add_source_boundaries(fig: go.Figure, parsed_set, bounds, color: str, name: str, resolution: int, clip_set=None) -> None:
    if isinstance(parsed_set, Relation2D):
        X, Y, Z = sample_relation_grid(parsed_set, bounds, resolution=resolution)
        Z = _clip_relation_grid_to_set(X, Y, Z, clip_set, resolution)
        _add_relation_boundary(fig, X[0, :], Y[:, 0], Z, parsed_set.operator, color, name)
    elif isinstance(parsed_set, CompositeSet):
        if parsed_set.operator == "intersection":
            _add_source_boundaries(fig, parsed_set.left, bounds, color, name, resolution, parsed_set.right)
            _add_source_boundaries(fig, parsed_set.right, bounds, color, name, resolution, parsed_set.left)
        else:
            _add_source_boundaries(fig, parsed_set.left, bounds, color, name, resolution, clip_set)
            _add_source_boundaries(fig, parsed_set.right, bounds, color, name, resolution, clip_set)


def _add_preimage_boundaries(
    fig: go.Figure,
    parsed_set,
    phi1_expr,
    phi2_expr,
    bounds,
    color: str,
    name: str,
    resolution: int,
    clip_set=None,
) -> None:
    if isinstance(parsed_set, Relation2D):
        X, Y, Z = compute_preimage_relation_grid(phi1_expr, phi2_expr, parsed_set, bounds, resolution=resolution)
        Z = _clip_preimage_relation_grid_to_set(phi1_expr, phi2_expr, clip_set, bounds, Z, resolution)
        _add_relation_boundary(fig, X[0, :], Y[:, 0], Z, parsed_set.operator, color, name)
    elif isinstance(parsed_set, CompositeSet):
        if parsed_set.operator == "intersection":
            _add_preimage_boundaries(fig, parsed_set.left, phi1_expr, phi2_expr, bounds, color, name, resolution, parsed_set.right)
            _add_preimage_boundaries(fig, parsed_set.right, phi1_expr, phi2_expr, bounds, color, name, resolution, parsed_set.left)
        else:
            _add_preimage_boundaries(fig, parsed_set.left, phi1_expr, phi2_expr, bounds, color, name, resolution, clip_set)
            _add_preimage_boundaries(fig, parsed_set.right, phi1_expr, phi2_expr, bounds, color, name, resolution, clip_set)


def render() -> None:
    st.header("Odwzorowania wektorowe")
    st.caption("Dla Φ : R² -> R² rysujemy przybliżenie obrazu Φ(C) i przeciwobrazu Φ⁻¹(B).")

    col1, col2 = st.columns(2)
    with col1:
        phi1_str = math_input("Φ₁(x, y)", "functions_2d", "vec_phi1", default_val="x", preview_prefix_latex="\\Phi_1(x,y) = ")
    with col2:
        phi2_str = math_input("Φ₂(x, y)", "functions_2d", "vec_phi2", default_val="y", preview_prefix_latex="\\Phi_2(x,y) = ")

    st.subheader("Zbiory")
    col3, col4 = st.columns(2)
    with col3:
        c_str = input_with_history("Zbiór C ⊆ R² (do obrazu)", "sets_r2", "vec_c", default_val="x^2 + y^2 <= 1")
        c_preview = parse_set_2d(c_str)
        if c_preview:
            st.caption("Podgląd C")
            st.latex(set_latex(c_preview, "C"))
    with col4:
        b_str = input_with_history("Zbiór B ⊆ R² (do przeciwobrazu)", "sets_r2", "vec_b", default_val="u^2 + v^2 <= 1")
        b_preview = parse_set_2d(b_str)
        if b_preview:
            st.caption("Podgląd B")
            st.latex(set_latex(b_preview, "B"))

    st.subheader("Okno źródłowe")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        a = st.number_input("x min", value=-2.0, key="va")
    with col6:
        b = st.number_input("x max", value=2.0, key="vb")
    with col7:
        c = st.number_input("y min", value=-2.0, key="vc")
    with col8:
        d = st.number_input("y max", value=2.0, key="vd")

    quality_resolution = st.slider(
        "Jakość rysowania (liczba próbek na oś)",
        min_value=250,
        max_value=2200,
        value=850,
        step=50,
        help="Większa wartość daje gładsze brzegi i mniej dziur, ale obliczenia trwają dłużej.",
    )

    if st.button("Oblicz i rysuj", type="primary"):
        if a > b or c > d:
            st.error("Okno musi spełniać x min <= x max oraz y min <= y max.")
            return

        phi1_res = parse_expression(phi1_str)
        phi2_res = parse_expression(phi2_str)
        if not phi1_res.is_valid:
            st.error(f"Niepoprawna funkcja Φ₁: {phi1_res.error}")
            return
        if not phi2_res.is_valid:
            st.error(f"Niepoprawna funkcja Φ₂: {phi2_res.error}")
            return

        c_set = parse_set_2d(c_str)
        b_set = parse_set_2d(b_str)
        if not c_set:
            st.error("Niepoprawny zbiór C. Przykłady: [-1,1]x[-1,1], x^2+y^2<=1.")
            return
        if not b_set:
            st.error("Niepoprawny zbiór B. Można używać zmiennych x,y albo u,v.")
            return

        add_or_update_history_entry("functions_2d", phi1_str.strip(), "Φ₁")
        add_or_update_history_entry("functions_2d", phi2_str.strip(), "Φ₂")
        add_or_update_history_entry("sets_r2", c_str.strip(), "Zbiór C")
        add_or_update_history_entry("sets_r2", b_str.strip(), "Zbiór B")

        source_bounds = ((float(a), float(b)), (float(c), float(d)))
        plot_col1, plot_col2 = st.columns(2)

        image_resolution = int(quality_resolution)
        boundary_resolution = min(2200, max(520, image_resolution))
        with plot_col1:
            st.write("### Obraz Φ(C)")
            fig_img = go.Figure()
            if _is_identity_mapping(phi1_res.expr, phi2_res.expr) and isinstance(c_set, Relation2D):
                Xc, Yc, Zc = sample_relation_grid(c_set, source_bounds, resolution=image_resolution)
                if not _add_relation_region(fig_img, Xc[0, :], Yc[:, 0], Zc, c_set.operator, "#1f5f9f", "Φ(C)"):
                    st.info("W wybranym oknie i rozdzielczości nie znaleziono punktów zbioru C.")
            elif _is_identity_mapping(phi1_res.expr, phi2_res.expr):
                Xc, Yc, C_mask = sample_set_grid(c_set, source_bounds, resolution=image_resolution)
                if not C_mask.any():
                    st.info("W wybranym oknie i rozdzielczości nie znaleziono punktów zbioru C.")
                fig_img.add_trace(
                    go.Contour(
                        z=C_mask.astype(float),
                        x=Xc[0, :],
                        y=Yc[:, 0],
                        contours=dict(start=0.5, end=1.5, size=1, coloring="fill", showlines=False),
                        colorscale=[[0, "rgba(255,255,255,0)"], [1, "#1f5f9f"]],
                        showscale=False,
                        hoverinfo="skip",
                        line_smoothing=0.85,
                        name="Φ(C)",
                    )
                )
                _add_source_boundaries(fig_img, c_set, source_bounds, "#1f5f9f", "brzeg Φ(C)", boundary_resolution)
            else:
                u_list, v_list = compute_image_points(phi1_res.expr, phi2_res.expr, c_set, source_bounds, resolution=min(image_resolution, 1300))
                if not u_list:
                    st.info("W wybranym oknie i rozdzielczości nie znaleziono punktów zbioru C.")
                fig_img.add_trace(
                    go.Scattergl(
                        x=u_list,
                        y=v_list,
                        mode="markers",
                        marker=dict(color="#1f5f9f", size=2.2, opacity=0.72),
                        hoverinfo="skip",
                    )
                )
            fig_img.update_layout(
                template="plotly_white",
                xaxis_title="u",
                yaxis_title="v",
                height=440,
                margin=dict(l=20, r=20, t=30, b=20),
            )
            fig_img.update_xaxes(constrain="domain")
            fig_img.update_yaxes(scaleanchor="x", scaleratio=1, constrain="domain")
            st.plotly_chart(fig_img, use_container_width=True)

        preimage_relation_mode = isinstance(b_set, Relation2D)
        if preimage_relation_mode:
            X, Y, Z_rel = compute_preimage_relation_grid(phi1_res.expr, phi2_res.expr, b_set, source_bounds, resolution=image_resolution)
            Z_bool = np.zeros_like(Z_rel, dtype=bool)
        else:
            X, Y, Z_bool = compute_preimage_grid(phi1_res.expr, phi2_res.expr, b_set, source_bounds, resolution=image_resolution)
        with plot_col2:
            st.write("### Przeciwobraz Φ⁻¹(B)")
            if not preimage_relation_mode and not Z_bool.any():
                st.info("W wybranym oknie i rozdzielczości nie znaleziono punktów przeciwobrazu.")
            fig_pre = go.Figure()
            if preimage_relation_mode:
                if not _add_relation_region(fig_pre, X[0, :], Y[:, 0], Z_rel, b_set.operator, "#2f7d46", "Φ⁻¹(B)"):
                    st.info("W wybranym oknie i rozdzielczości nie znaleziono punktów przeciwobrazu.")
            if not preimage_relation_mode:
                fig_pre.add_trace(
                    go.Contour(
                        z=Z_bool.astype(float),
                        x=X[0, :],
                        y=Y[:, 0],
                        contours=dict(start=0.5, end=1.5, size=1, coloring="fill", showlines=False),
                        colorscale=[[0, "rgba(255,255,255,0)"], [1, "#a8d8b9"]],
                        showscale=False,
                        hoverinfo="skip",
                        line_smoothing=0.85,
                        name="Φ⁻¹(B)",
                    )
                )
                _add_preimage_boundaries(fig_pre, b_set, phi1_res.expr, phi2_res.expr, source_bounds, "#2f7d46", "brzeg Φ⁻¹(B)", boundary_resolution)
            fig_pre.update_layout(
                template="plotly_white",
                xaxis_title="x",
                yaxis_title="y",
                height=440,
                margin=dict(l=20, r=20, t=30, b=20),
            )
            fig_pre.update_xaxes(constrain="domain")
            fig_pre.update_yaxes(scaleanchor="x", scaleratio=1, constrain="domain")
            st.plotly_chart(fig_pre, use_container_width=True)
