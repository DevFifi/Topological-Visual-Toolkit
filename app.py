import streamlit as st
from ui.styles import apply_global_styles

import ui.finite_metric_spaces_page as p1
import ui.supremum_interval_page as p2
import ui.supremum_rectangle_page as p3
import ui.bernstein_approximation_page as p4
import ui.scalar_preimage_page as p5
import ui.vector_mapping_images_page as p6
import ui.memory_page as mem
import ui.documentation_page as doc

st.set_page_config(
    page_title="Topological Visual Toolkit",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_global_styles()

st.sidebar.title("Nawigacja")
page = st.sidebar.radio(
    "Wybierz moduł:",
    [
        "Przestrzenie Metryczne",
        "Supremum na Przedziale",
        "Supremum na Prostokącie",
        "Aproksymacja Bernsteina",
        "Przeciwobraz Skalarny",
        "Odwzorowania Wektorowe",
        "Pamięć",
        "Dokumentacja"
    ]
)

if page == "Przestrzenie Metryczne":
    p1.render()
elif page == "Supremum na Przedziale":
    p2.render()
elif page == "Supremum na Prostokącie":
    p3.render()
elif page == "Aproksymacja Bernsteina":
    p4.render()
elif page == "Przeciwobraz Skalarny":
    p5.render()
elif page == "Odwzorowania Wektorowe":
    p6.render()
elif page == "Pamięć":
    mem.render()
elif page == "Dokumentacja":
    doc.render()
