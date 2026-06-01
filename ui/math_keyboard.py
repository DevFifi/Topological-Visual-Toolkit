import streamlit.components.v1 as components


def render_math_keyboard():
    html_code = """
<style>
.mk-container { padding: 12px; font-family: Inter, sans-serif; background-color: #fcfcfc; border-radius: 8px; border: 1px solid #eaeaea; }
.mk-group { margin-bottom: 12px; }
.mk-group-title { font-size: 11px; color: #777; margin-bottom: 6px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.4px; }
.mk-btn {
font-size: 14px; padding: 6px 10px; margin: 3px 2px; cursor: pointer;
border-radius: 6px; border: 1px solid #ddd; background: #fff; color: #222;
transition: all 0.12s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.mk-btn:hover { background: #f2f6fa; border-color: #aac6df; color: #164c80; }
</style>

<div class="mk-container" id="math-keyboard">
<div class="mk-group">
<div class="mk-group-title">Stałe i zmienne</div>
<button type="button" class="mk-btn" data-sym="x">x</button>
<button type="button" class="mk-btn" data-sym="y">y</button>
<button type="button" class="mk-btn" data-sym="u">u</button>
<button type="button" class="mk-btn" data-sym="v">v</button>
<button type="button" class="mk-btn" data-sym="xi">xi</button>
<button type="button" class="mk-btn" data-sym="yi">yi</button>
<button type="button" class="mk-btn" data-sym="e">e</button>
<button type="button" class="mk-btn" data-sym="pi">π</button>
<button type="button" class="mk-btn" data-sym="oo">∞</button>
</div>

<div class="mk-group">
<div class="mk-group-title">Operacje</div>
<button type="button" class="mk-btn" data-sym="+">+</button>
<button type="button" class="mk-btn" data-sym="-">-</button>
<button type="button" class="mk-btn" data-sym="*">*</button>
<button type="button" class="mk-btn" data-sym="/">/</button>
<button type="button" class="mk-btn" data-sym="^">^</button>
<button type="button" class="mk-btn" data-sym="&lt;=">&lt;=</button>
<button type="button" class="mk-btn" data-sym="&gt;=">&gt;=</button>
<button type="button" class="mk-btn" data-sym="=">=</button>
<button type="button" class="mk-btn" data-sym="()" data-off="1">( )</button>
<button type="button" class="mk-btn" data-sym="||" data-off="1">| |</button>
</div>

<div class="mk-group">
<div class="mk-group-title">Zbiory</div>
<button type="button" class="mk-btn" data-sym=" \\land ">∧</button>
<button type="button" class="mk-btn" data-sym=" \\lor ">∨</button>
<button type="button" class="mk-btn" data-sym=" \\cap ">∩</button>
<button type="button" class="mk-btn" data-sym=" \\cup ">∪</button>
<button type="button" class="mk-btn" data-sym="{}" data-off="1">{ }</button>
<button type="button" class="mk-btn" data-sym="{(,)}" data-off="3">{( , )}</button>
<button type="button" class="mk-btn" data-sym="[-1,1]x[-1,1]">prostokąt</button>
<button type="button" class="mk-btn" data-sym="x^2 + y^2 &lt;= 1">dysk</button>
<button type="button" class="mk-btn" data-sym="1/4 &lt; x^2 + y^2 &lt;= 1">pierścień</button>
</div>

<div class="mk-group">
<div class="mk-group-title">Funkcje i zapis LaTeX</div>
<button type="button" class="mk-btn" data-sym="\\frac{}{}" data-off="3">\\frac</button>
<button type="button" class="mk-btn" data-sym="\\sqrt{}" data-off="1">√</button>
<button type="button" class="mk-btn" data-sym="sin()" data-off="1">sin</button>
<button type="button" class="mk-btn" data-sym="cos()" data-off="1">cos</button>
<button type="button" class="mk-btn" data-sym="tan()" data-off="1">tan</button>
<button type="button" class="mk-btn" data-sym="log()" data-off="1">log</button>
<button type="button" class="mk-btn" data-sym="exp()" data-off="1">exp</button>
<button type="button" class="mk-btn" data-sym="e^()" data-off="1">e^</button>
<button type="button" class="mk-btn" data-sym="SUM()" data-off="1">SUM</button>
<button type="button" class="mk-btn" data-sym="Min(,)" data-off="2">Min</button>
<button type="button" class="mk-btn" data-sym="Max(,)" data-off="2">Max</button>
</div>
</div>

<script>
(() => {
const parentWindow = window.parent;
let parentDocument = null;
try {
    parentDocument = parentWindow.document;
} catch (err) {
    return;
}

const isEditableTarget = el => {
    if (!el) return false;
    if (!parentDocument.contains(el)) return false;
    const tag = el.tagName;
    if (tag !== "INPUT" && tag !== "TEXTAREA") return false;
    if (el.disabled || el.readOnly) return false;
    const type = (el.getAttribute("type") || "text").toLowerCase();
    return !["button", "submit", "reset", "checkbox", "radio", "file", "hidden"].includes(type);
};

if (!parentWindow.__mathKeyboardState) {
    parentWindow.__mathKeyboardState = { input: null, start: 0, end: 0 };
}

const remember = el => {
    if (!isEditableTarget(el)) return;
    parentWindow.__mathKeyboardState.input = el;
    parentWindow.__mathKeyboardState.start = typeof el.selectionStart === "number" ? el.selectionStart : el.value.length;
    parentWindow.__mathKeyboardState.end = typeof el.selectionEnd === "number" ? el.selectionEnd : el.value.length;
};

parentDocument.addEventListener("focusin", e => remember(e.target), true);
parentDocument.addEventListener("mousedown", e => remember(e.target), true);
parentDocument.addEventListener("mouseup", e => remember(e.target), true);
parentDocument.addEventListener("keyup", e => remember(e.target), true);
parentDocument.addEventListener("select", e => remember(e.target), true);
parentDocument.addEventListener("input", e => remember(e.target), true);

const setNativeValue = (el, value) => {
    const win = el.ownerDocument.defaultView;
    const proto = el.tagName === "TEXTAREA" ? win.HTMLTextAreaElement.prototype : win.HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(proto, "value");
    if (descriptor && descriptor.set) {
        descriptor.set.call(el, value);
    } else {
        el.value = value;
    }
};

const insertSymbol = (symbol, backOffset) => {
    const state = parentWindow.__mathKeyboardState;
    let el = state.input;
    if (!isEditableTarget(el)) el = parentDocument.activeElement;
    if (!isEditableTarget(el)) return;

    el.focus({ preventScroll: true });
    const value = el.value || "";
    const start = typeof el.selectionStart === "number" ? el.selectionStart : state.start;
    const end = typeof el.selectionEnd === "number" ? el.selectionEnd : state.end;
    const safeStart = Math.max(0, Math.min(start, value.length));
    const safeEnd = Math.max(0, Math.min(end, value.length));
    const newValue = value.slice(0, safeStart) + symbol + value.slice(safeEnd);
    const cursor = Math.max(0, Math.min(safeStart + symbol.length - backOffset, newValue.length));

    setNativeValue(el, newValue);
    const ParentInputEvent = parentWindow.InputEvent || window.InputEvent;
    const ParentEvent = parentWindow.Event || window.Event;
    try {
        el.dispatchEvent(new ParentInputEvent("input", { bubbles: true, inputType: "insertText", data: symbol }));
    } catch (err) {
        el.dispatchEvent(new ParentEvent("input", { bubbles: true }));
    }
    el.dispatchEvent(new ParentEvent("change", { bubbles: true }));
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
        insertSymbol(btn.getAttribute("data-sym") || "", parseInt(btn.getAttribute("data-off") || "0", 10));
    });
    btn.addEventListener("click", e => {
        e.preventDefault();
        e.stopPropagation();
    });
});
})();
</script>
"""
    components.html(html_code, height=520, scrolling=True)
