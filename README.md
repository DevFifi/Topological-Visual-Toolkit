# Topological Visual Toolkit

Aplikacja Streamlit przygotowana jako projekt z przedmiotu **Elementy topologii stosowanej**.

- Działająca aplikacja: <https://topological-visual-toolkit.streamlit.app>
- Dokumentacja projektu: [`docs/dokumentacja.pdf`](docs/dokumentacja.pdf)
- Źródło LaTeX dokumentacji: [`docs/dokumentacja.tex`](docs/dokumentacja.tex)

## Zakres projektu

Aplikacja zawiera sześć modułów:

1. **Skończone przestrzenie metryczne** - macierze odległości, średnica zbioru i odległość między zbiorami w `R^n`.
2. **Odległość supremum na przedziale** - przybliżone i częściowo symboliczne liczenie `d∞(f,g)` dla funkcji jednej zmiennej.
3. **Odległość supremum na prostokącie** - numeryczne liczenie `d∞(f,g)` dla funkcji dwóch zmiennych na prostokącie.
4. **Aproksymacja Bernsteina** - wykresy, błąd Czebyszewa i animacja wielomianów Bernsteina.
5. **Przeciwobraz funkcji skalarnej** - sprawdzanie przynależności punktu do `f^{-1}(A)` i rysowanie przeciwobrazu.
6. **Odwzorowania wektorowe** - przybliżone rysowanie obrazu `Φ(C)` i przeciwobrazu `Φ^{-1}(B)`.

## Najważniejsze funkcje

- wejścia matematyczne w zwykłym zapisie i w prostym stylu LaTeX,
- podgląd rozpoznanych wzorów w postaci matematycznej,
- klawiatura matematyczna w panelu bocznym,
- lokalna historia przykładów osobna dla modułów,
- dokładne wartości tam, gdzie SymPy potrafi je sensownie uprościć,
- numeryczne metody dla supremów, dużych zbiorów punktów oraz rysowania zbiorów,
- interaktywne wykresy Plotly.

## Zastosowane techniki

- parser wyrażeń oparty o SymPy z własną normalizacją zapisu LaTeX-like,
- parser zbiorów obsługujący przedziały, zbiory skończone, prostokąty, relacje i operacje `\cap`, `\cup`, `\land`, `\lor`,
- wspólny format wyniku z częścią dokładną, numeryczną, opisem metody i uwagami o dokładności,
- lokalne doszukiwanie maksimów na siatce przez SciPy,
- osobne sprawdzanie brzegów i narożników przy supremum na prostokącie,
- blokowe liczenie odległości dla dużych zbiorów punktów,
- stabilna numeryczna ewaluacja wielomianów Bernsteina dla dużych stopni,
- rysowanie obszarów i brzegów przez siatki, maski logiczne i kontury Plotly.

## Przykłady składni wejścia

Funkcje:

```text
e^x
\sqrt{x}
\frac{1+x}{2}
sin(50*x)
x^2 + y^2
```

Zbiory w `R`:

```text
[0, 1]
(0, 1]
(-oo, 0)
{0, 1, pi}
[0,1] \cup {2}
```

Zbiory w `R^2`:

```text
[-1,1]x[-2,2]
[-1,1]\times[-2,2]
x^2 + y^2 <= 1
1/4 < x^2 + y^2 <= 1
(x^2+y^2-1)^3 - x^2*y^3 < 0
```

Warunki można łączyć m.in. przez `\cap`, `\cup`, `\land`, `\lor`, `and`, `or`.

## Uruchomienie lokalne

Wymagany jest Python zainstalowany lokalnie. Przykładowe uruchomienie w PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Jeżeli katalog `venv` został utworzony wcześniej dla innej lub nieistniejącej instalacji Pythona, najprościej utworzyć nowe środowisko wirtualne i ponownie zainstalować zależności z `requirements.txt`.

## Testy

Testy jednostkowe znajdują się w katalogu [`tests`](tests). Można je uruchomić poleceniem:

```powershell
pytest -q
```

## Dokumentacja

Pełny opis rozwiązania jest w pliku [`docs/dokumentacja.pdf`](docs/dokumentacja.pdf). Dokumentacja opisuje założenia, użyte metody numeryczne, obsługiwaną składnię wejścia oraz przykładowe wyniki działania każdego modułu.
