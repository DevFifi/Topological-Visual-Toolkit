import streamlit as st

def render_math_keyboard():
    html_code = """
    <style>
    .mk-container { padding: 12px; font-family: 'Inter', sans-serif; background-color: #fcfcfc; border-radius: 8px; border: 1px solid #eaeaea; }
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
            <div class="mk-group-title">Zmienne i Operatory</div>
            <button type="button" class="mk-btn" title="x - Reprezentuje pierwszy wektor" onmousedown="handleBtnClick(event, 'x')">x</button>
            <button type="button" class="mk-btn" title="y - Reprezentuje drugi wektor" onmousedown="handleBtnClick(event, 'y')">y</button>
            <button type="button" class="mk-btn" title="xi - i-ta współrzędna wektora x (używane w SUM)" onmousedown="handleBtnClick(event, 'xi')">xi</button>
            <button type="button" class="mk-btn" title="yi - i-ta współrzędna wektora y (używane w SUM)" onmousedown="handleBtnClick(event, 'yi')">yi</button>
            <button type="button" class="mk-btn" title="Potęgowanie, np. x^2" onmousedown="handleBtnClick(event, '^')">^</button>
            <button type="button" class="mk-btn" title="Nawiasy, np. (x+y)" onmousedown="handleBtnClick(event, '()', 1)">( )</button>
            <button type="button" class="mk-btn" title="Nieskończoność (oznaczenie analityczne)" onmousedown="handleBtnClick(event, 'oo')">∞</button>
            <button type="button" class="mk-btn" title="Liczba Pi (~3.1415)" onmousedown="handleBtnClick(event, 'pi')">π</button>
        </div>

        <div class="mk-group">
            <div class="mk-group-title">Funkcje i Operacje</div>
            <button type="button" class="mk-btn" title="SUM(wyrażenie) - Sumuje wyrażenie po wszystkich wymiarach od i=1 do n. Przykład: SUM((xi-yi)^2)" onmousedown="handleBtnClick(event, 'SUM()', 1)">∑</button>
            <button type="button" class="mk-btn" title="Wartość bezwzględna. Alternatywa dla Abs(). Przykład: |x1 - y1|" onmousedown="handleBtnClick(event, '||', 1)">| |</button>
            <button type="button" class="mk-btn" title="Abs(wyrażenie) - Wartość bezwzględna wyrażenia." onmousedown="handleBtnClick(event, 'Abs()', 1)">Abs</button>
            <button type="button" class="mk-btn" title="sqrt(wyrażenie) - Pierwiastek kwadratowy" onmousedown="handleBtnClick(event, 'sqrt()', 1)">√</button>
            <button type="button" class="mk-btn" title="root(wyrażenie, n) - Pierwiastek n-tego stopnia z wyrażenia. Przykład: root(x, 3)" onmousedown="handleBtnClick(event, 'root(,)', 2)">root</button>
            <button type="button" class="mk-btn" title="Min(a, b) - Wybiera mniejszą z dwóch wartości" onmousedown="handleBtnClick(event, 'Min(,)', 2)">Min</button>
            <button type="button" class="mk-btn" title="Max(a, b) - Wybiera większą z dwóch wartości" onmousedown="handleBtnClick(event, 'Max(,)', 2)">Max</button>
            <button type="button" class="mk-btn" title="sin(x) - Sinus (kąt w radianach)" onmousedown="handleBtnClick(event, 'sin()', 1)">sin</button>
            <button type="button" class="mk-btn" title="cos(x) - Cosinus (kąt w radianach)" onmousedown="handleBtnClick(event, 'cos()', 1)">cos</button>
            <button type="button" class="mk-btn" title="exp(x) - Funkcja wykładnicza e^x" onmousedown="handleBtnClick(event, 'exp()', 1)">exp</button>
        </div>

        <div class="mk-group">
            <div class="mk-group-title">Litery Greckie</div>
            <button type="button" class="mk-btn" title="Alfa" onmousedown="handleBtnClick(event, 'α')">α</button>
            <button type="button" class="mk-btn" title="Beta" onmousedown="handleBtnClick(event, 'β')">β</button>
            <button type="button" class="mk-btn" title="Gamma" onmousedown="handleBtnClick(event, 'γ')">γ</button>
            <button type="button" class="mk-btn" title="Delta" onmousedown="handleBtnClick(event, 'δ')">δ</button>
            <button type="button" class="mk-btn" title="Epsilon" onmousedown="handleBtnClick(event, 'ε')">ε</button>
            <button type="button" class="mk-btn" title="Theta" onmousedown="handleBtnClick(event, 'θ')">θ</button>
            <button type="button" class="mk-btn" title="Lambda" onmousedown="handleBtnClick(event, 'λ')">λ</button>
            <button type="button" class="mk-btn" title="Mi" onmousedown="handleBtnClick(event, 'μ')">μ</button>
            <button type="button" class="mk-btn" title="Omega" onmousedown="handleBtnClick(event, 'ω')">ω</button>
        </div>
        
    </div>
    
    <script>
    let lastActiveInput = null;

    // Przechwytujemy zdarzenia na etapie capture (true), by wyłapać element 
    // ZANIM Streamlit/React zrobi cokolwiek
    function trackInput(e) {
        if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) {
            lastActiveInput = e.target;
        }
    }
    
    window.addEventListener('mousedown', trackInput, true);
    window.addEventListener('focusin', trackInput, true);
    window.addEventListener('click', trackInput, true);

    function handleBtnClick(event, symbol, backOffset = 0) {
        // Zatrzymujemy bąbelkowanie! To powstrzymuje React'a przez odznaczeniem pola!
        event.preventDefault();
        event.stopPropagation();
        
        if (!lastActiveInput) {
            console.log("Kliknij najpierw na pole tekstowe.");
            return;
        }
        
        try {
            let activeEl = lastActiveInput;
            let start = activeEl.selectionStart || 0;
            let end = activeEl.selectionEnd || 0;
            let val = activeEl.value || "";
            
            let newVal = val.substring(0, start) + symbol + val.substring(end);
            let newPos = start + symbol.length - backOffset;
            
            let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            if(activeEl.tagName === 'TEXTAREA') {
                nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            }
            nativeInputValueSetter.call(activeEl, newVal);
            
            // Rejestracja zmiany w React
            activeEl.dispatchEvent(new Event('input', { bubbles: true }));
            activeEl.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Fokusowanie wewnątrz setTimeout, aby upewnić się, że cykl Reacta się zakończył
            setTimeout(() => {
                activeEl.focus();
                activeEl.setSelectionRange(newPos, newPos);
            }, 10);
            
        } catch (e) {
            console.log("Błąd wklejania:", e);
        }
    }
    </script>
    """
    
    st.markdown(html_code, unsafe_allow_html=True)
