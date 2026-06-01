# Topological Visual Toolkit

Aplikacja Streamlit przygotowana na projekt z przedmiotu **Elementy topologii stosowanej**.
Zawiera sześć podprogramów:

1. skończone przestrzenie metryczne,
2. odległość supremum na przedziale,
3. odległość supremum na prostokącie,
4. aproksymację wielomianami Bernsteina,
5. przeciwobraz funkcji skalarnej,
6. obraz i przeciwobraz odwzorowania `R² -> R²`.

## Uruchomienie

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Jeżeli istniejący katalog `venv` wskazuje na nieistniejącego Pythona, usuń go i utwórz ponownie powyższymi komendami.

## Składnia wejścia

Parser przyjmuje zwykły zapis i prosty zapis LaTeX-like:

- `e^x`, `pi`, `\pi`,
- `sqrt(x)` i `\sqrt{x}`,
- `\frac{1}{2}`,
- `sin(x)`, `cos(x)`, `exp(x)`, `log(x)`,
- relacje zbiorów w `R²`, np. `x^2 + y^2 <= 1`,
- prostokąty, np. `[-1,1]x[-1,1]` albo `[-1,1]×[-1,1]`.

Historia poprawnych wejść jest dostępna bezpośrednio przy polach formularza.

## Metryka Minkowskiego

Dla `p >= 1` aplikacja używa wzoru

```text
d_p(x,y) = (sum_i |x_i-y_i|^p)^(1/p)
```

Dla `0 < p < 1` używana jest definicja z wykładu:

```text
d_p(x,y) = sum_i |x_i-y_i|^p
```
