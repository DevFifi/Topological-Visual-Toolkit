import streamlit as st
import streamlit.components.v1 as components

def render_math_keyboard():
    html_code = """
<style>
.mk-container { padding: 12px; font-family: Inter, sans-serif; background-color: #fcfcfc; border-radius: 8px; border: 1px solid #eaeaea; }
.mk-group { margin-bottom: 12px; }
.mk-group-title { font-size: 11px; color: #888; margin-bottom: 6px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.mk-btn {
font-size: 14px; padding: 6px 12px; margin: 3px 2px; cursor: pointer;
border-radius: 6px; border: 1px solid #ddd; background: #fff; color: #333;
transition: all 0.15s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-family: monospace;
}
.mk-btn:hover { background: #f0f4f8; border-color: #b9d2e8; color: #1a5c99; transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.mk-btn:active { transform: translateY(0); box-shadow: none; }
</style>

<div class="mk-container" id="math-keyboard">
<div class="mk-group">
<div class="mk-group-title">Zmienne i Stałe</div>
<button type="button" class="mk-btn" title="x - Reprezentuje pierwszy wektor" data-sym="x">x</button>
<button type="button" class="mk-btn" title="y - Reprezentuje drugi wektor" data-sym="y">y</button>
<button type="button" class="mk-btn" title="xi - i-ta współrzędna wektora x (używane w SUM)" data-sym="xi">xi</button>
<button type="button" class="mk-btn" title="yi - i-ta współrzędna wektora y (używane w SUM)" data-sym="yi">yi</button>
<button type="button" class="mk-btn" title="Nieskończoność" data-sym="oo">∞</button>
<button type="button" class="mk-btn" title="Liczba Pi" data-sym="pi">π</button>
<button type="button" class="mk-btn" title="Liczba Eulera" data-sym="e">e</button>
</div>

<div class="mk-group">
<div class="mk-group-title">Operacje Podstawowe</div>
<button type="button" class="mk-btn" title="Dodawanie" data-sym="+">+</button>
<button type="button" class="mk-btn" title="Odejmowanie" data-sym="-">-</button>
<button type="button" class="mk-btn" title="Mnożenie" data-sym="*">*</button>
<button type="button" class="mk-btn" title="Dzielenie" data-sym="/">/</button>
<button type="button" class="mk-btn" title="Równość" data-sym="=">=</button>
<button type="button" class="mk-btn" title="Mniejsze" data-sym="<"><</button>
<button type="button" class="mk-btn" title="Większe" data-sym=">">></button>
<button type="button" class="mk-btn" title="Potęgowanie, np. x^2" data-sym="^">^</button>
<button type="button" class="mk-btn" title="Nawiasy, np. (x+y)" data-sym="()" data-off="1">( )</button>
</div>

<div class="mk-group">
<div class="mk-group-title">Funkcje</div>
<button type="button" class="mk-btn" title="SUM(wyrażenie)" data-sym="SUM()" data-off="1">∑</button>
<button type="button" class="mk-btn" title="Wartość bezwzględna" data-sym="||" data-off="1">| |</button>
<button type="button" class="mk-btn" title="Abs(wyrażenie)" data-sym="Abs()" data-off="1">Abs</button>
<button type="button" class="mk-btn" title="sqrt(wyrażenie)" data-sym="sqrt()" data-off="1">√</button>
<button type="button" class="mk-btn" title="root(wyrażenie, n)" data-sym="root(,)" data-off="2">root</button>
<button type="button" class="mk-btn" title="Min(a, b)" data-sym="Min(,)" data-off="2">Min</button>
<button type="button" class="mk-btn" title="Max(a, b)" data-sym="Max(,)" data-off="2">Max</button>
<button type="button" class="mk-btn" title="log(x)" data-sym="log()" data-off="1">log</button>
<button type="button" class="mk-btn" title="sin(x)" data-sym="sin()" data-off="1">sin</button>
<button type="button" class="mk-btn" title="cos(x)" data-sym="cos()" data-off="1">cos</button>
<button type="button" class="mk-btn" title="tan(x)" data-sym="tan()" data-off="1">tan</button>
<button type="button" class="mk-btn" title="exp(x)" data-sym="exp()" data-off="1">exp</button>
</div>

<div class="mk-group">
<div class="mk-group-title">Litery Greckie</div>
<button type="button" class="mk-btn" title="Alfa" data-sym="α">α</button>
<button type="button" class="mk-btn" title="Beta" data-sym="β">β</button>
<button type="button" class="mk-btn" title="Gamma" data-sym="γ">γ</button>
<button type="button" class="mk-btn" title="Delta" data-sym="δ">δ</button>
<button type="button" class="mk-btn" title="Epsilon" data-sym="ε">ε</button>
<button type="button" class="mk-btn" title="Theta" data-sym="θ">θ</button>
<button type="button" class="mk-btn" title="Lambda" data-sym="λ">λ</button>
<button type="button" class="mk-btn" title="Mi" data-sym="μ">μ</button>
<button type="button" class="mk-btn" title="Rho" data-sym="ρ">ρ</button>
<button type="button" class="mk-btn" title="Sigma" data-sym="σ">σ</button>
<button type="button" class="mk-btn" title="Tau" data-sym="τ">τ</button>
<button type="button" class="mk-btn" title="Phi" data-sym="φ">φ</button>
<button type="button" class="mk-btn" title="Psi" data-sym="ψ">ψ</button>
<button type="button" class="mk-btn" title="Omega" data-sym="ω">ω</button>
</div>
</div>

<script>
const parentWindow = window.parent;
const parentDocument = parentWindow.document;

if (!parentWindow.__mathKeyboardState) {
    parentWindow.__mathKeyboardState = {
        input: null,
        start: 0,
        end: 0
    };

    const isEditableTarget = el => {
        if (!el) return false;
        const tag = el.tagName;
        if (tag !== "INPUT" && tag !== "TEXTAREA") return false;
        if (el.disabled || el.readOnly) return false;
        const type = (el.getAttribute("type") || "text").toLowerCase();
        return !["button", "submit", "reset", "checkbox", "radio", "file", "hidden"].includes(type);
    };

    const remember = el => {
        if (!isEditableTarget(el)) return;
        parentWindow.__mathKeyboardState.input = el;
        parentWindow.__mathKeyboardState.start = typeof el.selectionStart === "number" ? el.selectionStart : el.value.length;
        parentWindow.__mathKeyboardState.end = typeof el.selectionEnd === "number" ? el.selectionEnd : el.value.length;
    };

    parentDocument.addEventListener("focusin", e => remember(e.target), true);
    parentDocument.addEventListener("mouseup", e => remember(e.target), true);
    parentDocument.addEventListener("keyup", e => remember(e.target), true);
    parentDocument.addEventListener("select", e => remember(e.target), true);
    parentDocument.addEventListener("input", e => remember(e.target), true);
}

const isEditableTarget = el => {
    if (!el) return false;
    const tag = el.tagName;
    if (tag !== "INPUT" && tag !== "TEXTAREA") return false;
    if (el.disabled || el.readOnly) return false;
    const type = (el.getAttribute("type") || "text").toLowerCase();
    return !["button", "submit", "reset", "checkbox", "radio", "file", "hidden"].includes(type);
};

const setNativeValue = (el, value) => {
    const win = el.ownerDocument.defaultView;
    const proto = el.tagName === "TEXTAREA" ? win.HTMLTextAreaElement.prototype : win.HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(proto, "value");
    descriptor.set.call(el, value);
};

const insertSymbol = (symbol, backOffset) => {
    const state = parentWindow.__mathKeyboardState;
    let el = state.input;

    if (!isEditableTarget(el)) {
        el = parentDocument.activeElement;
    }

    if (!isEditableTarget(el)) return;

    el.focus({ preventScroll: true });

    const value = el.value || "";
    const start = typeof el.selectionStart === "number" ? el.selectionStart : state.start;
    const end = typeof el.selectionEnd === "number" ? el.selectionEnd : state.end;

    const safeStart = Math.max(0, Math.min(start, value.length));
    const safeEnd = Math.max(0, Math.min(end, value.length));

    const newValue = value.slice(0, safeStart) + symbol + value.slice(safeEnd);
    const rawCursor = safeStart + symbol.length - backOffset;
    const cursor = Math.max(0, Math.min(rawCursor, newValue.length));

    setNativeValue(el, newValue);

    el.dispatchEvent(new InputEvent("input", {
        bubbles: true,
        inputType: "insertText",
        data: symbol
    }));

    el.dispatchEvent(new Event("change", { bubbles: true }));

    el.focus({ preventScroll: true });
    el.setSelectionRange(cursor, cursor);

    state.input = el;
    state.start = cursor;
    state.end = cursor;
};

document.querySelectorAll(".mk-btn").forEach(btn => {
    btn.addEventListener("mousedown", e => {
        e.preventDefault();
        e.stopPropagation();
        const symbol = btn.getAttribute("data-sym") || "";
        const backOffset = parseInt(btn.getAttribute("data-off") || "0", 10);
        insertSymbol(symbol, backOffset);
    });

    btn.addEventListener("click", e => {
        e.preventDefault();
        e.stopPropagation();
    });
});
</script>
"""
    components.html(html_code, height=450, scrolling=True)