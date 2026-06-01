import sympy

from core.exact_numeric import DualValue
from core.formatting import format_point, latex_exact, latex_point, simplify_exact
from ui import components


def test_latex_exact_and_point_use_small_euler_symbol():
    assert latex_exact(sympy.E) == "e"
    assert format_point((sympy.E, sympy.sqrt(2))) == "(e, sqrt(2))"
    assert latex_point((sympy.E, sympy.sqrt(2))) == r"\left(e, \sqrt{2}\right)"


def test_matrix_cell_markdown_prefers_latex_exact_value():
    value = sympy.E + sympy.sqrt(2)
    dv = DualValue(
        exact=str(value),
        exact_latex=latex_exact(value),
        numeric="4.132",
        status="exact_and_numeric",
    )
    cell = components._matrix_cell_markdown(dv)
    assert cell.startswith("$")
    assert r"\sqrt{2}" in cell
    assert "e" in cell
    assert "E" not in cell
    assert "\u2248 4.132" in cell


def test_distance_matrix_renderer_outputs_markdown_with_latex_headers(monkeypatch):
    captured = {}

    def fake_markdown(body, unsafe_allow_html=False):
        captured["body"] = body
        captured["unsafe_allow_html"] = unsafe_allow_html

    monkeypatch.setattr(components.st, "markdown", fake_markdown)
    matrix = [[DualValue(exact="0", exact_latex="0", numeric="0.0", status="exact_and_numeric")]]

    components.render_distance_matrix_html(
        ["(e)"],
        matrix,
        headers_latex=[r"\left(e\right)"],
    )

    assert captured["unsafe_allow_html"] is True
    assert r"$\left(e\right)$" in captured["body"]
    assert "$0$" in captured["body"]


def test_simplify_exact_expands_redundant_squared_terms_for_display():
    expr = sympy.sqrt((1 - sympy.sqrt(2)) ** 2 + (1 - sympy.E) ** 2)
    simplified = simplify_exact(expr)
    assert sympy.simplify(simplified - expr) == 0
    assert "(1 - sqrt(2))**2" not in sympy.sstr(simplified)
    assert "(1 - E)**2" not in sympy.sstr(simplified)
    rendered = latex_exact(expr)
    assert r"e^{2}" in rendered
    assert r"\sqrt{2}" in rendered
    assert "(1" not in rendered
