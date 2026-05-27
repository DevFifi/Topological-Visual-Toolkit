import streamlit as st

def render() -> None:
    st.header("Dokumentacja")
    
    st.markdown("""
    ### O projekcie
    Topological Visual Toolkit to wszechstronna aplikacja matematyczna służąca do wizualizacji i obliczeń z zakresu topologii i analizy.
    
    ### Zastosowana Filozofia
    - **Dokładność tam, gdzie to możliwe**: Aplikacja stara się najpierw obliczyć wyniki w sposób analityczny/symboliczny (używając biblioteki SymPy).
    - **Aproksymacja z informacją**: Gdy dokładne obliczenie nie jest możliwe, aplikacja ucieka się do metod numerycznych i jasno o tym informuje użytkownika.
    - **Pamięć trwała**: Każde poprawne wejście można zapisać do historii JSON, aby łatwo użyć go ponownie.
    
    ### Obsługiwane Wzory (Parser)
    Dozwolone są:
    - Zmienne: `x`, `y`, `u`, `v`, `x1`, `y1`...
    - Funkcje: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `Abs`, `Min`, `Max`
    - Stałe: `pi`, `E`
    
    ### Zbiory
    - 1D: `[a, b]`, `(a, b)`, `{1, 2, 3}`
    - 2D: `[a, b]x[c, d]`, `x^2 + y^2 <= 1`
    
    ### Moduły
    1. **Przestrzenie Metryczne**: Oblicza macierze odległości i średnice zbiorów. Ograniczenia: własne metryki nie są w pełni udowadniane z aksjomatów.
    2. **Supremum na Przedziale**: Szuka maksimum z |f-g|. Wykorzystuje pochodne i sampling.
    3. **Supremum na Prostokącie**: Szuka maksimum z |f-g|. Złożoność jest tu ogromna, polegamy na metodach numerycznych (siatka).
    4. **Aproksymacja Bernsteina**: Interpolacja wielomianami, stabilna numerycznie.
    5. **Przeciwobraz Skalarny**: Wizualizuje $f^{-1}(A)$.
    6. **Odwzorowania Wektorowe**: Wizualizuje deformacje płaszczyzny.
    """)
