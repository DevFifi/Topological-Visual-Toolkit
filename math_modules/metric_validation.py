from typing import Any, Tuple

import numpy as np

from math_modules.finite_metric_spaces import compute_distance


def validate_metric_heuristically(formula: Any, metric_name: str, dim: int) -> Tuple[bool, str]:
    if formula is None:
        return False, "Nie udało się zbudować wzoru metryki."

    rng = np.random.default_rng(42)
    try:
        def d(p1, p2):
            dv = compute_distance(p1, p2, formula, metric_name)
            if not dv.numeric:
                raise ValueError("Brak wyniku numerycznego")
            return float(dv.numeric)

        for _ in range(80):
            x = tuple(rng.uniform(-10, 10, dim))
            y = tuple(rng.uniform(-10, 10, dim))
            z = tuple(rng.uniform(-10, 10, dim))

            dxx = d(x, x)
            if abs(dxx) > 1e-6:
                return False, f"Naruszenie identyczności: d(x,x) = {dxx:.5f}, a powinno być 0."

            dxy = d(x, y)
            if dxy < -1e-6:
                return False, f"Naruszenie dodatniości: d(x,y) = {dxy:.5f} < 0."

            dyx = d(y, x)
            if abs(dxy - dyx) > 1e-6:
                return False, f"Naruszenie symetrii: d(x,y) = {dxy:.5f}, d(y,x) = {dyx:.5f}."

            dyz = d(y, z)
            dxz = d(x, z)
            if dxz > dxy + dyz + 1e-5:
                return False, (
                    f"Naruszenie nierówności trójkąta: d(x,z) = {dxz:.5f} > "
                    f"d(x,y) + d(y,z) = {dxy:.5f} + {dyz:.5f}."
                )

        return True, "Wzór przeszedł heurystyczny test aksjomatów metryki na losowych punktach. To nie jest formalny dowód."

    except Exception as e:
        return False, f"Błąd w ocenie funkcji jako metryki: {str(e)}"
