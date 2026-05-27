import streamlit as st

def render_math_keyboard():
    html_code = """
    <div id="math-keyboard" style="padding: 5px; font-family: sans-serif; background-color: #fbfbfb; border-radius: 8px; border: 1px solid #ddd; display: flex; flex-wrap: wrap;">
        <button onmousedown="event.preventDefault(); insertSymbol('π')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">π</button>
        <button onmousedown="event.preventDefault(); insertSymbol('e')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">e</button>
        <button onmousedown="event.preventDefault(); insertSymbol('√()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">√</button>
        <button onmousedown="event.preventDefault(); insertSymbol('^')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">^</button>
        <button onmousedown="event.preventDefault(); insertSymbol('SUM()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">∑</button>
        <button onmousedown="event.preventDefault(); insertSymbol('Abs()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">|x|</button>
        <button onmousedown="event.preventDefault(); insertSymbol('∞')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">∞</button>
        <button onmousedown="event.preventDefault(); insertSymbol('^2')" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">x²</button>
        <button onmousedown="event.preventDefault(); insertSymbol('sin()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">sin</button>
        <button onmousedown="event.preventDefault(); insertSymbol('cos()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">cos</button>
        <button onmousedown="event.preventDefault(); insertSymbol('tan()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">tan</button>
        <button onmousedown="event.preventDefault(); insertSymbol('exp()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">exp</button>
        <button onmousedown="event.preventDefault(); insertSymbol('log()', 1)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">log</button>
        <button onmousedown="event.preventDefault(); insertSymbol('Min(,)', 2)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">Min</button>
        <button onmousedown="event.preventDefault(); insertSymbol('Max(,)', 2)" style="font-size: 14px; padding: 4px 8px; margin: 2px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: white;">Max</button>
    </div>
    
    <script>
    function insertSymbol(symbol, backOffset = 0) {
        try {
            // Skrypt działa bezpośrednio w środowisku Streamlit jako st.markdown
            let activeEl = document.activeElement;
            
            if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) {
                let start = activeEl.selectionStart;
                let end = activeEl.selectionEnd;
                let val = activeEl.value;
                activeEl.value = val.substring(0, start) + symbol + val.substring(end);
                
                // Przestawienie kursora (np. w środek nawiasu)
                let newPos = start + symbol.length - backOffset;
                activeEl.selectionStart = activeEl.selectionEnd = newPos;
                
                // React tracker hook - wymagany by React w Streamlit zarejestrował zmianę z JS
                let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                if(activeEl.tagName === 'TEXTAREA') {
                    nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                }
                nativeInputValueSetter.call(activeEl, activeEl.value);
                
                let event = new Event('input', { bubbles: true });
                activeEl.dispatchEvent(event);
            } else {
                console.log("Kliknij na pole tekstowe przed dodaniem symbolu.");
            }
        } catch (e) {
            console.log("Błąd wklejania:", e);
        }
    }
    </script>
    """
    
    st.markdown(html_code, unsafe_allow_html=True)
