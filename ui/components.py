import html
from typing import List, Optional

import streamlit as st
import sympy

from core.exact_numeric import DualValue
from core.expression_parser import parse_expression
from core.formatting import format_exact, latex_exact
from core.history import add_or_update_history_entry, get_history, remove_history_entry


def render_dual_value(dv: DualValue, title: str = "Wynik") -> None:
    st.write(f"**{title}**")

    if dv.status in ["exact", "exact_and_numeric"]:
        if dv.exact_latex:
            st.caption("Dokładnie")
            st.latex(dv.exact_latex)
        elif dv.exact:
            exact_html = f"<div class='dual-exact'>{html.escape(format_exact(dv.exact))}</div>"
            st.markdown(f"<div class='dual-value-box'>{exact_html}</div>", unsafe_allow_html=True)
        if dv.numeric:
            numeric_html = f"<div class='dual-numeric'>≈ {html.escape(str(dv.numeric))}</div>"
            st.markdown(f"<div class='dual-value-box'>{numeric_html}</div>", unsafe_allow_html=True)
    elif dv.status == "interval" and dv.interval:
        interval_html = (
            f"<div class='dual-interval'>wartość ∈ "
            f"[{html.escape(str(dv.interval[0]))}, {html.escape(str(dv.interval[1]))}]</div>"
        )
        st.markdown(f"<div class='dual-value-box'>{interval_html}</div>", unsafe_allow_html=True)
    elif dv.status == "numeric":
        numeric_html = f"<div class='dual-interval'>≈ {html.escape(str(dv.numeric))}</div>"
        st.markdown(f"<div class='dual-value-box'>{numeric_html}</div>", unsafe_allow_html=True)
    else:
        st.error("Nie udało się wykonać obliczeń.")

    if dv.method:
        st.caption(f"Metoda: {dv.method}")

    for note in dv.notes:
        st.info(note)


def _safe_table_latex(value: str) -> str:
    return value.replace("|", r"\vert ")


def _matrix_cell_markdown(dv: DualValue) -> str:
    if dv.status in ["exact", "exact_and_numeric"] and (dv.exact_latex or dv.exact):
        exact = _safe_table_latex(dv.exact_latex or latex_exact(dv.exact))
        numeric = f"<br><small>≈ {html.escape(str(dv.numeric))}</small>" if dv.numeric else ""
        return f"${exact}${numeric}"
    if dv.status == "interval" and dv.interval:
        lo = html.escape(str(dv.interval[0]))
        hi = html.escape(str(dv.interval[1]))
        return f"∈ [{lo}, {hi}]"
    if dv.status == "numeric" and dv.numeric:
        return f"≈ {html.escape(str(dv.numeric))}"
    if dv.exact:
        return f"${_safe_table_latex(latex_exact(dv.exact))}$"
    return "?"


def render_distance_matrix_html(
    headers: List[str],
    matrix: List[List[DualValue]],
    row_headers: Optional[List[str]] = None,
    headers_latex: Optional[List[str]] = None,
    row_headers_latex: Optional[List[str]] = None,
) -> None:
    if row_headers is None:
        row_headers = headers

    if headers_latex is not None or row_headers_latex is not None:
        latex_headers = headers_latex or [latex_exact(h) for h in headers]
        latex_rows = row_headers_latex or latex_headers
        lines = []
        header_cells = [""] + [f"${_safe_table_latex(h)}$" for h in latex_headers]
        lines.append("| " + " | ".join(header_cells) + " |")
        lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
        for row_label, row in zip(latex_rows, matrix):
            cells = [f"${_safe_table_latex(row_label)}$"] + [_matrix_cell_markdown(dv) for dv in row]
            lines.append("| " + " | ".join(cells) + " |")
        st.markdown("\n".join(lines), unsafe_allow_html=True)
        return

    html_parts = [
        "<div style='overflow-x: auto;'>",
        "<table style='border-collapse: collapse; width: 100%; font-size: 14px;'>",
        "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'></th>",
    ]
    for header in headers:
        html_parts.append(
            "<th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2; text-align: center;'>"
            f"{html.escape(str(header))}</th>"
        )
    html_parts.append("</tr>")

    for i, row in enumerate(matrix):
        html_parts.append(
            "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'>"
            f"{html.escape(str(row_headers[i]))}</th>"
        )
        for dv in row:
            html_parts.append("<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>")
            if dv.status in ["exact", "exact_and_numeric"] and dv.exact and dv.numeric:
                exact = html.escape(format_exact(dv.exact))
                numeric = html.escape(str(dv.numeric))
                html_parts.append(
                    f"<div style='color: #1f5f9f; font-weight: 600;' title='{exact}'>{exact}</div>"
                    f"<div style='color: #666; font-size: 0.9em;'>{numeric}</div>"
                )
            elif dv.status == "interval" and dv.interval:
                lo = html.escape(str(dv.interval[0]))
                hi = html.escape(str(dv.interval[1]))
                html_parts.append(f"<div title='wartość ∈ [{lo}, {hi}]'>∈ [{lo}, {hi}]</div>")
            elif dv.status == "numeric" and dv.numeric:
                numeric = html.escape(str(dv.numeric))
                html_parts.append(f"<div title='≈ {numeric}'>≈ {numeric}</div>")
            elif dv.exact:
                exact = html.escape(format_exact(dv.exact))
                html_parts.append(f"<div title='{exact}'>{exact}</div>")
            else:
                html_parts.append("<div>?</div>")
            html_parts.append("</td>")
        html_parts.append("</tr>")

    html_parts.append("</table></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def math_input(
    label: str,
    history_category: str,
    key: str,
    default_val: str = "",
    multiline: bool = False,
    preview: bool = True,
    preview_prefix_latex: str = "",
    help_text: Optional[str] = None,
) -> str:
    entries = get_history(history_category)
    options: List[Optional[str]] = [None] + [entry["id"] for entry in entries]
    entry_by_id = {entry["id"]: entry for entry in entries}

    def format_option(entry_id: Optional[str]) -> str:
        if entry_id is None:
            return "Wpisz ręcznie"
        raw = entry_by_id[entry_id]["raw_value"]
        return raw if len(raw) <= 70 else raw[:67] + "..."

    selected_id = st.selectbox(
        f"Historia: {label}",
        options,
        format_func=format_option,
        key=f"{key}_history",
    )

    if selected_id is not None:
        selected_raw = entry_by_id[selected_id]["raw_value"]
        applied_key = f"{key}_history_applied"
        if st.session_state.get(applied_key) != selected_id:
            st.session_state[f"{key}_input"] = selected_raw
            st.session_state[applied_key] = selected_id

        if st.button("Usuń wybrany wpis", key=f"{key}_delete_history"):
            remove_history_entry(history_category, selected_id)
            if st.session_state.get(f"{key}_input") == selected_raw:
                st.session_state[f"{key}_input"] = default_val
            st.session_state.pop(applied_key, None)
            st.rerun()

    current_val = st.session_state.get(f"{key}_input", default_val)
    if multiline:
        value = st.text_area(label, value=current_val, key=f"{key}_input", height=110, help=help_text)
    else:
        value = st.text_input(label, value=current_val, key=f"{key}_input", help=help_text)

    if preview and value.strip():
        result = parse_expression(value)
        if result.is_valid:
            st.caption("Podgląd wzoru")
            st.latex(f"{preview_prefix_latex}{sympy.latex(result.expr)}")
        else:
            st.caption(result.error)

    return value


def input_with_history(
    label: str,
    history_category: str,
    key: str,
    default_val: str = "",
    multiline: bool = False,
) -> str:
    return math_input(
        label,
        history_category,
        key,
        default_val=default_val,
        multiline=multiline,
        preview=False,
    )


def save_history_value(category: str, value: str, label: str = "", parsed_preview: str = "") -> None:
    if value.strip():
        add_or_update_history_entry(category, value.strip(), label=label, parsed_preview=parsed_preview)
