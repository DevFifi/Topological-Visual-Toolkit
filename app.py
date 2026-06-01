import streamlit as st

from core.persistence import reset_state_from_draft
from ui.styles import apply_global_styles
from ui.math_keyboard import render_math_keyboard

import ui.finite_metric_spaces_page as p1
import ui.supremum_interval_page as p2
import ui.supremum_rectangle_page as p3
import ui.bernstein_approximation_page as p4
import ui.scalar_preimage_page as p5
import ui.vector_mapping_images_page as p6


PAGES = {
    "Przestrzenie metryczne": p1.render,
    "Supremum na przedziale": p2.render,
    "Supremum na prostokącie": p3.render,
    "Aproksymacja Bernsteina": p4.render,
    "Funkcja R² → R i przeciwobraz": p5.render,
    "Odwzorowania wektorowe": p6.render,
}


st.set_page_config(
    page_title="Topological Visual Toolkit",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()

st.sidebar.title("Nawigacja")
if st.session_state.pop("state_reset_done", False):
    st.sidebar.success("Przywrócono stan początkowy.")

page = st.sidebar.radio("Wybierz moduł:", list(PAGES.keys()))

with st.sidebar.expander("Klawiatura matematyczna", expanded=False):
    render_math_keyboard()

with st.sidebar.expander("Stan aplikacji", expanded=False):
    st.caption("Przywraca domyślną pamięć przykładów i czyści bieżące pola formularzy.")
    if st.button("Przywróć stan początkowy", type="secondary"):
        reset_state_from_draft()
        st.cache_data.clear()
        st.cache_resource.clear()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["state_reset_done"] = True
        st.rerun()

PAGES[page]()
