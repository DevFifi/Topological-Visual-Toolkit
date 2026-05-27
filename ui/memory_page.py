import streamlit as st
import json
from core.persistence import APP_STATE_PATH, load_state, save_state
from core.history import clear_history_category

def render() -> None:
    st.header("Zarządzanie Pamięcią (JSON)")
    st.write("Aplikacja zapisuje wszystkie poprawne wejścia użytkownika do historii w pliku JSON.")
    
    state = load_state()
    
    st.subheader("Zawartość Pamięci")
    
    tabs = st.tabs(list(state.keys()))
    for i, (key, value) in enumerate(state.items()):
        with tabs[i]:
            if isinstance(value, list):
                st.write(f"Liczba wpisów: {len(value)}")
                if st.button(f"Wyczyść kategorię '{key}'", key=f"clear_{key}"):
                    clear_history_category(key)
                    st.rerun()
            st.json(value)
            
    st.subheader("Plik JSON")
    st.code(APP_STATE_PATH)
    
    with open(APP_STATE_PATH, "r", encoding="utf-8") as f:
        st.download_button(
            label="Pobierz plik app_state.json",
            data=f.read(),
            file_name="app_state.json",
            mime="application/json"
        )
