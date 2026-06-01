import html
import re
from typing import List, Optional, Tuple

import streamlit as st
import sympy

from core.exact_numeric import DualValue
from core.expression_parser import parse_expression
from core.formatting import format_exact, latex_exact
from core.history import add_or_update_history_entry, get_history, remove_history_entry
from core.set_parser import split_top_level


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


def _point_items_for_label(raw: str) -> List[str]:
    cleaned = str(raw).strip()
    if not cleaned:
        return []
    if cleaned.startswith("[") and cleaned.endswith("]"):
        inner = cleaned[1:-1].strip()
        return split_top_level(inner) if inner else []
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if len(lines) == 1:
        loose = split_top_level(lines[0])
        return loose if len(loose) > 1 else lines
    return lines


def _history_role_label(label: str) -> str:
    cleaned = str(label or "").strip()
    lowered = cleaned.lower()
    if re.search(r"(^|\s)(zbior|zbiór)?\s*e($|\s)", lowered) or cleaned == "E":
        return "[E]"
    if re.search(r"(^|\s)(zbior|zbiór)?\s*f($|\s)", lowered) or cleaned == "F":
        return "[F]"
    if "punkt" in lowered:
        return "[P]"
    if cleaned in {"A", "B", "C"}:
        return f"[{cleaned}]"
    return "[ ]"


def _split_box_product_for_label(text: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    stack: List[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = set(pairs.values())
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in pairs:
            stack.append(pairs[ch])
            current.append(ch)
            i += 1
            continue
        if ch in closing:
            if stack and ch == stack[-1]:
                stack.pop()
            current.append(ch)
            i += 1
            continue
        if not stack and text.startswith(r"\times", i):
            parts.append("".join(current).strip())
            current = []
            i += len(r"\times")
            continue
        prev_nonspace = next((text[j] for j in range(i - 1, -1, -1) if not text[j].isspace()), "")
        next_nonspace = next((text[j] for j in range(i + 1, len(text)) if not text[j].isspace()), "")
        if not stack and ch in {"x", "X", "×"} and prev_nonspace in {"]", ")"} and next_nonspace in {"[", "("}:
            parts.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _point_history_meta(raw: str) -> Tuple[str, str, str]:
    text = str(raw).strip()
    generator_match = re.match(r"^\s*(random|basis|line)\s*\((.*)\)\s*$", text, flags=re.IGNORECASE | re.DOTALL)
    if generator_match:
        args = {}
        for item in split_top_level(generator_match.group(2)):
            if "=" in item:
                key, value = item.split("=", 1)
                args[key.strip().lower()] = value.strip()
        dim = args.get("dim", "?")
        if generator_match.group(1).lower() == "basis":
            count = str(int(dim) + 1) if str(dim).isdigit() else "n+1"
        else:
            count = args.get("count", "?")
        return str(dim), count, text

    if any(token in text for token in ("\\cup", "\\cap", "\\land", "\\lor", "×")) or re.search(r"[\]\)]\s*[xX]\s*[\[(]", text):
        boxes = re.findall(
            r"[\[\(][^\[\]\(\)]*,[^\[\]\(\)]*[\]\)](?:\s*(?:\\times|×|[xX])\s*[\[\(][^\[\]\(\)]*,[^\[\]\(\)]*[\]\)])*",
            text,
        )
        product_parts = _split_box_product_for_label(boxes[0]) if boxes else []
        dim = str(len(product_parts)) if product_parts else "?"
        return dim, "∞", " ".join(text.split())

    items = _point_items_for_label(raw)
    dims = []
    for item in items:
        item = item.strip()
        if (item.startswith("(") and item.endswith(")")) or (item.startswith("[") and item.endswith("]")):
            dims.append(len(split_top_level(item[1:-1])))
        elif item:
            dims.append(1)
    if not items or not dims:
        preview = text.splitlines()[0] if text else ""
        return "?", "?", preview
    dim_values = sorted(set(dims))
    dim_text = str(dim_values[0]) if len(dim_values) == 1 else "/".join(str(dim) for dim in dim_values)
    preview_items = items[:2]
    preview = "[" + ", ".join(preview_items) + (", ..." if len(items) > 2 else "") + "]"
    return dim_text, str(len(items)), preview


def _format_point_history_option(label_text: str, raw: str) -> str:
    dim, count, preview = _point_history_meta(raw)
    preview = " ".join(str(preview).split())
    result = f"{_history_role_label(label_text)} | n={dim} | {count} | {preview}"
    return result if len(result) <= 120 else result[:117] + "..."


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
        label_text = entry_by_id[entry_id].get("label", "").strip()
        if history_category == "metric_points":
            return _format_point_history_option(label_text, raw)
        first_line = str(raw).strip().splitlines()[0] if str(raw).strip() else ""
        result = first_line if len(first_line) <= 90 else first_line[:87] + "..."
        return result if len(result) <= 90 else result[:87] + "..."

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
