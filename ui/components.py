import streamlit as st
from typing import List, Dict, Any, Callable, Optional
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

def render_distance_matrix_html(headers: List[str], matrix: List[List['DualValue']], row_headers: Optional[List[str]] = None) -> None:
    if row_headers is None:
        row_headers = headers
    html = "<div style='overflow-x: auto;'><table style='border-collapse: collapse; width: 100%; font-size: 14px;'>"
    html += "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'></th>"
    for h in headers:
        html += f"<th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2; text-align: center;'>{h}</th>"
    html += "</tr>"
    
    for i, row in enumerate(matrix):
        html += f"<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'>{row_headers[i]}</th>"
        for j, dv in enumerate(row):
            html += "<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>"
            if dv.status in ["exact", "exact_and_numeric"] and dv.exact and dv.numeric:
                html += f"""
                <div style='color: #1f77b4; font-weight: bold;' title='{dv.exact}'>{dv.exact}</div>
                <div style='color: #666; font-size: 0.9em;'>{dv.numeric}</div>
                """
            elif dv.status == "interval" and dv.interval:
                html += f"<div title='wartość ∈ [{dv.interval[0]}, {dv.interval[1]}]'>∈ [{dv.interval[0]}, {dv.interval[1]}]</div>"
            elif dv.status == "numeric" and dv.numeric:
                html += f"<div title='≈ {dv.numeric}'>≈ {dv.numeric}</div>"
            elif dv.exact:
                html += f"<div title='{dv.exact}'>{dv.exact}</div>"
            else:
                html += "<div>?</div>"
            html += "</td>"
        html += "</tr>"
        
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)

def history_change_callback(key):
    selected = st.session_state[f"{key}_history"]
    if selected != "-- Wpisz ręcznie --":
        st.session_state[f"{key}_input"] = selected

def input_with_history(
    label: str,
    history_category: str,
    key: str,
    default_val: str = "",
    multiline: bool = False
) -> str:
    history = get_history(history_category)
    options = ["-- Wpisz ręcznie --"] + [h["raw_value"] for h in history]
    
    st.selectbox(f"Historia: {label}", options, key=f"{key}_history", on_change=history_change_callback, args=(key,))
    
    current_val = st.session_state.get(f"{key}_input", default_val)
        
    if multiline:
        val = st.text_area(label, value=current_val, key=f"{key}_input", height=100)
    else:
        val = st.text_input(label, value=current_val, key=f"{key}_input")
        
    return val

def save_to_history_button(category: str, val: str, label: str = "", key_suffix: str = "") -> None:
    if st.button("Zapisz do historii", key=f"save_hist_{category}_{val}_{key_suffix}"):
        if val.strip():
            add_or_update_history_entry(category, val, label)
            st.success("Zapisano!")
