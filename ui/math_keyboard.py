import streamlit as st

def render_math_keyboard():
    html_code = """
    <div id="math-keyboard" style="padding: 5px; font-family: sans-serif; background-color: #fbfbfb; border-radius: 8px; border: 1px solid #ddd; display: flex; flex-wrap: wrap;">
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('π')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">π</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('e')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">e</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('√()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">√</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('root(,)', 2)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">root(x,n)</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('^')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">^</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('SUM()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">∑</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('Abs()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">|x|</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('∞')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">∞</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('^2')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">x²</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('sin()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">sin</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('cos()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">cos</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('tan()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">tan</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('exp()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">exp</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('log()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">log</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('Min(,)', 2)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">Min</button>
        <button type="button" onmousedown="event.preventDefault(); insertSymbol('Max(,)', 2)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">Max</button>
    </div>
    
    <script>
    let lastActiveInputIndex = -1;
    let isTextArea = false;

    document.addEventListener('focusin', function(e) {
        if (e.target && e.target.tagName === 'INPUT') {
            let inputs = Array.from(document.querySelectorAll('input'));
            lastActiveInputIndex = inputs.indexOf(e.target);
            isTextArea = false;
        } else if (e.target && e.target.tagName === 'TEXTAREA') {
            let textareas = Array.from(document.querySelectorAll('textarea'));
            lastActiveInputIndex = textareas.indexOf(e.target);
            isTextArea = true;
        }
    });

    function insertSymbol(symbol, backOffset = 0) {
        if (lastActiveInputIndex === -1) {
            console.log("Kliknij na pole tekstowe przed dodaniem symbolu.");
            return;
        }
        try {
            let activeEl;
            if (isTextArea) {
                let textareas = Array.from(document.querySelectorAll('textarea'));
                activeEl = textareas[lastActiveInputIndex];
            } else {
                let inputs = Array.from(document.querySelectorAll('input'));
                activeEl = inputs[lastActiveInputIndex];
            }
            if (!activeEl) return;
            
            let start = activeEl.selectionStart;
            let end = activeEl.selectionEnd;
            let val = activeEl.value;
            activeEl.value = val.substring(0, start) + symbol + val.substring(end);
            
            let newPos = start + symbol.length - backOffset;
            activeEl.selectionStart = activeEl.selectionEnd = newPos;
            
            let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            if(activeEl.tagName === 'TEXTAREA') {
                nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            }
            nativeInputValueSetter.call(activeEl, activeEl.value);
            
            activeEl.dispatchEvent(new Event('input', { bubbles: true }));
            activeEl.dispatchEvent(new Event('change', { bubbles: true }));
            
            setTimeout(() => {
                activeEl.focus();
                activeEl.setSelectionRange(newPos, newPos);
            }, 50);
        } catch (e) {
            console.log("Błąd wklejania:", e);
        }
    }
    </script>
    """
    
    st.markdown(html_code, unsafe_allow_html=True)
