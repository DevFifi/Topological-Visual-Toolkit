import streamlit as st
from typing import List, Dict, Any, Callable
from core.exact_numeric import DualValue
from core.history import get_history, add_or_update_history_entry

def render_dual_value(dv: DualValue, title: str = "Wynik") -> None:
    st.write(f"**{title}**")
    
    if dv.status in ["exact", "exact_and_numeric"]:
        exact_html = f"<div class='dual-exact'>{dv.exact}</div>"
        numeric_html = f"<div class='dual-numeric'>{dv.numeric}</div>" if dv.numeric else ""
        st.markdown(f"<div class='dual-value-box'>{exact_html}{numeric_html}</div>", unsafe_allow_html=True)
    elif dv.status == "interval":
        interval_html = f"<div class='dual-interval'>wartość ∈ [{dv.interval[0]}, {dv.interval[1]}]</div>"
        st.markdown(f"<div class='dual-value-box'>{interval_html}</div>", unsafe_allow_html=True)
    elif dv.status == "numeric":
        numeric_html = f"<div class='dual-interval'>≈ {dv.numeric}</div>"
        st.markdown(f"<div class='dual-value-box'>{numeric_html}</div>", unsafe_allow_html=True)
    else:
        st.error("Błąd obliczeń lub nieznany status.")

    if dv.method:
        st.caption(f"Metoda: {dv.method}")
        
    for note in dv.notes:
        st.info(note)

def render_distance_matrix_html(headers: List[str], rows: List[List[DualValue]]) -> None:
    html = "<table style='width: 100%; border-collapse: collapse; margin-bottom: 1rem;'>"
    
    html += "<tr><th style='padding: 8px; border-bottom: 2px solid #ddd;'></th>"
    for h in headers:
        html += f"<th style='padding: 8px; border-bottom: 2px solid #ddd; text-align: center;'>{h}</th>"
    html += "</tr>"
    
    for i, row in enumerate(rows):
        html += f"<tr><th style='padding: 8px; border-right: 2px solid #ddd; text-align: right;'>{headers[i]}</th>"
        for dv in row:
            html += "<td style='padding: 4px;'>"
            if dv.status in ["exact", "exact_and_numeric"] and dv.exact and dv.numeric:
                html += f"""
                <div class='table-cell-dual'>
                    <div class='table-cell-exact' title='{dv.exact}'>{dv.exact}</div>
                    <div class='table-cell-numeric'>{dv.numeric}</div>
                </div>
                """
            elif dv.status == "interval" and dv.interval:
                html += f"<div class='table-cell-single' title='wartość ∈ [{dv.interval[0]}, {dv.interval[1]}]'>∈ [{dv.interval[0]}, {dv.interval[1]}]</div>"
            elif dv.status == "numeric" and dv.numeric:
                html += f"<div class='table-cell-single' title='≈ {dv.numeric}'>≈ {dv.numeric}</div>"
            elif dv.exact:
                html += f"<div class='table-cell-single' title='{dv.exact}'>{dv.exact}</div>"
            else:
                html += "<div class='table-cell-single'>?</div>"
            html += "</td>"
        html += "</tr>"
        
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

def input_with_history(
    label: str,
    category: str,
    key: str,
    default_val: str = "",
    help_text: str = ""
) -> str:
    history = get_history(category)
    options = ["-- Nowy wpis --"] + [h["raw_value"] for h in history]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected = st.selectbox(f"Historia ({category})", options, key=f"{key}_hist")
        
    with col2:
        current_default = default_val
        if selected != "-- Nowy wpis --":
            current_default = selected
            
        val = st.text_input(label, value=current_default, key=f"{key}_input", help=help_text)
        
    return val

def save_to_history_button(category: str, val: str, label: str = "") -> None:
    if st.button("Zapisz do historii", key=f"save_hist_{category}_{val}"):
        if val.strip():
            add_or_update_history_entry(category, val, label)
            st.success("Zapisano!")
