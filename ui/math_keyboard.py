import streamlit as st
import streamlit.components.v1 as components

def render_math_keyboard():
    st.write("Skopiuj symbol (lub kliknij by spróbować auto-wklejenia):")
    
    html_code = """
    <div id="math-keyboard" style="padding: 5px; font-family: sans-serif; background-color: #fbfbfb; border-radius: 8px; border: 1px solid #ddd; display: flex; flex-wrap: wrap;">
        <button onclick="insertSymbol('π')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">π</button>
        <button onclick="insertSymbol('e')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">e</button>
        <button onclick="insertSymbol('√(')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">√</button>
        <button onclick="insertSymbol('^')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">^</button>
        <button onclick="insertSymbol('SUM(')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">∑</button>
        <button onclick="insertSymbol('Abs(')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">|x|</button>
        <button onclick="insertSymbol('∞')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">∞</button>
        <button onclick="insertSymbol('^2')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">x²</button>
    </div>
    <div style="font-size: 12px; color: #666; margin-top: 5px;">
        Bufor (skopiuj jeśli wklejanie nie zadziała):
        <input type="text" id="buffer" style="width: 100%; padding: 4px; margin-top: 2px; border: 1px solid #ccc; border-radius: 4px;">
    </div>
    
    <script>
    function insertSymbol(symbol) {
        document.getElementById('buffer').value += symbol;
        try {
            let parentDoc = window.parent.document;
            let activeEl = parentDoc.activeElement;
            if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) {
                let start = activeEl.selectionStart;
                let end = activeEl.selectionEnd;
                let val = activeEl.value;
                activeEl.value = val.substring(0, start) + symbol + val.substring(end);
                activeEl.selectionStart = activeEl.selectionEnd = start + symbol.length;
                let event = new Event('input', { bubbles: true });
                activeEl.dispatchEvent(event);
            }
        } catch (e) {
            console.log("No cross-origin access");
        }
    }
    </script>
    """
    
    components.html(html_code, height=110)
